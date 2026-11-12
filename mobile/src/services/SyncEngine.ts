// Mobile Offline Sync Engine (TNX-SYNC-001)
import { SQL_INIT_LOCAL_DB } from '../database/schema';

export interface SyncOperationItem {
  operation_id: string;
  operation_type: 'create' | 'update' | 'delete';
  entity_name: string;
  entity_id: string;
  client_timestamp: string;
  payload: Record<string, any>;
  attempt_count?: number;
}

export interface ISQLiteDatabase {
  execAsync?(sql: string): Promise<any>;
  runAsync?(sql: string, params?: any[]): Promise<any>;
  getAllAsync?<T>(sql: string, params?: any[]): Promise<T[]>;
}

export class MobileSyncEngine {
  private apiBaseUrl: string;
  private clientUUID: string;
  private authToken: string | null;
  private outboxQueue: SyncOperationItem[];
  private db: ISQLiteDatabase | null;

  constructor(
    apiBaseUrl = 'http://10.0.2.2:8000/api/v1',
    clientUUID = 'mobile-device-001',
    authToken: string | null = null,
    db: ISQLiteDatabase | null = null
  ) {
    this.apiBaseUrl = apiBaseUrl;
    this.clientUUID = clientUUID;
    this.authToken = authToken;
    this.outboxQueue = [];
    this.db = db;
  }

  setAuthToken(token: string | null) {
    this.authToken = token;
  }

  setDatabase(db: ISQLiteDatabase | null) {
    this.db = db;
  }

  /**
   * Initializes local schema and restores persisted outbox from SQLite.
   */
  async initialize(): Promise<void> {
    if (this.db) {
      if (this.db.execAsync) {
        await this.db.execAsync(SQL_INIT_LOCAL_DB);
      }
      await this.loadOutboxFromDatabase();
    }
  }

  /**
   * Restores uncommitted outbox queue from SQLite `sync_queue` table.
   */
  async loadOutboxFromDatabase(): Promise<void> {
    if (!this.db || !this.db.getAllAsync) return;
    try {
      const rows = await this.db.getAllAsync<{
        id: string;
        operation_type: 'create' | 'update' | 'delete';
        entity_name: string;
        entity_id: string;
        payload: string;
        created_at: string;
        attempt_count: number;
      }>('SELECT id, operation_type, entity_name, entity_id, payload, created_at, attempt_count FROM sync_queue ORDER BY created_at ASC');

      this.outboxQueue = rows.map((r) => ({
        operation_id: r.id,
        operation_type: r.operation_type,
        entity_name: r.entity_name,
        entity_id: r.entity_id,
        client_timestamp: r.created_at,
        payload: JSON.parse(r.payload),
        attempt_count: r.attempt_count,
      }));
    } catch (e) {
      console.warn('Could not restore outbox from SQLite:', e);
    }
  }

  /**
   * Enqueues an operation into durable SQLite storage and in-memory queue.
   */
  async enqueueOperation(op: SyncOperationItem): Promise<void> {
    const item: SyncOperationItem = {
      ...op,
      attempt_count: op.attempt_count || 0,
    };
    this.outboxQueue.push(item);

    if (this.db && this.db.runAsync) {
      try {
        await this.db.runAsync(
          `INSERT OR REPLACE INTO sync_queue (id, operation_type, entity_name, entity_id, payload, created_at, attempt_count)
           VALUES (?, ?, ?, ?, ?, ?, ?)`,
          [
            item.operation_id,
            item.operation_type,
            item.entity_name,
            item.entity_id,
            JSON.stringify(item.payload),
            item.client_timestamp,
            item.attempt_count,
          ]
        );
      } catch (err) {
        // Rollback in-memory state on persistence failure and throw
        this.outboxQueue = this.outboxQueue.filter((o) => o.operation_id !== item.operation_id);
        console.error('Failed to persist sync operation to durable SQLite storage:', err);
        throw err;
      }
    }
  }

  getOutboxQueue(): SyncOperationItem[] {
    return [...this.outboxQueue];
  }

  async clearOutboxQueue(): Promise<void> {
    this.outboxQueue = [];
    if (this.db && this.db.runAsync) {
      try {
        await this.db.runAsync('DELETE FROM sync_queue');
      } catch (e) {
        console.warn('Failed to clear sync_queue table from SQLite:', e);
      }
    }
  }

  async getPersistedCursor(): Promise<number> {
    if (this.db && this.db.getAllAsync) {
      try {
        const rows = await this.db.getAllAsync<{ key: string; value: string }>(
          "SELECT value FROM sync_meta WHERE key = 'sync_cursor'"
        );
        if (rows.length > 0) {
          return parseInt(rows[0].value, 10) || 0;
        }
      } catch (_) {}
    }
    return 0;
  }

