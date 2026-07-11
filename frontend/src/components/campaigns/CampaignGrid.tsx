import React from 'react';
import { Campaign } from '../../api/campaignClient';
import { useCampaignStore } from '../../store/useCampaignStore';
import { DollarSign, Calendar, TrendingUp } from 'lucide-react';

const StatusBadge: React.FC<{ status: string }> = ({ status }) => {
  const styles: Record<string, string> = {
    IMPORTED: 'bg-slate-800 text-slate-300 border-slate-700',
    PROCESSING: 'bg-indigo-900/50 text-indigo-300 border-indigo-700 animate-pulse',
    PROCESSED: 'bg-emerald-900/50 text-emerald-300 border-emerald-700',
    FAILED: 'bg-rose-900/50 text-rose-300 border-rose-700',
    ARCHIVED: 'bg-slate-800 text-slate-500 border-slate-700',
  };

  const style = styles[status] || styles.IMPORTED;
  
  return (
    <span className={`text-[10px] font-medium px-2 py-0.5 rounded-full border uppercase tracking-wider ${style}`}>
      {status}
    </span>
  );
};

const CampaignCard: React.FC<{ campaign: Campaign }> = ({ campaign }) => {
  const { activeCampaignId, setActiveCampaignId } = useCampaignStore();
  const isActive = activeCampaignId === campaign.id;
  const score = campaign.worth_it_score?.overall_score || 0;

  return (
    <div 
      onClick={() => setActiveCampaignId(campaign.id)}
      className={`relative p-4 rounded-xl cursor-pointer transition-all duration-200 border group
        ${isActive 
          ? 'bg-slate-800 border-indigo-500 shadow-md shadow-indigo-900/20' 
          : 'bg-slate-900 border-slate-800 hover:border-slate-600 hover:bg-slate-800/80'
        }
      `}
    >
      <div className="flex justify-between items-start mb-3">
        <h3 className="font-semibold text-slate-200 line-clamp-2 text-sm leading-tight pr-2 group-hover:text-indigo-400 transition-colors">
          {campaign.title || 'Untitled Campaign'}
        </h3>
        <StatusBadge status={campaign.status} />
      </div>

      <div className="flex flex-wrap items-center gap-x-4 gap-y-2 text-xs text-slate-400 mb-4">
        {campaign.brand && (
          <span className="flex items-center gap-1 font-medium text-slate-300 bg-slate-950 px-2 py-0.5 rounded-md border border-slate-800">
            {campaign.brand}
          </span>
        )}
        <span className="flex items-center gap-1">
          <DollarSign className="w-3.5 h-3.5" />
          {campaign.payout || 'TBD'}
        </span>
        <span className="flex items-center gap-1">
          <Calendar className="w-3.5 h-3.5" />
          {campaign.deadline ? new Date(campaign.deadline).toLocaleDateString() : 'No deadline'}
        </span>
      </div>

      <div className="flex items-center justify-between border-t border-slate-800 pt-3 mt-auto">
        <div className="flex items-center gap-2">
          <div className="text-xs text-slate-500">Worth-It Score</div>
          <div className="flex items-center gap-1 font-mono font-semibold text-emerald-400">
            <TrendingUp className="w-3.5 h-3.5" />
            {score > 0 ? score : '--'}
          </div>
        </div>
        
        {campaign.confidence_score > 0 && (
          <div className="text-[10px] text-slate-500" title="AI Confidence">
            {(campaign.confidence_score * 100).toFixed(0)}% Conf.
          </div>
        )}
      </div>
    </div>
  );
};

export const CampaignGrid: React.FC = () => {
  const { campaigns, isLoadingList } = useCampaignStore();

  if (isLoadingList && campaigns.length === 0) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 mt-6">
        {[...Array(8)].map((_, i) => (
          <div key={i} className="bg-slate-900 border border-slate-800 rounded-xl p-4 h-40 animate-pulse">
            <div className="h-4 bg-slate-800 rounded w-3/4 mb-4"></div>
            <div className="h-3 bg-slate-800 rounded w-1/4 mb-8"></div>
            <div className="h-3 bg-slate-800 rounded w-full mb-2"></div>
            <div className="h-3 bg-slate-800 rounded w-2/3"></div>
          </div>
        ))}
      </div>
    );
  }

  if (campaigns.length === 0) {
    return (
      <div className="mt-6 border-2 border-dashed border-slate-800 rounded-xl p-12 text-center">
        <div className="text-slate-500 mb-2">No campaigns found.</div>
        <p className="text-slate-600 text-sm">Import your first campaign above to get started.</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 mt-6">
      {campaigns.map(c => (
        <CampaignCard key={c.id} campaign={c} />
      ))}
    </div>
  );
};
