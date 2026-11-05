import React, { useState } from 'react';
import { ALL_126_PAGES, PageDef } from '../types/pages';
import { Search, Filter, BookOpen, ExternalLink, ArrowRight } from 'lucide-react';

export const PlatformDirectoryView: React.FC<{ onNavigate: (route: string) => void }> = ({ onNavigate }) => {
  const [search, setSearch] = useState('');
  const [selectedGroup, setSelectedGroup] = useState<string>('ALL');
  const [selectedPage, setSelectedPage] = useState<PageDef | null>(ALL_126_PAGES[0]);

  const groups = ['ALL', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L'];

  const filteredPages = ALL_126_PAGES.filter((p) => {
    const matchesGroup = selectedGroup === 'ALL' || p.group === selectedGroup;
    const matchesSearch =
      p.name.toLowerCase().includes(search.toLowerCase()) ||
      p.route.toLowerCase().includes(search.toLowerCase()) ||
      p.category.toLowerCase().includes(search.toLowerCase()) ||
      p.number.includes(search);
    return matchesGroup && matchesSearch;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2 mb-1">
          <span className="bg-emerald-100 text-emerald-800 text-xs font-bold px-2.5 py-0.5 rounded-full">
            TNX-UI-001 Complete Specification
          </span>
          <span className="text-xs text-slate-500 font-mono">126 Pages Fully Catalogued</span>
        </div>
        <h1 className="text-2xl font-bold text-slate-900">Platform Page & Route Directory</h1>
        <p className="text-xs text-slate-500 mt-1">
          Every screen from the 126-page UI/UX specification mapped with routes, wireframe outlines, and functional operations.
        </p>
      </div>

      {/* Filter & Search Bar */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm flex flex-col md:flex-row gap-4 items-center justify-between">
        {/* Search Input */}
        <div className="relative w-full md:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
          <input
            type="text"
            placeholder="Search by page name, number, or route..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-slate-50 border border-slate-200 rounded-xl pl-10 pr-4 py-2 text-xs text-slate-800 outline-none focus:ring-2 focus:ring-emerald-500"
          />
        </div>

        {/* Group Filter Buttons */}
        <div className="flex gap-1 overflow-x-auto w-full md:w-auto pb-1">
          {groups.map((g) => (
            <button
              key={g}
              onClick={() => setSelectedGroup(g)}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition whitespace-nowrap ${
                selectedGroup === g
                  ? 'bg-slate-900 text-white'
                  : 'bg-slate-100 hover:bg-slate-200 text-slate-600'
              }`}
            >
              {g === 'ALL' ? 'All (126)' : `Group ${g}`}
            </button>
          ))}
        </div>
      </div>

      {/* Directory Grid & Detail Drawer */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Pages List (2 cols) */}
        <div className="lg:col-span-2 bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-sm font-bold text-slate-700 uppercase tracking-wider">
              Showing {filteredPages.length} of 126 Pages
            </h3>
          </div>

          <div className="space-y-2 max-h-[600px] overflow-y-auto pr-2">
            {filteredPages.map((page) => (
              <div
                key={page.id}
                onClick={() => setSelectedPage(page)}
                className={`p-3.5 rounded-xl border cursor-pointer transition flex items-center justify-between ${
                  selectedPage?.id === page.id
                    ? 'border-emerald-500 bg-emerald-50/40 ring-1 ring-emerald-500'
                    : 'border-slate-100 hover:border-slate-300 hover:bg-slate-50/50'
                }`}
              >
                <div className="flex items-center gap-3">
                  <span className="text-xs font-mono font-bold text-slate-500 w-8">{page.number}.</span>
                  <div>
                    <h4 className="text-sm font-bold text-slate-900">{page.name}</h4>
                    <p className="text-xs font-mono text-emerald-700">{page.route}</p>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <span className="text-[10px] font-bold uppercase tracking-wider bg-slate-100 text-slate-600 px-2 py-0.5 rounded">
                    Group {page.group} • {page.category}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Selected Page Spec Detail Inspector (1 col) */}
        {selectedPage && (
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-4">
            <div>
              <span className="text-xs font-bold uppercase tracking-wider bg-emerald-100 text-emerald-800 px-2.5 py-1 rounded-md">
                Screen {selectedPage.number} • Group {selectedPage.group}
              </span>
              <h3 className="text-lg font-bold text-slate-900 mt-2">{selectedPage.name}</h3>
              <p className="text-xs font-mono text-slate-500 mt-0.5">Route: {selectedPage.route}</p>
            </div>

            <div className="space-y-1">
              <span className="text-xs font-semibold text-slate-500 uppercase">Functional Purpose:</span>
              <p className="text-xs text-slate-700 leading-relaxed bg-slate-50 p-3 rounded-xl border border-slate-100">
                {selectedPage.description}
              </p>
            </div>

            <div className="space-y-1">
              <span className="text-xs font-semibold text-slate-500 uppercase">Primary User Actions:</span>
              <ul className="text-xs text-slate-700 space-y-1">
                {selectedPage.primaryActions.map((act, i) => (
                  <li key={i} className="flex items-center gap-1.5">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span> {act}
                  </li>
                ))}
              </ul>
            </div>

            <div className="pt-4 border-t border-slate-100">
              <button
                onClick={() => {
                  // If it corresponds to a primary functional view, navigate to it
                  if (selectedPage.route.includes('/irrigation')) onNavigate('/irrigation/control');
                  else if (selectedPage.route.includes('/intelligence') || selectedPage.route.includes('/recommendations')) onNavigate('/intelligence');
                  else if (selectedPage.route.includes('/devices') || selectedPage.route.includes('/sensors')) onNavigate('/devices');
                  else if (selectedPage.route.includes('/fields') || selectedPage.route.includes('/farms')) onNavigate('/fields');
                  else if (selectedPage.route.includes('/tasks') || selectedPage.route.includes('/operations')) onNavigate('/operations');
                  else if (selectedPage.route.includes('/alerts') || selectedPage.route.includes('/monitoring')) onNavigate('/alerts');
                  else onNavigate('/dashboard');
                }}
                className="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs py-2.5 rounded-xl transition flex items-center justify-center gap-2"
              >
                Launch Screen View <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
