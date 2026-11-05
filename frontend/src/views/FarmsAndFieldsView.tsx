import React, { useEffect, useState } from 'react';
import { api } from '../api';
import { Sprout, Plus, MapPin, Eye, CheckCircle, FileText } from 'lucide-react';

export const FarmsAndFieldsView: React.FC = () => {
  const [farms, setFarms] = useState<any[]>([]);
  const [fields, setFields] = useState<any[]>([]);
  const [selectedField, setSelectedField] = useState<any>(null);
  const [observations, setObservations] = useState<any[]>([]);
  const [showAddFieldModal, setShowAddFieldModal] = useState(false);
  const [newFieldName, setNewFieldName] = useState('');
  const [newFieldArea, setNewFieldArea] = useState('5.0');
  const [newObsType, setNewObsType] = useState('pest_scouting');
  const [newObsDesc, setNewObsDesc] = useState('');
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [fData, fldData] = await Promise.all([
        api.getFarms().catch(() => []),
        api.getFields().catch(() => []),
      ]);
      setFarms(fData);
      setFields(fldData);
      if (fldData.length > 0) {
        setSelectedField(fldData[0]);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleCreateField = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newFieldName.trim() || farms.length === 0) return;
    try {
      await api.createField({
        farm_id: farms[0].id,
        name: newFieldName,
        area_hectares: parseFloat(newFieldArea) || 1.0,
      });
      setMessage('Field created successfully in PostgreSQL / PostGIS store.');
      setShowAddFieldModal(false);
      setNewFieldName('');
      await loadData();
    } catch (err: any) {
      setMessage(`Error: ${err.message}`);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Farms & Field Management</h1>
          <p className="text-xs text-slate-500 mt-1">
            Authoritative PostGIS spatial store. Multi-tenancy scoped by organisation.
          </p>
        </div>
        <button
          onClick={() => setShowAddFieldModal(true)}
          className="bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-semibold px-4 py-2.5 rounded-xl shadow transition flex items-center gap-2"
        >
          <Plus className="w-4 h-4" /> Add Field Plot
        </button>
      </div>

      {message && (
        <div className="p-4 bg-emerald-50 border border-emerald-200 text-emerald-800 text-sm font-medium rounded-xl flex items-center gap-2">
          <CheckCircle className="w-5 h-5 text-emerald-600" /> {message}
        </div>
      )}

      {/* Farms Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {farms.map((f) => (
          <div key={f.id} className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex items-start gap-4">
            <div className="p-3 bg-emerald-50 text-emerald-600 rounded-xl">
              <MapPin className="w-6 h-6" />
            </div>
            <div>
              <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full">
                Active Farm • {f.farm_code || 'GV-01'}
              </span>
              <h3 className="text-lg font-bold text-slate-900 mt-1">{f.name}</h3>
              <p className="text-xs text-slate-500 mt-1">
                Area: {f.area_hectares || 45.5} ha • Country: {f.country_code || 'KE'} • Timezone: {f.timezone || 'Africa/Nairobi'}
              </p>
            </div>
          </div>
        ))}
      </div>

      {/* Fields Grid */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
        <h3 className="text-base font-bold text-slate-900 mb-4 flex items-center gap-2">
          <Sprout className="w-5 h-5 text-emerald-600" /> Monitored Field Blocks ({fields.length})
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {fields.map((fld) => (
            <div
              key={fld.id}
              onClick={() => setSelectedField(fld)}
              className={`p-5 rounded-xl border cursor-pointer transition ${
                selectedField?.id === fld.id
                  ? 'border-emerald-500 bg-emerald-50/30 ring-2 ring-emerald-500/20'
                  : 'border-slate-200 hover:border-slate-300 bg-white'
              }`}
            >
              <div className="flex justify-between items-start mb-2">
                <span className="text-xs font-mono font-bold text-slate-500">{fld.field_code || 'FLD'}</span>
                <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800">
                  {fld.status}
                </span>
              </div>
              <h4 className="text-base font-bold text-slate-900">{fld.name}</h4>
              <p className="text-xs text-slate-500 mt-1">Area: {fld.area_hectares || 2.0} hectares</p>
              <div className="mt-4 pt-3 border-t border-slate-100 flex justify-between text-xs text-slate-600">
                <span>Crop: Active</span>
                <span className="text-emerald-600 font-semibold">View Details →</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Add Field Modal */}
      {showAddFieldModal && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-xl space-y-4">
            <h3 className="text-lg font-bold text-slate-900">Create New Field Block</h3>
            <form onSubmit={handleCreateField} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">Field Name</label>
                <input
                  type="text"
                  placeholder="e.g. West Acre - Drip Peppers"
                  value={newFieldName}
                  onChange={(e) => setNewFieldName(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm text-slate-800 outline-none focus:ring-2 focus:ring-emerald-500"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">Area (Hectares)</label>
                <input
                  type="number"
                  step="0.1"
                  value={newFieldArea}
                  onChange={(e) => setNewFieldArea(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm text-slate-800 outline-none focus:ring-2 focus:ring-emerald-500"
                  required
                />
              </div>

              <div className="flex gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowAddFieldModal(false)}
                  className="flex-1 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold py-2.5 rounded-xl text-sm transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold py-2.5 rounded-xl text-sm transition"
                >
                  Save Field
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
