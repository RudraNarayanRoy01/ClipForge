import React from 'react';
import { useCampaignStore } from '../../store/useCampaignStore';
import { X, ChevronDown, ChevronRight, Activity, TrendingUp, AlertTriangle, ShieldAlert } from 'lucide-react';

const ScoreRing: React.FC<{ score: number, label: string, color: string }> = ({ score, label, color }) => {
  const radius = 16;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;

  return (
    <div className="flex flex-col items-center">
      <div className="relative w-12 h-12 flex items-center justify-center">
        <svg className="w-12 h-12 transform -rotate-90">
          <circle cx="24" cy="24" r={radius} className="stroke-slate-800 fill-none" strokeWidth="4" />
          <circle
            cx="24"
            cy="24"
            r={radius}
            className={`fill-none ${color}`}
            strokeWidth="4"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
          />
        </svg>
        <span className="absolute text-xs font-bold text-slate-200">{score}</span>
      </div>
      <span className="text-[10px] text-slate-400 mt-1 uppercase tracking-wider">{label}</span>
    </div>
  );
};

export const CampaignDetailDrawer: React.FC = () => {
  const { activeCampaignDetails, activeCampaignId, setActiveCampaignId, isLoadingDetails } = useCampaignStore();
  const [showRaw, setShowRaw] = React.useState(false);

  if (!activeCampaignId) return null;

  const handleClose = () => setActiveCampaignId(null);

  return (
    <div className={`fixed inset-y-0 right-0 w-full max-w-xl bg-slate-950 border-l border-slate-800 shadow-2xl flex flex-col z-50 transform transition-transform duration-300 ease-in-out`}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-slate-800 bg-slate-900/50">
        <h2 className="text-lg font-semibold text-slate-200 line-clamp-1 pr-4">
          {activeCampaignDetails?.title || 'Loading Campaign...'}
        </h2>
        <button onClick={handleClose} className="p-2 hover:bg-slate-800 rounded-full text-slate-400 hover:text-slate-200 transition-colors">
          <X className="w-5 h-5" />
        </button>
      </div>

      {isLoadingDetails && !activeCampaignDetails ? (
        <div className="flex-1 flex items-center justify-center">
          <div className="animate-pulse flex flex-col items-center gap-4 text-slate-500">
            <Activity className="w-8 h-8 animate-spin" />
            <p>Loading Intelligence...</p>
          </div>
        </div>
      ) : activeCampaignDetails ? (
        <div className="flex-1 overflow-y-auto p-6 space-y-8">
          
          {/* Worth It Score Section */}
          <section className="bg-slate-900 rounded-xl p-5 border border-slate-800">
            <h3 className="text-sm font-semibold text-slate-300 mb-4 flex items-center gap-2 uppercase tracking-wider">
              <TrendingUp className="w-4 h-4 text-indigo-400" /> Worth-It Analysis
            </h3>
            
            {activeCampaignDetails.worth_it_score ? (
              <div className="flex justify-between items-center px-2">
                <ScoreRing score={activeCampaignDetails.worth_it_score.overall_score} label="Overall" color="stroke-indigo-500" />
                <ScoreRing score={activeCampaignDetails.worth_it_score.estimated_roi} label="ROI" color="stroke-emerald-500" />
                <ScoreRing score={activeCampaignDetails.worth_it_score.estimated_effort} label="Effort" color="stroke-amber-500" />
                <ScoreRing score={activeCampaignDetails.worth_it_score.submission_risk} label="Risk" color="stroke-rose-500" />
              </div>
            ) : (
              <p className="text-sm text-slate-500 italic">Score not generated.</p>
            )}
          </section>

          {/* Summary Section */}
          {activeCampaignDetails.summary && (
            <section className="space-y-4">
              <div>
                <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">About</h3>
                <p className="text-sm text-slate-300 leading-relaxed bg-slate-900/50 p-3 rounded-lg border border-slate-800/50">
                  {activeCampaignDetails.summary.about}
                </p>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Requirements</h3>
                  <p className="text-sm text-slate-300 leading-relaxed bg-slate-900/50 p-3 rounded-lg border border-slate-800/50">
                    {activeCampaignDetails.summary.requirements}
                  </p>
                </div>
                <div>
                  <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Restrictions</h3>
                  <p className="text-sm text-slate-300 leading-relaxed bg-slate-900/50 p-3 rounded-lg border border-slate-800/50">
                    {activeCampaignDetails.summary.restrictions}
                  </p>
                </div>
              </div>

              <div>
                <h3 className="text-xs font-semibold text-rose-500 uppercase tracking-wider mb-2 flex items-center gap-1">
                  <ShieldAlert className="w-3 h-3" /> Main Risks
                </h3>
                <p className="text-sm text-rose-200/80 leading-relaxed bg-rose-950/20 p-3 rounded-lg border border-rose-900/30">
                  {activeCampaignDetails.summary.main_risks}
                </p>
              </div>
            </section>
          )}

          {/* Rules Breakdown */}
          {activeCampaignDetails.rules && (
            <section className="bg-slate-900/50 rounded-xl p-5 border border-slate-800 space-y-4">
              <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider border-b border-slate-800 pb-2">Technical Rules</h3>
              
              <div className="grid grid-cols-2 gap-y-3 gap-x-4 text-sm">
                <div className="text-slate-500">Duration:</div>
                <div className="text-slate-300 font-medium">
                  {activeCampaignDetails.rules.video_duration_min || 0}s - {activeCampaignDetails.rules.video_duration_max || 'Uncapped'}s
                </div>
                
                <div className="text-slate-500">Aspect Ratio:</div>
                <div className="text-slate-300 font-medium">{activeCampaignDetails.rules.aspect_ratio || 'Any'}</div>
                
                <div className="text-slate-500">Resolution:</div>
                <div className="text-slate-300 font-medium">{activeCampaignDetails.rules.resolution_requirements || 'Any'}</div>
                
                <div className="text-slate-500">Hashtags:</div>
                <div className="text-slate-300 font-medium flex flex-wrap gap-1">
                  {activeCampaignDetails.rules.hashtags.length > 0 ? (
                    activeCampaignDetails.rules.hashtags.map(t => <span key={t} className="bg-slate-800 px-1.5 py-0.5 rounded text-xs">#{t}</span>)
                  ) : 'None'}
                </div>
                
                <div className="text-slate-500">Audio:</div>
                <div className="text-slate-300 font-medium">{activeCampaignDetails.rules.required_audio || 'Any'}</div>
              </div>

              {activeCampaignDetails.rules.rejection_reasons?.length > 0 && (
                <div className="mt-4 pt-4 border-t border-slate-800">
                  <h4 className="text-xs font-semibold text-amber-500 mb-2 flex items-center gap-1">
                    <AlertTriangle className="w-3 h-3" /> Rejection Triggers
                  </h4>
                  <ul className="list-disc pl-4 text-xs text-amber-200/70 space-y-1">
                    {activeCampaignDetails.rules.rejection_reasons.map((r, i) => <li key={i}>{r}</li>)}
                  </ul>
                </div>
              )}
            </section>
          )}

          {/* Raw Content Collapsible */}
          <section className="border border-slate-800 rounded-xl overflow-hidden bg-slate-900/30">
            <button 
              onClick={() => setShowRaw(!showRaw)}
              className="w-full flex items-center justify-between p-4 text-sm font-medium text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 transition-colors"
            >
              <span>View Raw Source Content</span>
              {showRaw ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
            </button>
            
            {showRaw && (
              <div className="p-4 border-t border-slate-800 bg-slate-950">
                <pre className="text-[10px] text-slate-500 whitespace-pre-wrap font-mono max-h-64 overflow-y-auto">
                  {activeCampaignDetails.source}
                </pre>
              </div>
            )}
          </section>

        </div>
      ) : null}
    </div>
  );
};
