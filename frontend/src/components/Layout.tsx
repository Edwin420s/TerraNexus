import React, { useState } from 'react';
import { 
  Sprout, LayoutDashboard, Zap, BrainCircuit, 
  Cpu, CheckSquare, Bell, Search, BookOpen, 
  ShieldCheck, Menu, X, ArrowUpRight
} from 'lucide-react';

interface LayoutProps {
  currentRoute: string;
  onNavigate: (route: string) => void;
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ currentRoute, onNavigate, children }) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navItems = [
    { label: 'Farm Dashboard', route: '/dashboard', icon: LayoutDashboard },
    { label: 'Farms & Fields', route: '/fields', icon: Sprout },
    { label: 'Irrigation Control Rig', route: '/irrigation/control', icon: Zap, badge: 'Interlocked' },
    { label: 'Agronomic AI & QVAC', route: '/intelligence', icon: BrainCircuit },
    { label: 'Devices & Telemetry', route: '/devices', icon: Cpu },
    { label: 'Operations & Tasks', route: '/operations', icon: CheckSquare },
    { label: 'Alerts & Monitoring', route: '/alerts', icon: Bell },
    { label: '126-Page Directory', route: '/directory', icon: BookOpen, badge: 'TNX-UI-001' },
  ];

  return (
    <div className="flex min-h-screen bg-slate-50">
      {/* Sidebar Navigation */}
      <aside className={`fixed inset-y-0 left-0 z-40 w-64 bg-slate-900 text-white flex flex-col justify-between transition-transform duration-300 md:translate-x-0 ${
        mobileMenuOpen ? 'translate-x-0' : '-translate-x-full'
      }`}>
        <div>
          {/* Brand Header */}
          <div className="h-16 flex items-center justify-between px-6 border-b border-slate-800">
            <div className="flex items-center gap-2.5 cursor-pointer" onClick={() => onNavigate('/dashboard')}>
              <div className="w-8 h-8 rounded-lg bg-emerald-500 flex items-center justify-center text-slate-950 font-black">
                TN
              </div>
              <span className="font-bold text-lg tracking-tight text-white">TerraNexus</span>
            </div>
            <button className="md:hidden text-slate-400" onClick={() => setMobileMenuOpen(false)}>
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Navigation Links */}
          <nav className="p-4 space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = currentRoute === item.route;
              return (
                <button
                  key={item.route}
                  onClick={() => {
                    onNavigate(item.route);
                    setMobileMenuOpen(false);
                  }}
                  className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-semibold transition ${
                    isActive
                      ? 'bg-emerald-500 text-slate-950 shadow-md'
                      : 'text-slate-300 hover:bg-slate-800/80 hover:text-white'
                  }`}
                >
                  <div className="flex items-center gap-2.5">
                    <Icon className="w-4 h-4" />
                    <span>{item.label}</span>
                  </div>
                  {item.badge && (
                    <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded-md ${
                      isActive ? 'bg-slate-950/20 text-slate-950' : 'bg-slate-800 text-emerald-400'
                    }`}>
                      {item.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Bottom Health & User Box */}
        <div className="p-4 border-t border-slate-800">
          <div className="bg-slate-800/60 rounded-xl p-3 text-xs space-y-1.5 mb-3">
            <div className="flex items-center justify-between text-slate-300 font-medium">
              <span>Platform Health</span>
              <span className="text-emerald-400 font-bold flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span> READY
              </span>
            </div>
            <p className="text-[10px] text-slate-400">PostgreSQL • Mosquitto MQTT • Redis</p>
          </div>

          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-emerald-600 flex items-center justify-center font-bold text-xs text-white">
              AD
            </div>
            <div className="flex-1 overflow-hidden">
              <h5 className="text-xs font-bold text-white truncate">Admin Nexus</h5>
              <p className="text-[10px] text-slate-400 truncate">admin@terranexus.org</p>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col md:pl-64 min-w-0">
        {/* Top Header */}
        <header className="h-16 bg-white border-b border-slate-200 px-6 flex items-center justify-between sticky top-0 z-30">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setMobileMenuOpen(true)}
              className="md:hidden p-2 text-slate-600 hover:bg-slate-100 rounded-lg"
            >
              <Menu className="w-5 h-5" />
            </button>
            <div className="flex items-center gap-2 text-xs font-medium text-slate-500">
              <span>TerraNexus</span>
              <span>/</span>
              <span className="text-slate-900 font-semibold capitalize">
                {currentRoute.replace('/', '').replace('-', ' ') || 'Dashboard'}
              </span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => onNavigate('/directory')}
              className="hidden sm:flex items-center gap-1.5 text-xs font-semibold bg-emerald-50 text-emerald-700 hover:bg-emerald-100 px-3 py-1.5 rounded-lg border border-emerald-200 transition"
            >
              <span>126-Page Specification</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </button>

            <button
              onClick={() => onNavigate('/alerts')}
              className="p-2 text-slate-600 hover:bg-slate-100 rounded-xl relative transition"
              title="Alerts"
            >
              <Bell className="w-4 h-4" />
              <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-red-500"></span>
            </button>
          </div>
        </header>

        {/* View Container */}
        <main className="p-6 max-w-7xl w-full mx-auto flex-1">
          {children}
        </main>
      </div>
    </div>
  );
};
