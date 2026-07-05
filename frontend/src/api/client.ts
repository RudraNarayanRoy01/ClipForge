import axios from 'axios';

// Use relative path by default to leverage the Vite dev server proxy
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface ClipUpdatePayload {
  start_time?: number;
  end_time?: number;
  title?: string;
  user_approved?: boolean;
}

export const ProjectService = {
  async getProjects() {
    const response = await apiClient.get('/projects');
    return response.data;
  },
  
  async createProject(name: string) {
    const response = await apiClient.post('/projects', { name });
    return response.data;
  },
  
  async addLocalVideo(projectId: string, filePath: string) {
    const response = await apiClient.post(`/projects/${projectId}/videos/local`, { file_path: filePath });
    return response.data;
  }
};

export const AnalysisService = {
  async triggerAnalysis(videoId: string) {
    const response = await apiClient.post(`/videos/${videoId}/analyze`);
    return response.data;
  }
};

export const ClipService = {
  async getClips(videoId: string) {
    const response = await apiClient.get(`/videos/${videoId}/clips`);
    return response.data;
  },
  
  async updateClip(clipId: string, updates: ClipUpdatePayload) {
    const response = await apiClient.patch(`/clips/${clipId}`, updates);
    return response.data;
  },
  
  async exportClip(clipId: string) {
    const response = await apiClient.post(`/clips/${clipId}/export`);
    return response.data;
  }
};
