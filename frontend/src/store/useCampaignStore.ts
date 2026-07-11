import { create } from 'zustand';
import { CampaignService, Campaign } from '../api/campaignClient';

interface CampaignState {
  campaigns: Campaign[];
  activeCampaignId: string | null;
  activeCampaignDetails: Campaign | null;
  isLoadingList: boolean;
  isLoadingDetails: boolean;
  isImporting: boolean;
  importProgressText: string;
  error: string | null;

  // Actions
  fetchCampaigns: () => Promise<void>;
  fetchCampaignDetails: (id: string) => Promise<void>;
  importCampaign: (contentType: string, source: string) => Promise<void>;
  setActiveCampaignId: (id: string | null) => void;
  clearError: () => void;
}

export const useCampaignStore = create<CampaignState>((set, get) => ({
  campaigns: [],
  activeCampaignId: null,
  activeCampaignDetails: null,
  isLoadingList: false,
  isLoadingDetails: false,
  isImporting: false,
  importProgressText: '',
  error: null,

  fetchCampaigns: async () => {
    set({ isLoadingList: true, error: null });
    try {
      const data = await CampaignService.getCampaigns(0, 100);
      set({ campaigns: data.data, isLoadingList: false });
    } catch (err: any) {
      set({ 
        error: err.response?.data?.detail || err.message || 'Failed to fetch campaigns', 
        isLoadingList: false 
      });
    }
  },

  fetchCampaignDetails: async (id: string) => {
    set({ isLoadingDetails: true, error: null, activeCampaignId: id });
    try {
      const data = await CampaignService.getCampaign(id);
      set({ activeCampaignDetails: data, isLoadingDetails: false });
    } catch (err: any) {
      set({ 
        error: err.response?.data?.detail || err.message || 'Failed to fetch campaign details', 
        isLoadingDetails: false 
      });
    }
  },

  importCampaign: async (contentType: string, source: string) => {
    set({ 
      isImporting: true, 
      error: null, 
      importProgressText: 'Initializing import...' 
    });
    
    try {
      // Basic mock progress since we don't have SSE/WebSockets for it yet
      set({ importProgressText: 'Parsing campaign source and analyzing rules...' });
      
      const newCampaign = await CampaignService.importCampaign(contentType, source);
      
      set((state) => ({ 
        campaigns: [newCampaign, ...state.campaigns],
        isImporting: false,
        importProgressText: '',
        activeCampaignId: newCampaign.id,
        activeCampaignDetails: newCampaign
      }));
    } catch (err: any) {
      set({ 
        error: err.response?.data?.detail || err.message || 'Failed to import campaign', 
        isImporting: false,
        importProgressText: ''
      });
    }
  },

  setActiveCampaignId: (id: string | null) => {
    set({ activeCampaignId: id });
    if (!id) {
      set({ activeCampaignDetails: null });
    } else {
      const existing = get().campaigns.find(c => c.id === id);
      if (existing) {
        set({ activeCampaignDetails: existing });
        // Optionally fetch full details in background if we think the list version is truncated
        // get().fetchCampaignDetails(id);
      } else {
        get().fetchCampaignDetails(id);
      }
    }
  },

  clearError: () => set({ error: null })
}));
