import React, { useEffect, useState } from 'react';
import { api } from '../api';
import { 
  BrainCircuit, CheckCircle, XCircle, ArrowRight, 
  Send, Sparkles, Droplets, LineChart, Cpu, ShieldCheck
} from 'lucide-react';

export const IntelligenceWorkspaceView: React.FC = () => {
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [prompt, setPrompt] = useState('');
  const [reasoningResult, setReasoningResult] = useState<any>(null);
  const [loadingReasoning, setLoadingReasoning] = useState(false);
  const [actionMessage, setActionMessage] = useState<string | null>(null);

  useEffect(() => {
    loadRecommendations();
  }, []);

  const loadRecommendations = async () => {
    try {
      const data = await api.getRecommendations();
      setRecommendations(data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleAccept = async (id: string) => {
    try {
      await api.acceptRecommendation(id);
      setActionMessage('Recommendation accepted and queued for execution.');
      await loadRecommendations();
    } catch (err: any) {
      setActionMessage(`Error: ${err.message}`);
    }
  };

  const handleReject = async (id: string) => {
    try {
      await api.rejectRecommendation(id);
      setActionMessage('Recommendation rejected with operator feedback.');
      await loadRecommendations();
    } catch (err: any) {
      setActionMessage(`Error: ${err.message}`);
    }
  };

  const handleRunReasoning = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) return;
    setLoadingReasoning(true);
    setReasoningResult(null);
    try {
      const res = await api.runLocalReasoning(prompt);
      setReasoningResult(res);
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoadingReasoning(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-teal-900 to-indigo-950 text-white p-6 rounded-2xl shadow-sm flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="bg-teal-500/20 text-teal-300 text-xs font-semibold px-2.5 py-0.5 rounded-full border border-teal-400/30">
              Agronomic Intelligence • FAO-56 Engine
            </span>
            <span className="bg-indigo-500/20 text-indigo-300 text-xs font-semibold px-2.5 py-0.5 rounded-full border border-indigo-400/30">
              QVAC Edge LLM Adapter
            </span>
          </div>
          <h1 className="text-2xl font-bold">Agricultural Intelligence & Advisory Workspace</h1>
          <p className="text-xs text-teal-100 mt-1">
            Synthesizes soil probe measurements, weather predictions, and FAO-56 crop coefficient curves into auditable farming actions.
          </p>
        </div>
      </div>

      {actionMessage && (
        <div className="p-4 bg-emerald-50 border border-emerald-200 text-emerald-800 text-sm font-medium rounded-xl flex items-center gap-2">
          <CheckCircle className="w-5 h-5 text-emerald-600" /> {actionMessage}
        </div>
      )}

      {/* Soil Water Depletion Curve Visualizer */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
        <h3 className="text-base font-bold text-slate-900 mb-2 flex items-center gap-2">
          <Droplets className="w-5 h-5 text-blue-500" /> Soil Moisture Depletion vs Agronomic Thresholds (SG-02 Drip Tomatoes)
        </h3>
        <p className="text-xs text-slate-500 mb-4">
          Management Allowed Depletion (MAD = 50%). When available water drops below 25%, irrigation must be scheduled to prevent yield reduction.
        </p>

        <div className="relative pt-6 pb-2">
          {/* Progress bar visualizer */}
          <div className="h-8 bg-slate-100 rounded-xl relative overflow-hidden flex">
            {/* Wilting Point (0 - 15%) */}
            <div style={{ width: '15%' }} className="bg-red-400 h-full flex items-center justify-center text-[10px] text-white font-bold">
              Wilting (15%)
            </div>
            {/* Stress Zone (15 - 25%) */}
            <div style={{ width: '10%' }} className="bg-amber-400 h-full flex items-center justify-center text-[10px] text-white font-bold">
              MAD (25%)
            </div>
            {/* Optimal Moisture Zone (25 - 65%) */}
            <div style={{ width: '40%' }} className="bg-emerald-400 h-full flex items-center justify-center text-[10px] text-white font-bold">
              Optimal Available Water
            </div>
            {/* Saturation Zone (65 - 100%) */}
            <div style={{ width: '35%' }} className="bg-blue-300 h-full flex items-center justify-center text-[10px] text-slate-800 font-bold">
              Field Capacity (65%)
            </div>
          </div>

          {/* Current Needle */}
          <div className="mt-2 flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-blue-600 animate-ping"></span>
            <span className="text-sm font-bold text-slate-900">Current Measured Moisture: 28.5% (Volumetric Water Content)</span>
            <span className="text-xs text-amber-600 font-medium bg-amber-50 px-2 py-0.5 rounded-md ml-auto">
              3.5% above MAD threshold
            </span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column: Recommendations */}
        <div className="space-y-4">
          <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <BrainCircuit className="w-5 h-5 text-indigo-600" /> Active Recommendations ({recommendations.length})
          </h3>

          {recommendations.map((rec) => (
            <div key={rec.id} className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-4">
              <div className="flex justify-between items-start">
                <div>
                  <span className="text-xs font-semibold uppercase px-2.5 py-0.5 rounded-full bg-indigo-50 text-indigo-700">
                    {rec.category} • Urgency: {rec.urgency}
                  </span>
                  <h4 className="text-base font-bold text-slate-900 mt-2">{rec.title}</h4>
                </div>
                <span className="text-xs font-bold text-emerald-600 bg-emerald-50 px-2 py-1 rounded-lg">
                  {(rec.confidence_score * 100).toFixed(0)}% Confidence
                </span>
              </div>

              <p className="text-sm text-slate-700 leading-relaxed">{rec.summary}</p>

              <div className="bg-slate-50 rounded-xl p-3 text-xs text-slate-600 space-y-1">
                <p className="font-semibold text-slate-800">Agronomic Rationale:</p>
                <p>{rec.rationale}</p>
              </div>

              {rec.evidence && rec.evidence.length > 0 && (
                <div className="pt-2 border-t border-slate-100">
                  <p className="text-xs font-semibold text-slate-500 mb-2">Evidence Citations:</p>
                  <div className="grid grid-cols-1 gap-2">
                    {rec.evidence.map((ev: any, i: number) => (
                      <div key={i} className="text-xs bg-slate-50 p-2 rounded-lg flex justify-between">
                        <span className="font-medium text-slate-700">{ev.metric_name}</span>
                        <span className="text-slate-500 font-mono">{ev.observed_value} (Threshold: {ev.threshold_value})</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="flex items-center gap-3 pt-2">
                <button
                  onClick={() => handleAccept(rec.id)}
                  className="bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold py-2.5 px-4 rounded-xl transition flex items-center gap-1.5"
                >
                  <CheckCircle className="w-4 h-4" /> Accept & Schedule Run
                </button>
                <button
                  onClick={() => handleReject(rec.id)}
                  className="bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold py-2.5 px-4 rounded-xl transition flex items-center gap-1.5"
                >
                  <XCircle className="w-4 h-4" /> Reject with Feedback
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Right Column: QVAC Local AI Terminal */}
        <div className="space-y-4">
          <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <Cpu className="w-5 h-5 text-teal-600" /> Local QVAC AI Agronomist
          </h3>

          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 flex flex-col justify-between min-h-[420px]">
            <div>
              <p className="text-xs text-slate-500 mb-4 leading-relaxed">
                Query the local quantized agronomic LLM model running on your edge node or local environment. Operates 100% offline without sending farm data to external clouds.
              </p>

              {/* Chat Output */}
              {reasoningResult ? (
                <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 mb-4 text-xs space-y-3">
                  <div className="flex items-center justify-between border-b border-slate-200 pb-2">
                    <span className="font-semibold text-slate-800 flex items-center gap-1.5">
                      <Sparkles className="w-4 h-4 text-amber-500" /> Model: {reasoningResult.model}
                    </span>
                    <span className="text-[10px] bg-teal-100 text-teal-800 font-bold px-2 py-0.5 rounded-full">
                      {reasoningResult.execution_mode}
                    </span>
                  </div>

                  <p className="text-slate-700 leading-relaxed text-sm font-sans">
                    {reasoningResult.reasoning}
                  </p>

                  <div className="pt-2 border-t border-slate-200">
                    <span className="font-semibold text-slate-700">Proposed Actions:</span>
                    <ul className="list-disc list-inside mt-1 space-y-0.5 text-slate-600">
                      {reasoningResult.suggested_actions.map((act: any, i: number) => (
                        <li key={i}>{act.action} (Zone: {act.zone || 'all'}, Duration: {act.duration_minutes || 30} min)</li>
                      ))}
                    </ul>
                  </div>
                </div>
              ) : (
                <div className="bg-slate-50 border border-dashed border-slate-200 rounded-xl p-8 text-center text-slate-400 text-xs mb-4">
                  Ask a question below, e.g.:
                  <br />
                  <span className="text-slate-600 font-medium">"What is the irrigation priority for the greenhouse tomato block given today's solar radiation?"</span>
                </div>
              )}
            </div>

            {/* Prompt Input Form */}
            <form onSubmit={handleRunReasoning} className="flex gap-2">
              <input
                type="text"
                placeholder="Ask QVAC Agronomist (e.g., analyze water deficit for tomato block)..."
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                className="flex-1 bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm text-slate-800 outline-none focus:ring-2 focus:ring-teal-500"
              />
              <button
                type="submit"
                disabled={loadingReasoning || !prompt.trim()}
                className="bg-teal-600 hover:bg-teal-700 disabled:bg-slate-200 text-white px-5 py-2.5 rounded-xl font-bold text-sm transition flex items-center gap-1.5"
              >
                {loadingReasoning ? 'Thinking...' : <><Send className="w-4 h-4" /> Ask</>}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};
