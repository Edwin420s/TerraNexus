// Mobile Offline Sync Engine (TNX-SYNC-001)
export interface SyncOperationItem {
  operation_id: string;
  operation_type: 'create' | 'update' | 'delete';
  entity_name: string;
  entity_id: string;
  client_timestamp: string;
  payload: Record<string, any>;
}

export class MobileSyncEngine {
  private apiBaseUrl: string;
  private clientUUID: string;

  constructor(apiBaseUrl = 'http://10.0.2.2:8000/api/v1', clientUUID = 'mobile-device-001') {
    this.apiBaseUrl = apiBaseUrl;
    this.clientUUID = clientUUID;
  }

  async pushOfflineChanges(operations: SyncOperationItem[]) {
    if (operations.length === 0) return { applied: 0, conflicts: 0 };

    try {
      const response = await fetch(`${this.apiBaseUrl}/sync/push`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
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
      return result;
    } catch (err) {
      console.warn('Sync push network error:', err);
      return { status: 'offline_buffered', error: String(err) };
    }
  }

  async pullServerChanges(sinceCursor = 0) {
    try {
      const response = await fetch(`${this.apiBaseUrl}/sync/pull`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
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
