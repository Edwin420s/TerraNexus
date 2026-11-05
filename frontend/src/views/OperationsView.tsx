import React, { useEffect, useState } from 'react';
import { api } from '../api';
import { CheckSquare, Wrench, Package, Scissors, Plus, CheckCircle } from 'lucide-react';

export const OperationsView: React.FC = () => {
  const [tasks, setTasks] = useState<any[]>([]);
  const [equipment, setEquipment] = useState<any[]>([]);
  const [inventory, setInventory] = useState<any[]>([]);
  const [harvests, setHarvests] = useState<any[]>([]);
  const [showNewTaskModal, setShowNewTaskModal] = useState(false);
  const [taskTitle, setTaskTitle] = useState('');
  const [taskType, setTaskType] = useState('scouting');
  const [taskPriority, setTaskPriority] = useState('medium');
  const [activeTab, setActiveTab] = useState<'tasks' | 'equipment' | 'inventory' | 'harvest'>('tasks');
  const [msg, setMsg] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [tData, eqData, invData, hData] = await Promise.all([
        api.getTasks().catch(() => []),
        api.getEquipment().catch(() => []),
        api.getInventory().catch(() => []),
        api.getHarvest().catch(() => []),
      ]);
      setTasks(tData);
      setEquipment(eqData);
      setInventory(invData);
      setHarvests(hData);
    } catch (err) {
      console.error(err);
    }
  };

  const handleCreateTask = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!taskTitle.trim()) return;
    try {
      await api.createTask({
        farm_id: 'c0000000-0000-0000-0000-000000000001',
        title: taskTitle,
        task_type: taskType,
        priority: taskPriority,
      });
      setMsg('Task created and assigned successfully.');
      setShowNewTaskModal(false);
      setTaskTitle('');
      await loadData();
    } catch (err: any) {
      setMsg(`Error: ${err.message}`);
    }
  };

  const handleUpdateTaskStatus = async (taskId: string, newStatus: string) => {
    try {
      await api.updateTask(taskId, { status: newStatus });
      await loadData();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Farm Operations & Workflows</h1>
          <p className="text-xs text-slate-500 mt-1">
            Tasks, equipment operating hours, warehouse input inventories, and harvest traceability.
          </p>
        </div>
        <button
          onClick={() => setShowNewTaskModal(true)}
          className="bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-semibold px-4 py-2.5 rounded-xl shadow transition flex items-center gap-2"
        >
          <Plus className="w-4 h-4" /> Create Work Order
        </button>
      </div>

      {msg && (
        <div className="p-4 bg-emerald-50 border border-emerald-200 text-emerald-800 text-sm font-medium rounded-xl flex items-center gap-2">
          <CheckCircle className="w-5 h-5 text-emerald-600" /> {msg}
        </div>
      )}

      {/* Navigation Tabs */}
      <div className="flex gap-2 border-b border-slate-200 pb-2">
        <button
          onClick={() => setActiveTab('tasks')}
          className={`px-4 py-2 rounded-xl text-sm font-bold flex items-center gap-2 transition ${
            activeTab === 'tasks' ? 'bg-emerald-600 text-white' : 'text-slate-600 hover:bg-slate-100'
          }`}
        >
          <CheckSquare className="w-4 h-4" /> Tasks ({tasks.length})
        </button>
        <button
          onClick={() => setActiveTab('equipment')}
          className={`px-4 py-2 rounded-xl text-sm font-bold flex items-center gap-2 transition ${
            activeTab === 'equipment' ? 'bg-emerald-600 text-white' : 'text-slate-600 hover:bg-slate-100'
          }`}
        >
          <Wrench className="w-4 h-4" /> Equipment ({equipment.length})
        </button>
        <button
          onClick={() => setActiveTab('inventory')}
          className={`px-4 py-2 rounded-xl text-sm font-bold flex items-center gap-2 transition ${
            activeTab === 'inventory' ? 'bg-emerald-600 text-white' : 'text-slate-600 hover:bg-slate-100'
          }`}
        >
          <Package className="w-4 h-4" /> Inputs & Inventory ({inventory.length})
        </button>
        <button
          onClick={() => setActiveTab('harvest')}
          className={`px-4 py-2 rounded-xl text-sm font-bold flex items-center gap-2 transition ${
            activeTab === 'harvest' ? 'bg-emerald-600 text-white' : 'text-slate-600 hover:bg-slate-100'
          }`}
        >
          <Scissors className="w-4 h-4" /> Harvest Logs ({harvests.length})
        </button>
      </div>

      {/* Tab Contents */}
      {activeTab === 'tasks' && (
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
          <h3 className="text-base font-bold text-slate-900 mb-4">Operations Task Checklist</h3>
          <div className="space-y-3">
            {tasks.map((t) => (
              <div
                key={t.id}
                className="p-4 rounded-xl border border-slate-200 flex items-center justify-between hover:bg-slate-50/50 transition"
              >
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold uppercase tracking-wider text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
                      {t.task_type}
                    </span>
                    <span
                      className={`text-xs font-semibold px-2 py-0.5 rounded ${
                        t.priority === 'high' ? 'bg-red-100 text-red-800' : 'bg-slate-100 text-slate-700'
                      }`}
                    >
                      {t.priority}
                    </span>
                  </div>
                  <h4 className="text-sm font-bold text-slate-900 mt-1">{t.title}</h4>
                  {t.description && <p className="text-xs text-slate-500 mt-0.5">{t.description}</p>}
                </div>

                <div className="flex items-center gap-2">
                  <select
                    value={t.status}
                    onChange={(e) => handleUpdateTaskStatus(t.id, e.target.value)}
                    className="text-xs font-semibold bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 text-slate-700 outline-none"
                  >
                    <option value="todo">To Do</option>
                    <option value="in_progress">In Progress</option>
                    <option value="completed">Completed</option>
                    <option value="blocked">Blocked</option>
                  </select>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'equipment' && (
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
          <h3 className="text-base font-bold text-slate-900 mb-4">Farm Machinery & Pumps</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {equipment.map((eq) => (
              <div key={eq.id} className="p-4 rounded-xl border border-slate-200">
                <span className="text-xs font-bold text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded-full uppercase">
                  {eq.equipment_type}
                </span>
                <h4 className="text-base font-bold text-slate-900 mt-1">{eq.name}</h4>
                <p className="text-xs text-slate-500 mt-1">Status: {eq.status} • Meter: {eq.operating_hours || 0} hrs</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'inventory' && (
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
          <h3 className="text-base font-bold text-slate-900 mb-4">Inputs & Warehouse Stock</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {inventory.map((inv) => (
              <div key={inv.id} className="p-4 rounded-xl border border-slate-200">
                <span className="text-xs font-bold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full uppercase">
                  {inv.category}
                </span>
                <h4 className="text-base font-bold text-slate-900 mt-1">{inv.item_name}</h4>
                <p className="text-lg font-bold text-slate-800 mt-2">
                  {inv.quantity_on_hand} <span className="text-xs text-slate-500 font-normal">{inv.unit_of_measure}</span>
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'harvest' && (
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
          <h3 className="text-base font-bold text-slate-900 mb-4">Harvest & Yield Traceability</h3>
          <p className="text-xs text-slate-500">
            Certified harvest lots with grade classification and batch numbering.
          </p>
        </div>
      )}

      {/* New Task Modal */}
      {showNewTaskModal && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-xl space-y-4">
            <h3 className="text-lg font-bold text-slate-900">Create Farm Work Order</h3>
            <form onSubmit={handleCreateTask} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">Task Title</label>
                <input
                  type="text"
                  placeholder="e.g. Inspect drip emitters for calcium clogging"
                  value={taskTitle}
                  onChange={(e) => setTaskTitle(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm text-slate-800 outline-none focus:ring-2 focus:ring-emerald-500"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">Category</label>
                <select
                  value={taskType}
                  onChange={(e) => setTaskType(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm text-slate-800 outline-none focus:ring-2 focus:ring-emerald-500"
                >
                  <option value="scouting">Scouting</option>
                  <option value="irrigation">Irrigation</option>
                  <option value="fertilizing">Fertilizing</option>
                  <option value="spraying">Spraying</option>
                  <option value="harvesting">Harvesting</option>
                  <option value="maintenance">Maintenance</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">Priority</label>
                <select
                  value={taskPriority}
                  onChange={(e) => setTaskPriority(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm text-slate-800 outline-none focus:ring-2 focus:ring-emerald-500"
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="urgent">Urgent</option>
                </select>
              </div>

              <div className="flex gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowNewTaskModal(false)}
                  className="flex-1 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold py-2.5 rounded-xl text-sm transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold py-2.5 rounded-xl text-sm transition"
                >
                  Create Task
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
