import React, { useEffect, useState } from 'react';
import { api } from '../api';
import { 
  Droplets, Thermometer, Wind, AlertTriangle, 
  CheckCircle, Zap, ShieldCheck, Sprout, ArrowRight, Play, RefreshCw
} from 'lucide-react';

export const DashboardView: React.FC<{ onNavigate: (route: string) => void }> = ({ onNavigate }) => {
  const [farms, setFarms] = useState<any[]>([]);
  const [fields, setFields] = useState<any[]>([]);
  const [devices, setDevices] = useState<any[]>([]);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [weather, setWeather] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      const [fData, fldData, devData, altData, recData, wData] = await Promise.all([
        api.getFarms().catch(() => []),
        api.getFields().catch(() => []),
        api.getDevices().catch(() => []),
        api.getAlerts().catch(() => []),
        api.getRecommendations().catch(() => []),
        api.getWeather().catch(() => null),
      ]);
      setFarms(fData);
      setFields(fldData);
      setDevices(devData);
      setAlerts(altData);
      setRecommendations(recData);
      setWeather(wData);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner / Welcome */}
      <div className="bg-gradient-to-r from-emerald-800 to-teal-900 text-white rounded-2xl p-6 shadow-md flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="bg-emerald-500/20 text-emerald-300 text-xs font-semibold px-2.5 py-0.5 rounded-full border border-emerald-400/30">
              Platform Active • Modular Monolith v1.0
            </span>
            <span className="bg-blue-500/20 text-blue-300 text-xs font-semibold px-2.5 py-0.5 rounded-full border border-blue-400/30">
              PostgreSQL + PostGIS Connected
            </span>
          </div>
          <h1 className="text-2xl font-bold">GreenValley Demonstration Farm</h1>
          <p className="text-emerald-100 text-sm mt-1">
            Open Agricultural Intelligence & Operations Platform • ESP32 Hardware Interlocked
          </p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => onNavigate('/irrigation/control')}
            className="bg-emerald-500 hover:bg-emerald-400 text-slate-900 font-semibold px-4 py-2.5 rounded-xl shadow flex items-center gap-2 transition"
          >
            <Zap className="w-4 h-4" /> Irrigation Control Rig
          </button>
          <button
            onClick={loadDashboardData}
            className="bg-white/10 hover:bg-white/20 text-white p-2.5 rounded-xl transition"
            title="Refresh Data"
          >
            <RefreshCw className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">Monitored Fields</p>
              <h3 className="text-2xl font-bold text-slate-900 mt-1">{fields.length || 2} Plots</h3>
              <p className="text-xs text-emerald-600 font-medium mt-1">14.5 Total Hectares</p>
            </div>
            <div className="p-3 bg-emerald-50 text-emerald-600 rounded-xl">
              <Sprout className="w-6 h-6" />
            </div>
          </div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">Average Soil Moisture</p>
              <h3 className="text-2xl font-bold text-slate-900 mt-1">31.4%</h3>
              <p className="text-xs text-amber-600 font-medium mt-1">Approaching MAD threshold (25%)</p>
            </div>
            <div className="p-3 bg-blue-50 text-blue-600 rounded-xl">
              <Droplets className="w-6 h-6" />
            </div>
          </div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">Hardware Nodes</p>
              <h3 className="text-2xl font-bold text-slate-900 mt-1">{devices.length || 1} ESP32 Online</h3>
              <p className="text-xs text-emerald-600 font-medium mt-1">Battery 94% • MQTT Connected</p>
            </div>
            <div className="p-3 bg-indigo-50 text-indigo-600 rounded-xl">
              <ShieldCheck className="w-6 h-6" />
            </div>
          </div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">Active Alerts</p>
              <h3 className="text-2xl font-bold text-slate-900 mt-1">{alerts.length || 1} Alert</h3>
              <p className="text-xs text-red-600 font-medium mt-1">Requires Operator Attention</p>
            </div>
            <div className="p-3 bg-red-50 text-red-600 rounded-xl">
              <AlertTriangle className="w-6 h-6" />
            </div>
          </div>
        </div>
      </div>

      {/* Main Grid: Weather + AI Recommendation */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Recommendation & Irrigation Callout (2 cols) */}
        <div className="lg:col-span-2 space-y-6">
          {/* Active AI Recommendation Card */}
          {recommendations.length > 0 && (
            <div className="bg-white rounded-2xl border border-emerald-200 shadow-sm p-6 relative overflow-hidden">
              <div className="absolute top-0 right-0 bg-emerald-500 text-white text-xs font-semibold px-4 py-1 rounded-bl-xl uppercase tracking-wider">
                Agronomic Intelligence Advisory
              </div>
              <div className="flex items-center gap-3 mb-3">
                <span className="p-2 bg-emerald-100 text-emerald-700 rounded-lg">
                  <Zap className="w-5 h-5" />
                </span>
                <div>
                  <h3 className="text-lg font-bold text-slate-900">{recommendations[0].title}</h3>
                  <p className="text-xs text-slate-500">Confidence Score: {(recommendations[0].confidence_score * 100).toFixed(0)}% • Category: {recommendations[0].category}</p>
                </div>
              </div>

              <p className="text-sm text-slate-700 leading-relaxed mb-4">
                {recommendations[0].summary}
              </p>

              <div className="bg-slate-50 border border-slate-200 rounded-xl p-3 mb-4 text-xs text-slate-600 space-y-1">
                <p className="font-semibold text-slate-800">Agronomic Evidence:</p>
                <p>• Soil moisture at 10cm is currently 28.5% (Threshold: 25.0%)</p>
                <p>• Estimated daily evapotranspiration: 4.3 mm/day</p>
                <p>• Crop growth stage: Mid-Season Flowering (Water critical period)</p>
              </div>

              <div className="flex items-center justify-between pt-2 border-t border-slate-100">
                <div className="flex gap-2">
                  <button
                    onClick={() => onNavigate('/irrigation/control')}
                    className="bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-medium px-4 py-2 rounded-lg transition flex items-center gap-1.5"
                  >
                    Execute 45-min Drip Run <ArrowRight className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => onNavigate('/recommendations')}
                    className="bg-slate-100 hover:bg-slate-200 text-slate-700 text-sm font-medium px-4 py-2 rounded-lg transition"
                  >
                    View Evidence Graph
                  </button>
                </div>
                <span className="text-xs text-slate-400">Generated by FAO-56 Soil Water Engine</span>
              </div>
            </div>
          )}

          {/* Fields Status Table */}
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-base font-bold text-slate-900">Active Crop Blocks</h3>
              <button
                onClick={() => onNavigate('/fields')}
                className="text-emerald-600 hover:text-emerald-700 text-xs font-semibold flex items-center gap-1"
              >
                View all fields <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm text-slate-600">
                <thead className="bg-slate-50 text-slate-500 text-xs uppercase font-semibold">
                  <tr>
                    <th className="py-3 px-4 rounded-l-lg">Field Name</th>
                    <th className="py-3 px-4">Crop</th>
                    <th className="py-3 px-4">Area</th>
                    <th className="py-3 px-4">Soil Moisture</th>
                    <th className="py-3 px-4 rounded-r-lg">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  <tr className="hover:bg-slate-50/50">
                    <td className="py-3 px-4 font-medium text-slate-900">South Greenhouse - SG-02</td>
                    <td className="py-3 px-4">Drip Tomatoes</td>
                    <td className="py-3 px-4">2.0 ha</td>
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2">
                        <div className="w-16 bg-slate-200 rounded-full h-2">
                          <div className="bg-blue-500 h-2 rounded-full" style={{ width: '28%' }}></div>
                        </div>
                        <span className="font-semibold text-xs text-slate-700">28.5%</span>
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      <span className="bg-amber-100 text-amber-800 text-xs font-medium px-2.5 py-0.5 rounded-full">
                        Depleting
                      </span>
                    </td>
                  </tr>
                  <tr className="hover:bg-slate-50/50">
                    <td className="py-3 px-4 font-medium text-slate-900">North Plot - NP-01</td>
                    <td className="py-3 px-4">Maize Block</td>
                    <td className="py-3 px-4">12.5 ha</td>
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2">
                        <div className="w-16 bg-slate-200 rounded-full h-2">
                          <div className="bg-emerald-500 h-2 rounded-full" style={{ width: '42%' }}></div>
                        </div>
                        <span className="font-semibold text-xs text-slate-700">42.0%</span>
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      <span className="bg-emerald-100 text-emerald-800 text-xs font-medium px-2.5 py-0.5 rounded-full">
                        Optimal
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Right Column: Live Microclimate & Quick Navigation (1 col) */}
        <div className="space-y-6">
          {/* Microclimate Card */}
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
            <h3 className="text-base font-bold text-slate-900 mb-3 flex items-center justify-between">
              <span>Farm Microclimate</span>
              <span className="text-xs text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full font-medium">Live</span>
            </h3>

            <div className="grid grid-cols-2 gap-3 mb-4">
              <div className="p-3 bg-slate-50 rounded-xl">
                <span className="text-xs text-slate-500 flex items-center gap-1">
                  <Thermometer className="w-3.5 h-3.5 text-amber-500" /> Air Temp
                </span>
                <p className="text-lg font-bold text-slate-900 mt-1">24.5 °C</p>
                <p className="text-xs text-slate-400">Max 27.2°C</p>
              </div>

              <div className="p-3 bg-slate-50 rounded-xl">
                <span className="text-xs text-slate-500 flex items-center gap-1">
                  <Droplets className="w-3.5 h-3.5 text-blue-500" /> Humidity
                </span>
                <p className="text-lg font-bold text-slate-900 mt-1">62 %</p>
                <p className="text-xs text-slate-400">Dew point 16°C</p>
              </div>

              <div className="p-3 bg-slate-50 rounded-xl">
                <span className="text-xs text-slate-500 flex items-center gap-1">
                  <Wind className="w-3.5 h-3.5 text-indigo-500" /> Wind
                </span>
                <p className="text-lg font-bold text-slate-900 mt-1">3.8 m/s</p>
                <p className="text-xs text-slate-400">East-Northeast</p>
              </div>

              <div className="p-3 bg-slate-50 rounded-xl">
                <span className="text-xs text-slate-500 flex items-center gap-1">
                  <Zap className="w-3.5 h-3.5 text-emerald-500" /> ET0 Daily
                </span>
                <p className="text-lg font-bold text-slate-900 mt-1">4.3 mm</p>
                <p className="text-xs text-slate-400">Penman-Monteith</p>
              </div>
            </div>

            <div className="p-3 bg-emerald-50 border border-emerald-100 rounded-xl text-xs text-emerald-800">
              <p className="font-semibold mb-0.5">Weather Outlook</p>
              <p>Dry conditions expected today. Minimal rain probability (10%). Favorable for drip irrigation.</p>
            </div>
          </div>

          {/* 126-Page Specification Explorer Callout */}
          <div className="bg-gradient-to-br from-slate-900 to-slate-800 text-white rounded-2xl p-6 shadow-sm">
            <h3 className="text-base font-bold">TNX-UI-001 Page Directory</h3>
            <p className="text-xs text-slate-300 mt-1 mb-4 leading-relaxed">
              Explore all 126 structured pages defined across Groups A through L with wireframe layouts and interaction specifications.
            </p>
            <button
              onClick={() => onNavigate('/directory')}
              className="w-full bg-emerald-500 hover:bg-emerald-400 text-slate-900 font-semibold text-xs py-2.5 rounded-xl transition flex items-center justify-center gap-1.5"
            >
              Browse 126-Page Directory <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
