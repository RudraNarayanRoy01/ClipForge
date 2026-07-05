import { useState, useEffect } from 'react';
import axios from 'axios';
import { Plus, Loader2 } from 'lucide-react';
import EmptyState from '../components/EmptyState';
import ProjectCard, { Project } from '../components/ProjectCard';
import CreateProjectDialog from '../components/CreateProjectDialog';

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [isCreateOpen, setIsCreateOpen] = useState(false);

  const fetchProjects = async () => {
    setIsLoading(true);
    setError('');
    try {
      const res = await axios.get('/api/v1/projects/');
      setProjects(res.data.data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch projects');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  const handleDelete = async (id: string) => {
    try {
      await axios.delete(`/api/v1/projects/${id}`);
      setProjects(projects.filter(p => p.id !== id));
    } catch (err: any) {
      setError('Failed to delete project: ' + (err.response?.data?.error?.message || err.message));
    }
  };

  const handleProjectCreated = () => {
    setIsCreateOpen(false);
    fetchProjects();
  };

  return (
    <div className="min-h-screen bg-[var(--background)] p-8">
      <div className="max-w-7xl mx-auto">
        
        <header className="flex justify-between items-end mb-8">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">Projects</h1>
            <p className="text-gray-400">Manage your video clipping workspaces</p>
          </div>
          
          <button 
            onClick={() => setIsCreateOpen(true)}
            className="px-5 py-2.5 bg-[var(--accent)] text-white font-medium rounded-lg hover:bg-opacity-90 transition-all active:scale-95 flex items-center gap-2"
          >
            <Plus size={20} />
            New Project
          </button>
        </header>

        {isLoading ? (
          <div className="flex flex-col items-center justify-center py-20 text-gray-400">
            <Loader2 size={40} className="animate-spin mb-4 text-[var(--accent)]" />
            <p>Loading projects...</p>
          </div>
        ) : error ? (
          <div className="bg-red-900/20 border border-red-500/30 text-red-400 p-6 rounded-xl text-center">
            <p className="mb-4">{error}</p>
            <button 
              onClick={fetchProjects}
              className="px-4 py-2 bg-red-900/40 text-red-200 hover:bg-red-900/60 rounded-md transition-colors"
            >
              Try Again
            </button>
          </div>
        ) : projects.length === 0 ? (
          <EmptyState onCreateClick={() => setIsCreateOpen(true)} />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {projects.map(project => (
              <ProjectCard 
                key={project.id} 
                project={project} 
                onDelete={handleDelete} 
              />
            ))}
          </div>
        )}

      </div>

      {isCreateOpen && (
        <CreateProjectDialog 
          onClose={() => setIsCreateOpen(false)} 
          onSuccess={handleProjectCreated} 
        />
      )}
    </div>
  );
}
