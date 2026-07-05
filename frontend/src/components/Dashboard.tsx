import React, { useEffect, useState } from 'react';
import { useAppStore } from '../store/useAppStore';
import { VideoPlayer } from './VideoPlayer';

export const Dashboard: React.FC = () => {
  const { 
    projects, 
    fetchProjects, 
    createProject, 
    activeVideoId, 
    triggerAnalysis, 
    clips, 
    fetchClips,
    isLoading,
    error
  } = useAppStore();

  const [newProjectName, setNewProjectName] = useState('');
  const [seekTime, setSeekTime] = useState<number | null>(null);

  useEffect(() => {
    fetchProjects();
  }, [fetchProjects]);

  useEffect(() => {
    if (activeVideoId) {
      fetchClips(activeVideoId);
    }
  }, [activeVideoId, fetchClips]);

  const handleCreateProject = () => {
    if (newProjectName.trim()) {
      createProject(newProjectName);
      setNewProjectName('');
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-200 flex flex-col font-sans">
      
      {/* HEADER */}
      <header className="bg-slate-900 border-b border-slate-800 p-4 flex justify-between items-center shadow-md">
        <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-indigo-500 bg-clip-text text-transparent">
          AI Clipping Studio
        </h1>
        <div className="flex gap-4">
          <input 
            type="text" 
            placeholder="New Project Name..." 
            className="px-4 py-2 bg-slate-800 border border-slate-700 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
            value={newProjectName}
            onChange={(e) => setNewProjectName(e.target.value)}
          />
          <button 
            onClick={handleCreateProject}
            disabled={isLoading}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-md font-medium transition-colors disabled:opacity-50"
          >
            Create
          </button>
        </div>
      </header>

      {/* ERROR BANNER */}
      {error && (
        <div className="bg-red-900/50 border-l-4 border-red-500 p-4 m-4 rounded">
          <p className="text-red-200">{error}</p>
        </div>
      )}

      {/* MAIN CONTENT */}
      <main className="flex-1 flex overflow-hidden p-4 gap-6">
        
        {/* LEFT PANEL: PROJECTS & CLIPS */}
        <aside className="w-1/3 flex flex-col gap-6 overflow-y-auto pr-2">
          
          {/* Projects List */}
          <section className="bg-slate-900 rounded-xl border border-slate-800 p-4 shadow-lg">
            <h2 className="text-lg font-semibold mb-4 text-slate-300 border-b border-slate-800 pb-2">Projects</h2>
            {projects.length === 0 ? (
              <p className="text-slate-500 text-sm">No projects found. Create one above.</p>
            ) : (
              <ul className="space-y-2">
                {projects.map((p) => (
                  <li key={p.id} className="p-3 bg-slate-800 hover:bg-slate-700 rounded-lg cursor-pointer transition-colors border border-slate-700">
                    <p className="font-medium text-slate-200">{p.name}</p>
                    <p className="text-xs text-slate-500 mt-1">Status: {p.status}</p>
                  </li>
                ))}
              </ul>
            )}
          </section>

          {/* AI Clips List */}
          <section className="bg-slate-900 rounded-xl border border-slate-800 p-4 shadow-lg flex-1">
            <div className="flex justify-between items-center mb-4 border-b border-slate-800 pb-2">
              <h2 className="text-lg font-semibold text-slate-300">Generated Clips</h2>
              <button 
                onClick={() => activeVideoId && triggerAnalysis(activeVideoId)}
                disabled={!activeVideoId || isLoading}
                className="px-3 py-1 bg-emerald-600 hover:bg-emerald-700 text-white text-sm rounded transition-colors disabled:opacity-50"
              >
                Analyze Video
              </button>
            </div>
            
            {clips.length === 0 ? (
              <p className="text-slate-500 text-sm">Select a video and run analysis to generate viral clips.</p>
            ) : (
              <div className="space-y-3">
                {clips.map((clip) => (
                  <div 
                    key={clip.id} 
                    className="p-3 bg-slate-800 border border-slate-700 rounded-lg cursor-pointer hover:border-indigo-500 transition-colors group"
                    onClick={() => setSeekTime(clip.start_time)}
                  >
                    <div className="flex justify-between items-start">
                      <h3 className="font-semibold text-slate-200 group-hover:text-indigo-400">{clip.title}</h3>
                      <span className="bg-indigo-900 text-indigo-300 text-xs px-2 py-1 rounded-full border border-indigo-700">
                        Score: {clip.virality_score}
                      </span>
                    </div>
                    <p className="text-sm text-slate-400 mt-2 italic">"{clip.hook_text}"</p>
                    <div className="mt-3 flex gap-2">
                      {clip.hashtags.map((tag: string) => (
                        <span key={tag} className="text-xs text-slate-500">#{tag}</span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>
        </aside>

        {/* RIGHT PANEL: VIDEO PLAYER */}
        <section className="flex-1 flex flex-col">
          <div className="flex-1 bg-slate-900 rounded-xl border border-slate-800 p-2 shadow-lg flex items-center justify-center">
             {/* We mock the video URL for UI design purposes until the backend serves it */}
            <VideoPlayer 
              videoUrl={activeVideoId ? `blob:http://localhost:5173/${activeVideoId}` : null} 
              seekToTime={seekTime} 
            />
          </div>
        </section>
        
      </main>
    </div>
  );
};