  private getRequestHeaders(): Record<string, string> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };
    if (this.authToken) {
      headers['Authorization'] = `Bearer ${this.authToken}`;
    }
    return headers;
  }

  async pushOfflineChanges(operations: SyncOperationItem[] = this.outboxQueue) {
    if (operations.length === 0) return { applied: 0, conflicts: 0, deduplicated: 0 };

    try {
      const response = await fetch(`${this.apiBaseUrl}/sync/push`, {
        method: 'POST',
        headers: this.getRequestHeaders(),
        body: JSON.stringify({
          client_uuid: this.clientUUID,
          app_version: '1.0.0',
          operations: operations,
        }),
      });

      if (!response.ok) {
        throw new Error(`Sync push failed with status ${response.status}`);
      }

      const result = await response.json();
      
      // Inspect detailed per-operation results: only prune applied and deduplicated operations.
      // Conflicted and rejected mutations are preserved in durable SQLite outbox for manual/user resolution.
      const settledIds = new Set<string>();
      if (Array.isArray(result.results)) {
        for (const res of result.results) {
          if (res.status === 'applied' || res.status === 'deduplicated') {
            settledIds.add(res.operation_id);
          }
        }
      } else {
        // Fallback for backwards compatibility if results array is absent
        operations.forEach((o) => settledIds.add(o.operation_id));
      }

      this.outboxQueue = this.outboxQueue.filter((o) => !settledIds.has(o.operation_id));

      if (this.db && this.db.runAsync) {
        for (const id of settledIds) {
          try {
            await this.db.runAsync('DELETE FROM sync_queue WHERE id = ?', [id]);
          } catch (e) {
            console.warn(`Failed to delete settled operation ${id} from SQLite:`, e);
          }
        }
      }

      return result;
    } catch (err) {
      console.warn('Sync push network error, retaining operations in durable outbox:', err);
      // Increment attempt count for retained operations
      for (const op of operations) {
        op.attempt_count = (op.attempt_count || 0) + 1;
        if (this.db && this.db.runAsync) {
          try {
            await this.db.runAsync('UPDATE sync_queue SET attempt_count = ? WHERE id = ?', [
              op.attempt_count,
              op.operation_id,
            ]);
          } catch (_) {}
        }
      }
      return { status: 'offline_buffered', queue_depth: this.outboxQueue.length, error: String(err) };
    }
  }

  async pullServerChanges(sinceCursor = 0) {
    try {
      const response = await fetch(`${this.apiBaseUrl}/sync/pull`, {
        method: 'POST',
        headers: this.getRequestHeaders(),
        body: JSON.stringify({
          client_uuid: this.clientUUID,
          since_cursor: sinceCursor,
        }),
      });

      if (!response.ok) {
        throw new Error(`Sync pull failed with status ${response.status}`);
      }

      const result = await response.json();

      if (this.db && this.db.runAsync && Array.isArray(result.changes)) {
        for (const change of result.changes) {
          if (change.entity_name === 'task' && change.payload) {
            const p = change.payload;
            try {
              await this.db.runAsync(
                `INSERT OR REPLACE INTO local_tasks (id, farm_id, field_id, title, description, task_type, priority, status, due_date, updated_at, sync_status)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'synced')`,
                [
                  p.id,
                  p.farm_id || 'default-farm',
                  p.field_id || null,
                  p.title || 'Untitled Task',
                  p.description || '',
                  p.task_type || 'general',
                  p.priority || 'medium',
                  p.status || 'pending',
                  p.due_date || null,
                  p.updated_at || new Date().toISOString()
                ]
              );
            } catch (err) {
              console.warn('Failed to insert pulled task into SQLite:', err);
            }
          } else if (change.entity_name === 'field_observation' && change.payload) {
            const p = change.payload;
            try {
              await this.db.runAsync(
                `INSERT OR REPLACE INTO local_field_observations (id, field_id, observation_type, description, severity, latitude, longitude, observed_at, sync_status)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'synced')`,
                [
                  p.id,
                  p.field_id || 'default-field',
                  p.observation_type || 'scouting',
                  p.description || '',
                  p.severity || 'medium',
                  p.latitude || null,
                  p.longitude || null,
                  p.created_at || new Date().toISOString()
                ]
              );
            } catch (err) {
              console.warn('Failed to insert pulled field observation into SQLite:', err);
            }
          }
        }
        if (result.new_sync_cursor !== undefined) {
          try {
            await this.db.runAsync(
              `INSERT OR REPLACE INTO sync_meta (key, value) VALUES ('sync_cursor', ?)`,
              [String(result.new_sync_cursor)]
            );
          } catch (err) {
            console.warn('Failed to update sync_cursor in SQLite sync_meta:', err);
          }
        }
      }

      return result;
    } catch (err) {
      console.warn('Sync pull network error:', err);
      return { status: 'offline', changes: [] };
    }
  }
}
