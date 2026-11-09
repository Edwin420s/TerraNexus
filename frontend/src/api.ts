// TerraNexus API Client
const API_BASE = 'http://localhost:8000/api/v1';

export async function fetchWithAuth(endpoint: string, options: RequestInit = {}) {
  const token = localStorage.getItem('tnx_token');
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  try {
    const res = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Request failed' }));
      throw new Error(err.detail || `HTTP ${res.status}`);
    }
    return await res.json();
  } catch (error) {
    console.error(`API Error on ${endpoint}:`, error);
    throw error;
  }
}

export const api = {
  // Auth
  login: (email: string, password: string) =>
    fetchWithAuth('/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) }),
  getMe: () => fetchWithAuth('/auth/me'),

  // Farms & Fields
  getFarms: () => fetchWithAuth('/farms'),
  createFarm: (data: any) => fetchWithAuth('/farms', { method: 'POST', body: JSON.stringify(data) }),
  getFields: (farmId?: string) => fetchWithAuth(`/fields${farmId ? `?farm_id=${farmId}` : ''}`),
  createField: (data: any) => fetchWithAuth('/fields', { method: 'POST', body: JSON.stringify(data) }),

  // Agriculture
  getCrops: () => fetchWithAuth('/crops'),
  getSeasons: () => fetchWithAuth('/seasons'),

  // Devices & Telemetry
  getDevices: () => fetchWithAuth('/devices'),
  getSensors: () => fetchWithAuth('/sensors'),
  getMeasurements: (params?: string) => fetchWithAuth(`/measurements${params ? `?${params}` : ''}`),
  dispatchCommand: (deviceId: string, data: any) =>
    fetchWithAuth(`/devices/${deviceId}/commands`, { method: 'POST', body: JSON.stringify(data) }),

  // Irrigation & Safe Actuation
  getIrrigationSources: () => fetchWithAuth('/irrigation/sources'),
  getIrrigationZones: () => fetchWithAuth('/irrigation/zones'),
  startIrrigation: (zoneId: string, durationMinutes: number) =>
    fetchWithAuth('/irrigation/control/start', {
      method: 'POST',
      body: JSON.stringify({ zone_id: zoneId, duration_minutes: durationMinutes }),
    }),
  stopIrrigation: (zoneId: string, reason?: string) =>
    fetchWithAuth('/irrigation/control/stop', {
      method: 'POST',
      body: JSON.stringify({ zone_id: zoneId, reason: reason || 'manual_stop' }),
    }),
  getIrrigationHistory: () => fetchWithAuth('/irrigation/history'),

  // Operations
  getTasks: () => fetchWithAuth('/tasks'),
  createTask: (data: any) => fetchWithAuth('/tasks', { method: 'POST', body: JSON.stringify(data) }),
  updateTask: (taskId: string, data: any) =>
    fetchWithAuth(`/tasks/${taskId}`, { method: 'PATCH', body: JSON.stringify(data) }),
  getEquipment: () => fetchWithAuth('/equipment'),
  getInventory: () => fetchWithAuth('/inventory'),
  getHarvest: () => fetchWithAuth('/harvest'),

  // Alerts & Notifications
  getAlerts: () => fetchWithAuth('/alerts'),
  acknowledgeAlert: (alertId: string) => fetchWithAuth(`/alerts/${alertId}/ack`, { method: 'POST' }),
  resolveAlert: (alertId: string) => fetchWithAuth(`/alerts/${alertId}/resolve`, { method: 'POST' }),
  getNotifications: () => fetchWithAuth('/notifications'),

  // Intelligence & Local AI
  getRecommendations: () => fetchWithAuth('/intelligence/recommendations'),
  acceptRecommendation: (id: string) => fetchWithAuth(`/intelligence/recommendations/${id}/accept`, { method: 'POST' }),
  rejectRecommendation: (id: string) => fetchWithAuth(`/intelligence/recommendations/${id}/reject`, { method: 'POST' }),
  getWeather: () => fetchWithAuth('/intelligence/weather'),
  runLocalReasoning: (prompt: string) =>
    fetchWithAuth('/intelligence/local-reasoning', { method: 'POST', body: JSON.stringify({ prompt }) }),

  // QVAC Private Documents (Local RAG)
  getDocuments: (farmId?: string, category?: string) => {
    const params = new URLSearchParams();
    if (farmId) params.append('farm_id', farmId);
    if (category) params.append('category', category);
    const qs = params.toString();
    return fetchWithAuth(`/intelligence/documents${qs ? `?${qs}` : ''}`);
  },
  indexDocument: (data: { title: string; category?: string; content_text: string; farm_id?: string }) =>
    fetchWithAuth('/intelligence/documents/index', { method: 'POST', body: JSON.stringify(data) }),
  queryDocuments: (query: string, farmId?: string, topK: number = 3) =>
    fetchWithAuth('/intelligence/documents/query', { method: 'POST', body: JSON.stringify({ query, farm_id: farmId, top_k: topK }) }),
  chatDocuments: (prompt: string, farmId?: string) =>
    fetchWithAuth('/intelligence/chat-documents', { method: 'POST', body: JSON.stringify({ prompt, farm_id: farmId }) }),

  // QVAC Speech AI (Whisper ASR & TTS)
  transcribeSpeech: (data: { audio_base64?: string; filename?: string }) =>
    fetchWithAuth('/intelligence/speech/transcribe', { method: 'POST', body: JSON.stringify(data) }),
  synthesizeSpeech: (text: string, voice: string = 'agronomist_female') =>
    fetchWithAuth('/intelligence/speech/synthesize', { method: 'POST', body: JSON.stringify({ text, voice }) }),
  voiceAssistant: (data: { audio_base64?: string; transcript_override?: string; voice?: string }) =>
    fetchWithAuth('/intelligence/voice-assistant', { method: 'POST', body: JSON.stringify(data) }),

  // Tether WDK Agentic Finance (USD₮ Self-Custodial Vault & Human Gates)
  getFinanceWallet: () => fetchWithAuth('/finance/wallet'),
  getFinancePayments: (farmId?: string, statusFilter?: string) => {
    const params = new URLSearchParams();
    if (farmId) params.append('farm_id', farmId);
    if (statusFilter) params.append('status_filter', statusFilter);
    const qs = params.toString();
    return fetchWithAuth(`/finance/payments${qs ? `?${qs}` : ''}`);
  },
  prepareFinancePayment: (data: {
    purpose: string;
    amount_usdt: number;
    recipient_address: string;
    description?: string;
    agent_reasoning?: string;
    chain?: string;
    farm_id?: string;
  }) => fetchWithAuth('/finance/payments/prepare', { method: 'POST', body: JSON.stringify(data) }),
  approveFinancePayment: (paymentId: string) =>
    fetchWithAuth(`/finance/payments/${paymentId}/approve`, { method: 'POST' }),
  rejectFinancePayment: (paymentId: string, reason?: string) =>
    fetchWithAuth(`/finance/payments/${paymentId}/reject`, { method: 'POST', body: JSON.stringify({ reason: reason || 'Operator declined' }) }),

  // Admin & System
  getSystemStatus: () => fetchWithAuth('/admin/system-status'),
  getAuditLogs: () => fetchWithAuth('/admin/audit'),
};
