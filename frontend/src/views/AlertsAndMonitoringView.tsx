import React, { useEffect, useState } from 'react';
import { api } from '../api';
import { AlertTriangle, CheckCircle, Bell, Shield, ArrowRight } from 'lucide-react';

export const AlertsAndMonitoringView: React.FC = () => {
  const [alerts, setAlerts] = useState<any[]>([]);
  const [msg, setMsg] = useState<string | null>(null);

  useEffect(() => {
    loadAlerts();
  }, []);

  const loadAlerts = async () => {
    try {
      const data = await api.getAlerts();
      setAlerts(data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleAck = async (id: string) => {
    try {
      await api.acknowledgeAlert(id);
      setMsg('Alert acknowledged.');
      await loadAlerts();
    } catch (err: any) {
      setMsg(`Error: ${err.message}`);
    }
  };

  const handleResolve = async (id: string) => {
    try {
      await api.resolveAlert(id);
      setMsg('Alert resolved.');
      await loadAlerts();
    } catch (err: any) {
      setMsg(`Error: ${err.message}`);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Alerts & Monitoring Centre</h1>
        <p className="text-xs text-slate-500 mt-1">
          Automated threshold monitoring for soil water deficit, frost hazards, and hardware outages.
        </p>
      </div>

      {msg && (
        <div className="p-4 bg-emerald-50 border border-emerald-200 text-emerald-800 text-sm font-medium rounded-xl flex items-center gap-2">
          <CheckCircle className="w-5 h-5 text-emerald-600" /> {msg}
        </div>
      )}

      <div className="space-y-4">
        {alerts.map((alt) => (
          <div key={alt.id} className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-3">
            <div className="flex justify-between items-start">
              <div className="flex items-center gap-3">
                <span
                  className={`p-2 rounded-xl ${
                    alt.severity === 'critical'
                      ? 'bg-red-100 text-red-600'
                      : 'bg-amber-100 text-amber-600'
                  }`}
                >
                  <AlertTriangle className="w-5 h-5" />
                </span>
                <div>
                  <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
                    Severity: {alt.severity} • Status: {alt.status}
                  </span>
                  <h3 className="text-base font-bold text-slate-900 mt-0.5">{alt.title}</h3>
                </div>
              </div>

              <span className="text-xs text-slate-400">
                {alt.triggered_at ? new Date(alt.triggered_at).toLocaleTimeString() : 'Active'}
              </span>
            </div>

            <p className="text-sm text-slate-700 leading-relaxed">{alt.message}</p>

            <div className="pt-2 border-t border-slate-100 flex items-center gap-3">
              {alt.status === 'active' && (
                <button
                  onClick={() => handleAck(alt.id)}
                  className="bg-amber-600 hover:bg-amber-700 text-white text-xs font-bold py-2 px-4 rounded-xl transition"
                >
                  Acknowledge Alert
                </button>
              )}
              {alt.status !== 'resolved' && (
                <button
                  onClick={() => handleResolve(alt.id)}
                  className="bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold py-2 px-4 rounded-xl transition"
                >
                  Mark Resolved
                </button>
              )}
              {alt.status === 'resolved' && (
                <span className="text-xs font-semibold text-emerald-600 flex items-center gap-1">
                  <CheckCircle className="w-4 h-4" /> Issue Closed & Resolved
                </span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
