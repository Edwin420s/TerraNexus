// Mobile Offline Sync Engine (TNX-SYNC-001)
export interface SyncOperationItem {
  operation_id: string;
  operation_type: 'create' | 'update' | 'delete';
  entity_name: string;
  entity_id: string;
  client_timestamp: string;
  payload: Record<string, any>;
  attempt_count?: number;
}

export class MobileSyncEngine {
  private apiBaseUrl: string;
  private clientUUID: string;
  private authToken: string | null;
  private outboxQueue: SyncOperationItem[];

  constructor(
    apiBaseUrl = 'http://10.0.2.2:8000/api/v1',
    clientUUID = 'mobile-device-001',
    authToken: string | null = null
  ) {
    this.apiBaseUrl = apiBaseUrl;
    this.clientUUID = clientUUID;
    this.authToken = authToken;
    this.outboxQueue = [];
  }

  setAuthToken(token: string | null) {
    this.authToken = token;
  }

  /**
   * Enqueues an operation into the durable outbox buffer.
   */
  enqueueOperation(op: SyncOperationItem) {
    this.outboxQueue.push({
      ...op,
      attempt_count: op.attempt_count || 0,
    });
  }

  getOutboxQueue(): SyncOperationItem[] {
    return [...this.outboxQueue];
  }

  clearOutboxQueue() {
    this.outboxQueue = [];
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
      // On successful push, remove acknowledged operations from outbox
      const pushedIds = new Set(operations.map((o) => o.operation_id));
      this.outboxQueue = this.outboxQueue.filter((o) => !pushedIds.has(o.operation_id));
      return result;
    } catch (err) {
      console.warn('Sync push network error, retaining operations in outbox buffer:', err);
      // Increment attempt count for retained operations
      for (const op of operations) {
        op.attempt_count = (op.attempt_count || 0) + 1;
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
      return result;
    } catch (err) {
      console.warn('Sync pull network error:', err);
      return { status: 'offline', changes: [] };
    }
  }
}
