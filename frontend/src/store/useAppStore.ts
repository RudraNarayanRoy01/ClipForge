import { create } from 'zustand';
import { ProjectService, AnalysisService, ClipService } from '../api/client';

interface AppState {
  projects: any[];
  currentProjectId: string | null;
  activeVideoId: string | null;
  clips: any[];
  isLoading: boolean;
  error: string | null;
  
  // Actions
  fetchProjects: () => Promise<void>;
  createProject: (name: string) => Promise<void>;
  setActiveVideo: (videoId: string) => void;
  triggerAnalysis: (videoId: string) => Promise<void>;
  fetchClips: (videoId: string) => Promise<void>;
}

export const useAppStore = create<AppState>((set) => ({
  projects: [],
  currentProjectId: null,
  activeVideoId: null,
  clips: [],
  isLoading: false,
  error: null,

  fetchProjects: async () => {
    set({ isLoading: true, error: null });
    try {
      const data = await ProjectService.getProjects();
      set({ projects: data.data, isLoading: false });
    } catch (err: any) {
      set({ error: err.message, isLoading: false });
    }
  },

  createProject: async (name: string) => {
    set({ isLoading: true, error: null });
    try {
      const project = await ProjectService.createProject(name);
      set((state) => ({ 
        projects: [...state.projects, project],
        currentProjectId: project.id,
        isLoading: false 
      }));
    } catch (err: any) {
      set({ error: err.message, isLoading: false });
    }
  },

  setActiveVideo: (videoId: string) => {
    set({ activeVideoId: videoId });
  },

  triggerAnalysis: async (videoId: string) => {
    set({ isLoading: true, error: null });
    try {
      await AnalysisService.triggerAnalysis(videoId);
      // In a real app, we would open a WebSocket here to listen for progress
      set({ isLoading: false });
    } catch (err: any) {
      set({ error: err.message, isLoading: false });
    }
  },

  fetchClips: async (videoId: string) => {
    set({ isLoading: true, error: null });
    try {
      const data = await ClipService.getClips(videoId);
      set({ clips: data.data, isLoading: false });
    } catch (err: any) {
      set({ error: err.message, isLoading: false });
    }
  }
}));
