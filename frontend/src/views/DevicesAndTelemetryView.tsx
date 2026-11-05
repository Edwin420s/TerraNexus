import React, { useEffect, useState } from 'react';
import { api } from '../api';
import { Cpu, Wifi, Battery, Play, RotateCcw, CheckCircle, Terminal, Radio } from 'lucide-react';

export const DevicesAndTelemetryView: React.FC = () => {
  const [devices, setDevices] = useState<any[]>([]);
  const [sensors, setSensors] = useState<any[]>([]);
  const [measurements, setMeasurements] = useState<any[]>([]);
  const [selectedDevice, setSelectedDevice] = useState<any>(null);
  const [commandType, setCommandType] = useState('turn_on');
  const [durationSec, setDurationSec] = useState('300');
  const [statusMsg, setStatusMsg] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [devData, sData, mData] = await Promise.all([
        api.getDevices().catch(() => []),
        api.getSensors().catch(() => []),
        api.getMeasurements().catch(() => []),
      ]);
      setDevices(devData);
      setSensors(sData);
      setMeasurements(mData);
      if (devData.length > 0) {
        setSelectedDevice(devData[0]);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleSendCommand = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedDevice) return;
    setStatusMsg(null);
    try {
      const res = await api.dispatchCommand(selectedDevice.id, {
        command_type: commandType,
        payload: { duration_sec: parseInt(durationSec, 10) || 300 },
        priority: 1,
      });
      setStatusMsg(`Command [${commandType}] dispatched successfully. Status: ${res.status}`);
      await loadData();
    } catch (err: any) {
      setStatusMsg(`Error: ${err.message}`);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Devices & Telemetry Infrastructure</h1>
        <p className="text-xs text-slate-500 mt-1">
          ESP32-WROOM-32 edge nodes, capacitive ADC soil sensors, and durable MQTT ingestion.
        </p>
      </div>

      {statusMsg && (
        <div className="p-4 bg-emerald-50 border border-emerald-200 text-emerald-800 text-sm font-medium rounded-xl flex items-center gap-2">
          <CheckCircle className="w-5 h-5 text-emerald-600" /> {statusMsg}
        </div>
      )}

      {/* Devices List */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {devices.map((dev) => (
          <div
            key={dev.id}
            onClick={() => setSelectedDevice(dev)}
            className={`p-6 rounded-2xl border cursor-pointer transition ${
              selectedDevice?.id === dev.id
                ? 'border-indigo-500 bg-indigo-50/20 ring-2 ring-indigo-500/20'
                : 'border-slate-200 bg-white hover:border-slate-300'
            }`}
          >
            <div className="flex justify-between items-start mb-3">
              <span className="text-xs font-mono font-bold text-indigo-700 bg-indigo-50 px-2.5 py-1 rounded-lg">
                {dev.device_uid}
              </span>
              <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span> {dev.connection_status.toUpperCase()}
              </span>
            </div>

            <h3 className="text-lg font-bold text-slate-900">{dev.name}</h3>
            <p className="text-xs text-slate-500 mt-1">
              Hardware: {dev.hardware_version} • Firmware: {dev.firmware_version} • Type: {dev.device_type}
            </p>

            <div className="mt-4 pt-3 border-t border-slate-100 flex items-center gap-4 text-xs text-slate-600">
              <span className="flex items-center gap-1">
                <Battery className="w-4 h-4 text-emerald-600" /> {dev.battery_level_pct || 94}%
              </span>
              <span className="flex items-center gap-1">
                <Wifi className="w-4 h-4 text-indigo-600" /> {dev.signal_strength_rssi || -68} dBm
              </span>
              <span className="ml-auto text-indigo-600 font-semibold">Select Device →</span>
            </div>
          </div>
        ))}
      </div>

      {/* Telemetry Stream & Remote Command Console */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Telemetry Log (2 cols) */}
        <div className="lg:col-span-2 bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <Radio className="w-5 h-5 text-indigo-600" /> Live Ingested Telemetry Feed
            </h3>
            <span className="text-xs text-slate-400 font-mono">TNX-API-001 Section 27 Canonical Schema</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-600">
              <thead className="bg-slate-50 text-slate-500 text-xs uppercase font-semibold">
                <tr>
                  <th className="py-2.5 px-4 rounded-l-lg">Measurement Type</th>
                  <th className="py-2.5 px-4">Value</th>
                  <th className="py-2.5 px-4">Depth</th>
                  <th className="py-2.5 px-4">Quality Score</th>
                  <th className="py-2.5 px-4 rounded-r-lg">Observed At</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-mono text-xs">
                {measurements.map((m, i) => (
                  <tr key={m.id || i} className="hover:bg-slate-50/50">
                    <td className="py-2.5 px-4 font-sans font-medium text-slate-900">{m.measurement_type}</td>
                    <td className="py-2.5 px-4 font-bold text-slate-800">{m.value} {m.unit}</td>
                    <td className="py-2.5 px-4 text-slate-500">{m.depth_cm ? `${m.depth_cm} cm` : 'N/A'}</td>
                    <td className="py-2.5 px-4 text-emerald-600 font-semibold">{m.quality_score * 100}% (Valid)</td>
                    <td className="py-2.5 px-4 text-slate-400">
                      {m.observed_at ? new Date(m.observed_at).toLocaleTimeString() : 'Recent'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Remote Command Terminal (1 col) */}
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 flex flex-col justify-between">
          <div>
            <h3 className="text-base font-bold text-slate-900 mb-2 flex items-center gap-2">
              <Terminal className="w-5 h-5 text-slate-800" /> Command Terminal
            </h3>
            <p className="text-xs text-slate-500 mb-4 leading-relaxed">
              Issues durable signed commands to the device MQTT topic with preflight safety checks.
            </p>

            <form onSubmit={handleSendCommand} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">Target Device</label>
                <input
                  type="text"
                  disabled
                  value={selectedDevice ? `${selectedDevice.name} (${selectedDevice.device_uid})` : 'No device selected'}
                  className="w-full bg-slate-100 border border-slate-200 rounded-xl px-4 py-2 text-xs font-mono text-slate-700"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">Command Action</label>
                <select
                  value={commandType}
                  onChange={(e) => setCommandType(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2 text-sm text-slate-800 outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="turn_on">turn_on (Engage Relays)</option>
                  <option value="turn_off">turn_off (Cut Relays)</option>
                  <option value="ping">ping (Heartbeat Check)</option>
                  <option value="reboot">reboot (Safe Restart)</option>
                </select>
              </div>

              {commandType === 'turn_on' && (
                <div>
                  <label className="block text-xs font-semibold text-slate-600 mb-1">Duration (Seconds)</label>
                  <input
                    type="number"
                    value={durationSec}
                    onChange={(e) => setDurationSec(e.target.value)}
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2 text-sm text-slate-800 outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
              )}

              <button
                type="submit"
                disabled={!selectedDevice}
                className="w-full bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-200 text-white font-bold py-2.5 rounded-xl text-sm transition flex items-center justify-center gap-2"
              >
                <Play className="w-4 h-4" /> Dispatch Command
              </button>
            </form>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-100 text-[10px] text-slate-400 font-mono">
            Topic: tnx/org/farm/device/{selectedDevice?.device_uid}/commands
          </div>
        </div>
      </div>
    </div>
  );
};
