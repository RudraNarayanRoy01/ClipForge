import React, { useEffect } from 'react';
import { useCampaignStore } from '../store/useCampaignStore';
import { CampaignImportCard } from '../components/campaigns/CampaignImportCard';
import { CampaignGrid } from '../components/campaigns/CampaignGrid';
import { CampaignDetailDrawer } from '../components/campaigns/CampaignDetailDrawer';
import { RefreshCw, LayoutTemplate } from 'lucide-react';
import { Link } from 'react-router-dom';

const CampaignsPage: React.FC = () => {
  const { fetchCampaigns, isLoadingList, activeCampaignId } = useCampaignStore();

  useEffect(() => {
    fetchCampaigns();
  }, [fetchCampaigns]);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-200 flex font-sans overflow-hidden">
      
      {/* MOCK SIDEBAR (To keep it consistent with Dashboard left nav conceptually) */}
      <nav className="w-16 lg:w-64 border-r border-slate-800 bg-slate-950 flex flex-col items-center lg:items-start py-6 shrink-0">
        <div className="px-4 mb-8 hidden lg:block">
          <h1 className="text-xl font-bold bg-gradient-to-r from-blue-400 to-indigo-500 bg-clip-text text-transparent">
            ClipForge
          </h1>
        </div>
        <div className="w-full space-y-2 px-2">
          <Link to="/projects" className="flex items-center gap-3 px-3 py-2 text-slate-400 hover:text-slate-200 hover:bg-slate-900 rounded-lg transition-colors">
            <LayoutTemplate className="w-5 h-5 shrink-0" />
            <span className="hidden lg:inline font-medium">Projects</span>
          </Link>
          <Link to="/campaigns" className="flex items-center gap-3 px-3 py-2 text-indigo-400 bg-indigo-950/30 rounded-lg transition-colors">
            <LayoutTemplate className="w-5 h-5 shrink-0" />
            <span className="hidden lg:inline font-medium">Campaigns</span>
          </Link>
        </div>
      </nav>

      {/* MAIN WORKSPACE */}
      <main className="flex-1 flex flex-col relative overflow-hidden">
        
        {/* HEADER */}
        <header className="h-20 border-b border-slate-800 bg-slate-950 flex items-center justify-between px-8 shrink-0">
          <div>
            <h1 className="text-2xl font-bold text-slate-100">Campaign Workspace</h1>
            <p className="text-sm text-slate-400 mt-1">Import campaigns, analyze rules, and identify the highest-value opportunities.</p>
          </div>
          
          <button 
            onClick={fetchCampaigns} 
            disabled={isLoadingList}
            className="p-2 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded-lg transition-colors disabled:opacity-50"
            title="Refresh Campaigns"
          >
            <RefreshCw className={`w-5 h-5 ${isLoadingList ? 'animate-spin' : ''}`} />
          </button>
        </header>

        {/* SCROLLABLE CONTENT */}
        <div className="flex-1 overflow-y-auto p-8 bg-[#0B0F19]">
          <div className="max-w-7xl mx-auto flex flex-col gap-8 pb-20">
            
            {/* TOP: Import Panel */}
            <section className="w-full lg:w-2/3 xl:w-1/2">
              <CampaignImportCard />
            </section>

            {/* BOTTOM: Grid */}
            <section>
              <h2 className="text-lg font-semibold text-slate-200 mb-2">Campaign Intelligence</h2>
              <CampaignGrid />
            </section>

          </div>
        </div>

        {/* OVERLAYS */}
        {activeCampaignId && (
          <>
            <div 
              className="fixed inset-0 bg-black/40 z-40 transition-opacity backdrop-blur-sm"
              onClick={() => useCampaignStore.getState().setActiveCampaignId(null)}
            />
            <CampaignDetailDrawer />
          </>
        )}
      </main>

    </div>
  );
};

export default CampaignsPage;
