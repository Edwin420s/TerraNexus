import React, { useEffect, useState } from 'react';
import { api } from '../api';
import { 
  BrainCircuit, CheckCircle, XCircle, ArrowRight, 
  Send, Sparkles, Droplets, LineChart, Cpu, ShieldCheck,
  FileText, Mic, Volume2, Wallet, Coins, Play, Search,
  AlertTriangle, RefreshCw
} from 'lucide-react';

export const IntelligenceWorkspaceView: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'agronomy' | 'documents' | 'voice' | 'finance'>('agronomy');

  // Tab 1: Agronomy & FAO-56
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [prompt, setPrompt] = useState('');
  const [reasoningResult, setReasoningResult] = useState<any>(null);
  const [loadingReasoning, setLoadingReasoning] = useState(false);
  const [actionMessage, setActionMessage] = useState<string | null>(null);

  // Tab 2: Private Documents (Local RAG)
  const [documents, setDocuments] = useState<any[]>([]);
  const [docSearchQuery, setDocSearchQuery] = useState('');
  const [docSearchResults, setDocSearchResults] = useState<any[]>([]);
  const [docChatPrompt, setDocChatPrompt] = useState('');
  const [docChatResponse, setDocChatResponse] = useState<any>(null);
  const [loadingDocChat, setLoadingDocChat] = useState(false);
  const [newDocTitle, setNewDocTitle] = useState('');
  const [newDocCategory, setNewDocCategory] = useState('agronomy_guide');
  const [newDocContent, setNewDocContent] = useState('');
  const [showAddDocModal, setShowAddDocModal] = useState(false);

  // Tab 3: Speech AI (Whisper & TTS)
  const [ttsText, setTtsText] = useState('Soil moisture in tomato greenhouse zone 1 is 18.2%. Scheduled drip cycle recommended.');
  const [ttsAudioBase64, setTtsAudioBase64] = useState<string | null>(null);
  const [voiceQueryText, setVoiceQueryText] = useState('Why is my greenhouse soil moisture dropping and should I irrigate?');
  const [voiceAssistantResult, setVoiceAssistantResult] = useState<any>(null);
  const [loadingVoice, setLoadingVoice] = useState(false);

  // Tab 4: Tether WDK Finance
  const [wallet, setWallet] = useState<any>(null);
  const [payments, setPayments] = useState<any[]>([]);
  const [loadingFinance, setLoadingFinance] = useState(false);
  const [prepPurpose, setPrepPurpose] = useState('automated_soluble_potassium_restock');
  const [prepAmount, setPrepAmount] = useState('65.00');
  const [prepRecipient, setPrepRecipient] = useState('0x92E...AgriChemNairobi');
  const [prepDesc, setPrepDesc] = useState('Replenishment of water-soluble potassium sulfate for tomato flowering phase.');

  useEffect(() => {
    loadRecommendations();
    loadDocuments();
    loadFinance();
  }, []);

  const loadRecommendations = async () => {
    try {
      const data = await api.getRecommendations();
      setRecommendations(data);
    } catch (err) {
      console.error(err);
    }
  };

  const loadDocuments = async () => {
    try {
      const docs = await api.getDocuments();
      setDocuments(docs);
    } catch (err) {
      console.error(err);
    }
  };

  const loadFinance = async () => {
    setLoadingFinance(true);
    try {
      const [w, p] = await Promise.all([
        api.getFinanceWallet(),
        api.getFinancePayments()
      ]);
      setWallet(w);
      setPayments(p);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingFinance(false);
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

  const handleDocSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!docSearchQuery.trim()) return;
    try {
      const results = await api.queryDocuments(docSearchQuery);
      setDocSearchResults(results);
    } catch (err: any) {
      console.error(err);
    }
  };

  const handleDocChat = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!docChatPrompt.trim()) return;
    setLoadingDocChat(true);
    setDocChatResponse(null);
    try {
      const res = await api.chatDocuments(docChatPrompt);
      setDocChatResponse(res);
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoadingDocChat(false);
    }
  };

  const handleIndexDoc = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newDocTitle.trim() || !newDocContent.trim()) return;
    try {
      await api.indexDocument({
        title: newDocTitle,
        category: newDocCategory,
        content_text: newDocContent
      });
      setShowAddDocModal(false);
      setNewDocTitle('');
      setNewDocContent('');
      await loadDocuments();
      setActionMessage('Private document indexed into local vector database.');
    } catch (err: any) {
      console.error(err);
    }
  };

  const handleSynthesizeTts = async () => {
    if (!ttsText.trim()) return;
    try {
      const res = await api.synthesizeSpeech(ttsText);
      setTtsAudioBase64(res.audio_base64);
    } catch (err: any) {
      console.error(err);
    }
  };

  const handleRunVoiceAssistant = async () => {
    setLoadingVoice(true);
    setVoiceAssistantResult(null);
    try {
      const res = await api.voiceAssistant({ transcript_override: voiceQueryText });
      setVoiceAssistantResult(res);
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoadingVoice(false);
    }
  };

  const handlePreparePayment = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.prepareFinancePayment({
        purpose: prepPurpose,
        amount_usdt: parseFloat(prepAmount),
        recipient_address: prepRecipient,
        description: prepDesc
      });
      await loadFinance();
      setActionMessage('Disbursement proposal prepared. Requiring human operator approval signature.');
    } catch (err: any) {
      setActionMessage(`Error: ${err.message}`);
    }
  };

  const handleApprovePayment = async (paymentId: string) => {
    try {
      await api.approveFinancePayment(paymentId);
      await loadFinance();
      setActionMessage('Payment authorized and transaction broadcasted to network.');
    } catch (err: any) {
      setActionMessage(`Error: ${err.message}`);
    }
  };

  const handleRejectPayment = async (paymentId: string) => {
    try {
      await api.rejectFinancePayment(paymentId, 'Operator denied procurement request');
      await loadFinance();
      setActionMessage('Payment proposal rejected with audit record.');
    } catch (err: any) {
      setActionMessage(`Error: ${err.message}`);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-teal-900 via-indigo-950 to-slate-900 text-white p-6 rounded-2xl shadow-sm flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <div className="flex flex-wrap items-center gap-2 mb-1">
            <span className="bg-teal-500/20 text-teal-300 text-xs font-semibold px-2.5 py-0.5 rounded-full border border-teal-400/30">
              QVAC Edge AI Engine
            </span>
            <span className="bg-indigo-500/20 text-indigo-300 text-xs font-semibold px-2.5 py-0.5 rounded-full border border-indigo-400/30">
              Tether WDK Finance
            </span>
            <span className="bg-blue-500/20 text-blue-300 text-xs font-semibold px-2.5 py-0.5 rounded-full border border-blue-400/30">
              FAO-56 Soil Water Balance
            </span>
          </div>
          <h1 className="text-2xl font-bold">Agricultural Intelligence & Advisory Workspace</h1>
          <p className="text-xs text-teal-100 mt-1">
            Offline on-device agronomic reasoning, private document vector retrieval, speech synthesis, and self-custodial Tether USD₮ procurement with mandatory human approval.
          </p>
        </div>
      </div>

      {actionMessage && (
        <div className="p-4 bg-emerald-50 border border-emerald-200 text-emerald-800 text-sm font-medium rounded-xl flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CheckCircle className="w-5 h-5 text-emerald-600" /> {actionMessage}
          </div>
          <button onClick={() => setActionMessage(null)} className="text-xs text-slate-500 hover:text-slate-800">Dismiss</button>
        </div>
      )}

      {/* Workspace Navigation Tabs */}
      <div className="flex border-b border-slate-200 bg-white px-4 rounded-xl shadow-xs">
        <button
          onClick={() => setActiveTab('agronomy')}
          className={`py-3 px-4 text-xs font-bold border-b-2 flex items-center gap-2 transition ${
            activeTab === 'agronomy'
              ? 'border-teal-600 text-teal-700'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <Droplets className="w-4 h-4" /> Agronomic Deficit & FAO-56
        </button>
        <button
          onClick={() => setActiveTab('documents')}
          className={`py-3 px-4 text-xs font-bold border-b-2 flex items-center gap-2 transition ${
            activeTab === 'documents'
              ? 'border-teal-600 text-teal-700'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <FileText className="w-4 h-4" /> Private Documents & RAG ({documents.length})
        </button>
        <button
          onClick={() => setActiveTab('voice')}
          className={`py-3 px-4 text-xs font-bold border-b-2 flex items-center gap-2 transition ${
            activeTab === 'voice'
              ? 'border-teal-600 text-teal-700'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <Mic className="w-4 h-4" /> Voice Agronomist (Whisper & TTS)
        </button>
        <button
          onClick={() => setActiveTab('finance')}
          className={`py-3 px-4 text-xs font-bold border-b-2 flex items-center gap-2 transition ${
            activeTab === 'finance'
              ? 'border-teal-600 text-teal-700'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <Wallet className="w-4 h-4" /> Tether WDK Farm Finance
        </button>
      </div>

      {/* ==================== TAB 1: AGRONOMY & FAO-56 ==================== */}
      {activeTab === 'agronomy' && (
        <div className="space-y-6">
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
                <div style={{ width: '15%' }} className="bg-red-400 h-full flex items-center justify-center text-[10px] text-white font-bold">
                  Wilting (15%)
                </div>
                <div style={{ width: '10%' }} className="bg-amber-400 h-full flex items-center justify-center text-[10px] text-white font-bold">
                  MAD (25%)
                </div>
                <div style={{ width: '40%' }} className="bg-emerald-400 h-full flex items-center justify-center text-[10px] text-white font-bold">
                  Optimal Available Water
                </div>
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
      )}

      {/* ==================== TAB 2: PRIVATE DOCUMENTS (LOCAL RAG) ==================== */}
      {activeTab === 'documents' && (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                <FileText className="w-5 h-5 text-teal-600" /> Private Agricultural Documents & Knowledge Base
              </h2>
              <p className="text-xs text-slate-500">
                Local on-device vector retrieval (qvac-fabric-llm.cpp). Chunks documents and executes cosine similarity searches completely offline.
              </p>
            </div>
            <button
              onClick={() => setShowAddDocModal(true)}
              className="bg-teal-600 hover:bg-teal-700 text-white text-xs font-bold py-2.5 px-4 rounded-xl transition flex items-center gap-1.5"
            >
              + Index New Document
            </button>
          </div>

          {/* Add Document Modal */}
          {showAddDocModal && (
            <div className="bg-white rounded-2xl border border-teal-200 shadow-md p-6 space-y-4">
              <h3 className="text-sm font-bold text-slate-900">Index New Farm Document for Local RAG</h3>
              <form onSubmit={handleIndexDoc} className="space-y-3">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <div>
                    <label className="text-xs font-medium text-slate-600 block mb-1">Document Title</label>
                    <input
                      type="text"
                      placeholder="E.g., Drip Irrigation Maintenance Manual"
                      value={newDocTitle}
                      onChange={(e) => setNewDocTitle(e.target.value)}
                      className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs"
                      required
                    />
                  </div>
                  <div>
                    <label className="text-xs font-medium text-slate-600 block mb-1">Category</label>
                    <select
                      value={newDocCategory}
                      onChange={(e) => setNewDocCategory(e.target.value)}
                      className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs"
                    >
                      <option value="agronomy_guide">Agronomy Guide</option>
                      <option value="fao56_manual">FAO-56 Technical Standard</option>
                      <option value="soil_report">Soil & Water Analysis</option>
                      <option value="equipment_sop">Equipment SOP</option>
                    </select>
                  </div>
                </div>
                <div>
                  <label className="text-xs font-medium text-slate-600 block mb-1">Content (Markdown / Text)</label>
                  <textarea
                    rows={4}
                    placeholder="Enter document text to chunk and index into local vector store..."
                    value={newDocContent}
                    onChange={(e) => setNewDocContent(e.target.value)}
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl p-3 text-xs"
                    required
                  ></textarea>
                </div>
                <div className="flex justify-end gap-2">
                  <button
                    type="button"
                    onClick={() => setShowAddDocModal(false)}
                    className="text-xs text-slate-600 py-2 px-4 rounded-xl border border-slate-200"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="bg-teal-600 hover:bg-teal-700 text-white text-xs font-bold py-2 px-4 rounded-xl"
                  >
                    Index Document
                  </button>
                </div>
              </form>
            </div>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Left: Chat with Documents */}
            <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-4">
              <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-teal-600" /> Chat with Your Farm Documents (RAG)
              </h3>
              <p className="text-xs text-slate-500">
                Ask questions against private guides and FAO-56 standards. Grounded answers with exact chunk citations.
              </p>

              {docChatResponse && (
                <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 text-xs space-y-3">
                  <p className="font-semibold text-slate-800">Q: {docChatResponse.query}</p>
                  <p className="text-slate-700 leading-relaxed font-sans">{docChatResponse.answer}</p>
                  <div className="border-t border-slate-200 pt-2">
                    <span className="font-semibold text-slate-700 block mb-1">Citations ({docChatResponse.citations?.length}):</span>
                    {docChatResponse.citations?.map((c: any, i: number) => (
                      <div key={i} className="bg-white p-2 rounded-lg border border-slate-200 text-[11px] mb-1">
                        <span className="font-bold text-teal-700">{c.source_doc}</span> (Match: {(c.similarity_score * 100).toFixed(1)}%)
                        <p className="text-slate-600 mt-0.5">{c.text}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <form onSubmit={handleDocChat} className="flex gap-2">
                <input
                  type="text"
                  placeholder="Ask a question about your farm manuals or crop Kc values..."
                  value={docChatPrompt}
                  onChange={(e) => setDocChatPrompt(e.target.value)}
                  className="flex-1 bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-xs text-slate-800 outline-none focus:ring-2 focus:ring-teal-500"
                />
                <button
                  type="submit"
                  disabled={loadingDocChat || !docChatPrompt.trim()}
                  className="bg-teal-600 hover:bg-teal-700 disabled:bg-slate-200 text-white px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-1"
                >
                  {loadingDocChat ? 'Searching...' : <><Send className="w-3.5 h-3.5" /> Chat</>}
                </button>
              </form>
            </div>

            {/* Right: Indexed Documents List */}
            <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-4">
              <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                <FileText className="w-4 h-4 text-indigo-600" /> Indexed Documents ({documents.length})
              </h3>
              <div className="space-y-3 max-h-[380px] overflow-y-auto">
                {documents.map((d) => (
                  <div key={d.id} className="p-3 bg-slate-50 rounded-xl border border-slate-200 space-y-1">
                    <div className="flex justify-between items-start">
                      <span className="font-bold text-xs text-slate-900">{d.title}</span>
                      <span className="text-[10px] bg-teal-100 text-teal-800 font-bold px-2 py-0.5 rounded-full">
                        {d.chunks_count} Chunks
                      </span>
                    </div>
                    <span className="text-[10px] text-slate-500 uppercase tracking-wider font-semibold">
                      Category: {d.category}
                    </span>
                    <p className="text-xs text-slate-600 line-clamp-2 mt-1 font-mono">
                      {d.content_text}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ==================== TAB 3: VOICE AGRONOMIST ==================== */}
      {activeTab === 'voice' && (
        <div className="space-y-6">
          <div>
            <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
              <Mic className="w-5 h-5 text-indigo-600" /> On-Device Voice Agronomist (qvac-fabric-speech.cpp)
            </h2>
            <p className="text-xs text-slate-500">
              Offline Speech-to-Text (Whisper ASR) and Text-to-Speech (PCM WAV TTS) running locally on edge hardware.
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Voice Assistant Loop */}
            <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-4">
              <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                <Mic className="w-4 h-4 text-teal-600" /> Spoken Voice Query Simulation
              </h3>
              <p className="text-xs text-slate-500 leading-relaxed">
                Transcribe farmer audio instructions, evaluate with QVAC local LLM, and synthesize audio feedback in real-time.
              </p>

              <div>
                <label className="text-xs font-semibold text-slate-700 block mb-1">Farmer Voice Instruction</label>
                <input
                  type="text"
                  value={voiceQueryText}
                  onChange={(e) => setVoiceQueryText(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-xs text-slate-800"
                />
              </div>

              <button
                onClick={handleRunVoiceAssistant}
                disabled={loadingVoice}
                className="bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-200 text-white text-xs font-bold py-2.5 px-4 rounded-xl transition flex items-center gap-2"
              >
                {loadingVoice ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
                {loadingVoice ? 'Processing Voice Query...' : 'Simulate Voice Query & Synthesize Answer'}
              </button>

              {voiceAssistantResult && (
                <div className="bg-slate-50 border border-indigo-100 rounded-xl p-4 text-xs space-y-3">
                  <div className="flex items-center justify-between border-b border-slate-200 pb-2">
                    <span className="font-semibold text-slate-800">Transcription Result:</span>
                    <span className="text-[10px] bg-indigo-100 text-indigo-800 font-bold px-2 py-0.5 rounded-full">
                      Whisper ASR
                    </span>
                  </div>
                  <p className="text-slate-700 italic">"{voiceAssistantResult.transcription}"</p>

                  <div className="border-t border-slate-200 pt-2">
                    <span className="font-semibold text-slate-800 block mb-1">Agronomic Reasoning:</span>
                    <p className="text-slate-600">{voiceAssistantResult.reasoning}</p>
                  </div>

                  {voiceAssistantResult.audio_response?.audio_base64 && (
                    <div className="border-t border-slate-200 pt-3">
                      <span className="font-semibold text-slate-800 block mb-1">Synthesized Voice Response:</span>
                      <audio
                        controls
                        src={`data:audio/wav;base64,${voiceAssistantResult.audio_response.audio_base64}`}
                        className="w-full h-9 mt-1"
                      />
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Direct TTS Synthesis */}
            <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-4">
              <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                <Volume2 className="w-4 h-4 text-teal-600" /> Direct Text-to-Speech (TTS) Generator
              </h3>
              <p className="text-xs text-slate-500">
                Generate pure 16-bit PCM WAV spoken audio container from agronomic advisories.
              </p>

              <div>
                <label className="text-xs font-semibold text-slate-700 block mb-1">Advisory Text to Synthesize</label>
                <textarea
                  rows={3}
                  value={ttsText}
                  onChange={(e) => setTtsText(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl p-3 text-xs text-slate-800"
                ></textarea>
              </div>

              <button
                onClick={handleSynthesizeTts}
                className="bg-teal-600 hover:bg-teal-700 text-white text-xs font-bold py-2.5 px-4 rounded-xl transition flex items-center gap-2"
              >
                <Volume2 className="w-4 h-4" /> Generate Audio WAV
              </button>

              {ttsAudioBase64 && (
                <div className="bg-slate-50 border border-teal-200 rounded-xl p-4 text-xs space-y-2">
                  <span className="font-bold text-teal-900 block">Generated Audio Container:</span>
                  <audio
                    controls
                    src={`data:audio/wav;base64,${ttsAudioBase64}`}
                    className="w-full h-9"
                  />
                  <p className="text-[10px] text-slate-500 font-mono">
                    Format: audio/wav • Sample Rate: 16000Hz • Profile: agronomist_female
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* ==================== TAB 4: TETHER WDK FARM FINANCE ==================== */}
      {activeTab === 'finance' && (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                <Wallet className="w-5 h-5 text-emerald-600" /> Tether WDK Agentic Farm Finance
              </h2>
              <p className="text-xs text-slate-500">
                Self-custodial USD₮ micro-escrows and automated farm input replenishment with MANDATORY HUMAN APPROVAL.
              </p>
            </div>
            <button
              onClick={loadFinance}
              className="text-xs bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold py-2 px-3 rounded-xl flex items-center gap-1"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loadingFinance ? 'animate-spin' : ''}`} /> Refresh
            </button>
          </div>

          {/* Wallet Balance Cards */}
          {wallet && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-1">
                <span className="text-xs text-slate-500 font-semibold uppercase">Available Balance</span>
                <p className="text-2xl font-black text-emerald-600">
                  {wallet.balances.available_usdt.toFixed(2)} <span className="text-sm font-semibold">{wallet.currency}</span>
                </p>
                <span className="text-[10px] text-slate-400 block font-mono">Self-Custodial Vault</span>
              </div>
              <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-1">
                <span className="text-xs text-slate-500 font-semibold uppercase">Escrow Allocated</span>
                <p className="text-2xl font-black text-amber-600">
                  {wallet.balances.allocated_escrow_usdt.toFixed(2)} <span className="text-sm font-semibold">{wallet.currency}</span>
                </p>
                <span className="text-[10px] text-slate-400 block font-mono">Pending Deliveries</span>
              </div>
              <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-1">
                <span className="text-xs text-slate-500 font-semibold uppercase">Active Chain</span>
                <p className="text-xl font-bold text-indigo-700">{wallet.active_chain}</p>
                <span className="text-[10px] text-slate-400 block font-mono">Polygon PoS L2</span>
              </div>
              <div className="bg-emerald-50 p-5 rounded-2xl border border-emerald-200 shadow-sm space-y-1">
                <div className="flex items-center gap-1.5 text-emerald-800 text-xs font-bold uppercase">
                  <ShieldCheck className="w-4 h-4 text-emerald-600" /> Safety Gate
                </div>
                <p className="text-sm font-bold text-emerald-900">Human Approval Enforced</p>
                <p className="text-[10px] text-emerald-700">0.00 USD₮ Unattended Allowance</p>
              </div>
            </div>
          )}

          {/* Payments & Approval Gates */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left 2 Cols: Proposed & Broadcasted Disbursements */}
            <div className="lg:col-span-2 space-y-4">
              <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                <Coins className="w-4 h-4 text-emerald-600" /> Agent Procurement Proposals ({payments.length})
              </h3>

              <div className="space-y-3">
                {payments.map((p) => (
                  <div key={p.id} className="bg-white rounded-2xl border border-slate-200 shadow-sm p-5 space-y-3">
                    <div className="flex justify-between items-start">
                      <div>
                        <div className="flex items-center gap-2">
                          <span className={`text-[10px] font-bold uppercase px-2.5 py-0.5 rounded-full ${
                            p.status === 'pending_approval'
                              ? 'bg-amber-100 text-amber-800 border border-amber-300'
                              : p.status === 'broadcasted'
                              ? 'bg-emerald-100 text-emerald-800 border border-emerald-300'
                              : 'bg-red-100 text-red-800'
                          }`}>
                            {p.status}
                          </span>
                          <span className="text-xs text-slate-500 font-mono">{p.chain}</span>
                        </div>
                        <h4 className="text-base font-bold text-slate-900 mt-1">{p.purpose}</h4>
                      </div>
                      <div className="text-right">
                        <span className="text-lg font-black text-emerald-700">
                          {p.amount_usdt.toFixed(2)} {p.currency}
                        </span>
                        <span className="text-[10px] text-slate-400 block font-mono">{p.recipient_address.substring(0, 14)}...</span>
                      </div>
                    </div>

                    <p className="text-xs text-slate-600">{p.description}</p>

                    {p.agent_reasoning && (
                      <div className="bg-slate-50 p-2.5 rounded-xl text-xs text-slate-600 border border-slate-100">
                        <span className="font-semibold text-slate-700 block mb-0.5">Agent Reasoning:</span>
                        {p.agent_reasoning}
                      </div>
                    )}

                    {p.transaction_hash && (
                      <div className="text-[11px] text-slate-500 font-mono bg-emerald-50/50 p-2 rounded-lg border border-emerald-100">
                        <span className="font-semibold text-emerald-800">Tx Hash:</span> {p.transaction_hash}
                      </div>
                    )}

                    {p.status === 'pending_approval' && (
                      <div className="pt-2 border-t border-slate-100 flex items-center justify-between">
                        <span className="text-[11px] text-amber-700 font-semibold flex items-center gap-1">
                          <AlertTriangle className="w-3.5 h-3.5 text-amber-600" /> Human signature required to broadcast
                        </span>
                        <div className="flex gap-2">
                          <button
                            onClick={() => handleRejectPayment(p.id)}
                            className="text-xs text-red-600 hover:bg-red-50 font-bold py-1.5 px-3 rounded-lg transition"
                          >
                            Reject
                          </button>
                          <button
                            onClick={() => handleApprovePayment(p.id)}
                            className="bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold py-1.5 px-4 rounded-lg transition flex items-center gap-1"
                          >
                            <CheckCircle className="w-3.5 h-3.5" /> Approve & Broadcast
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Right: AI Agent Procurement Simulation Form */}
            <div className="space-y-4">
              <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                <BrainCircuit className="w-4 h-4 text-indigo-600" /> Simulate Agent Proposal
              </h3>
              <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-5">
                <form onSubmit={handlePreparePayment} className="space-y-3 text-xs">
                  <div>
                    <label className="font-semibold text-slate-700 block mb-1">Procurement Purpose</label>
                    <input
                      type="text"
                      value={prepPurpose}
                      onChange={(e) => setPrepPurpose(e.target.value)}
                      className="w-full bg-slate-50 border border-slate-200 rounded-xl p-2.5 text-xs text-slate-800"
                      required
                    />
                  </div>
                  <div>
                    <label className="font-semibold text-slate-700 block mb-1">Disbursement Amount (USD₮)</label>
                    <input
                      type="number"
                      step="0.01"
                      value={prepAmount}
                      onChange={(e) => setPrepAmount(e.target.value)}
                      className="w-full bg-slate-50 border border-slate-200 rounded-xl p-2.5 text-xs text-slate-800"
                      required
                    />
                  </div>
                  <div>
                    <label className="font-semibold text-slate-700 block mb-1">Target Vendor Address</label>
                    <input
                      type="text"
                      value={prepRecipient}
                      onChange={(e) => setPrepRecipient(e.target.value)}
                      className="w-full bg-slate-50 border border-slate-200 rounded-xl p-2.5 text-xs text-slate-800"
                      required
                    />
                  </div>
                  <div>
                    <label className="font-semibold text-slate-700 block mb-1">Telemetry-Driven Justification</label>
                    <textarea
                      rows={3}
                      value={prepDesc}
                      onChange={(e) => setPrepDesc(e.target.value)}
                      className="w-full bg-slate-50 border border-slate-200 rounded-xl p-2.5 text-xs text-slate-800"
                      required
                    ></textarea>
                  </div>
                  <button
                    type="submit"
                    className="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-bold py-2.5 rounded-xl transition flex items-center justify-center gap-1.5"
                  >
                    <Sparkles className="w-4 h-4" /> Agent Propose Disbursement
                  </button>
                </form>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
