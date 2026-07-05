import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { ArrowLeft, Loader2, FolderOpen, Video } from 'lucide-react';
import { Project } from '../components/ProjectCard';
import { VideoUploader } from '../components/VideoUploader';
import { VideoCard } from '../components/VideoCard';

export default function ProjectWorkspace() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [project, setProject] = useState<Project | null>(null);
  const [videos, setVideos] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchProjectAndVideos = async () => {
      try {
        const [projectRes, videosRes] = await Promise.all([
          axios.get(`/api/v1/projects/${id}`),
          axios.get(`/api/v1/projects/${id}/videos`)
        ]);
        setProject(projectRes.data);
        setVideos(videosRes.data);
      } catch (err: any) {
        setError(err.response?.data?.error?.message || err.message || 'Failed to fetch project details');
      } finally {
        setIsLoading(false);
      }
    };
    
    if (id) {
      fetchProjectAndVideos();
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
      
      <main className="flex-1 p-8 max-w-5xl mx-auto w-full">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-[var(--panel)] p-6 rounded-2xl border border-[var(--border)] shadow-xl relative overflow-hidden">
              <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-[var(--accent)] to-transparent opacity-50"></div>
              
              <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                <Video className="text-[var(--accent)]" size={20} />
                Project Videos
              </h2>
              
              {videos.length === 0 ? (
                <div className="text-center py-12 text-gray-500 border border-dashed border-gray-800 rounded-xl bg-black/20">
                  <FolderOpen size={48} className="mx-auto mb-4 opacity-50" />
                  <p>No videos imported yet.</p>
                  <p className="text-sm mt-1">Upload a video to get started.</p>
                </div>
              ) : (
                <div className="space-y-4 max-h-[500px] overflow-y-auto pr-2 custom-scrollbar">
                  {videos.map(video => (
                    <VideoCard 
                      key={video.id} 
                      video={video} 
                      onDelete={(id) => setVideos(prev => prev.filter(v => v.id !== id))} 
                    />
                  ))}
                </div>
              )}
            </div>
          </div>
          
          <div className="lg:col-span-1 space-y-6">
            <div className="bg-[var(--panel)] p-6 rounded-2xl border border-[var(--border)] shadow-xl">
              <h3 className="text-lg font-medium text-white mb-4">Import Video</h3>
              <VideoUploader 
                projectId={project.id} 
                onUploadSuccess={(video) => setVideos(prev => [video, ...prev])} 
              />
            </div>
            
            <div className="bg-black/30 rounded-xl p-6 border border-gray-800/50 backdrop-blur-sm">
              <p className="text-sm font-medium text-blue-300">
                Sprint 2.2 Foundation
              </p>
              <p className="text-xs text-gray-500 mt-2">
                Videos are stored locally. AI processing and timeline generation will be introduced in upcoming sprints.
              </p>
            </div>
          </div>
          
        </div>
      </main>
    </div>
  );
}
