import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { ArrowLeft, Loader2, FolderOpen } from 'lucide-react';
import { Project } from '../components/ProjectCard';

export default function ProjectWorkspace() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [project, setProject] = useState<Project | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchProject = async () => {
      try {
        const res = await axios.get(`/api/v1/projects/${id}`);
        setProject(res.data);
      } catch (err: any) {
        setError(err.response?.data?.error?.message || err.message || 'Failed to fetch project');
      } finally {
        setIsLoading(false);
      }
    };
    
    if (id) {
      fetchProject();
    }
  }, [id]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[var(--background)] flex flex-col items-center justify-center text-gray-400">
        <Loader2 size={40} className="animate-spin mb-4 text-[var(--accent)]" />
        <p>Loading workspace...</p>
      </div>
    );
  }

  if (error || !project) {
    return (
      <div className="min-h-screen bg-[var(--background)] flex flex-col items-center justify-center p-8">
        <div className="bg-red-900/20 border border-red-500/30 text-red-400 p-8 rounded-xl max-w-lg w-full text-center">
          <h2 className="text-xl font-bold mb-2">Error Loading Project</h2>
          <p className="mb-6">{error || 'Project not found'}</p>
          <button 
            onClick={() => navigate('/projects')}
            className="px-6 py-2 bg-red-900/40 text-red-200 hover:bg-red-900/60 rounded-md transition-colors inline-flex items-center gap-2"
          >
            <ArrowLeft size={16} />
            Back to Projects
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[var(--background)] flex flex-col">
      <header className="border-b border-[var(--border)] bg-[var(--panel)] p-4 flex items-center gap-4 sticky top-0 z-10 shadow-sm">
        <button 
          onClick={() => navigate('/projects')}
          className="p-2 text-gray-400 hover:text-white hover:bg-black/20 rounded-lg transition-colors"
          title="Back to Projects"
        >
          <ArrowLeft size={20} />
        </button>
        <div>
          <h1 className="text-xl font-bold text-white truncate">{project.name}</h1>
          <div className="flex items-center gap-2 text-xs text-gray-400 mt-1">
            <span className="px-1.5 py-0.5 rounded bg-black/40 border border-gray-700 uppercase">{project.status}</span>
            <span>{project.video_count} Videos</span>
            <span>Created {new Date(project.created_at).toLocaleDateString()}</span>
          </div>
        </div>
      </header>
      
      <main className="flex-1 flex items-center justify-center p-8">
        <div className="bg-[var(--panel)] p-10 rounded-2xl border border-[var(--border)] max-w-2xl w-full text-center shadow-2xl relative overflow-hidden">
          
          <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-[var(--accent)] to-transparent opacity-50"></div>
          
          <div className="w-20 h-20 bg-black/40 rounded-2xl border border-[var(--border)] flex items-center justify-center mx-auto mb-6 shadow-inner text-[var(--accent)]">
            <FolderOpen size={40} />
          </div>
          
          <h2 className="text-3xl font-bold text-white mb-2">{project.name}</h2>
          {project.description && (
            <p className="text-gray-400 mb-8 max-w-md mx-auto">{project.description}</p>
          )}
          
          <div className="bg-black/30 rounded-xl p-6 mb-8 border border-gray-800/50 backdrop-blur-sm inline-block">
            <p className="text-lg font-medium text-blue-300">
              This workspace will be expanded in Sprint 2.2.
            </p>
            <p className="text-sm text-gray-500 mt-2">
              Future updates will include video uploading, AI multimodal analysis, and timeline editing.
            </p>
          </div>
          
        </div>
      </main>
    </div>
  );
}
