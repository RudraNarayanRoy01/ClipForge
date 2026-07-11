import { apiClient } from './client';

export interface CampaignRules {
  allowed_regions: string[];
  video_duration_min?: number;
  video_duration_max?: number;
  aspect_ratio?: string;
  resolution_requirements?: string;
  caption_requirements?: string;
  hashtags: string[];
  required_audio?: string;
  content_restrictions: string[];
  rejection_reasons: string[];
  additional_notes?: string;
}

export interface CampaignSummary {
  about: string;
  requirements: string;
  restrictions: string;
  main_risks: string;
  deadline?: string;
  payout?: string;
}

export interface WorthItScore {
  estimated_roi: number;
  estimated_effort: number;
  campaign_complexity: number;
  submission_risk: number;
  overall_score: number;
}

export interface Campaign {
  id: string;
  title: string;
  source: string;
  brand: string;
  campaign_url: string;
  platforms: string[];
  deadline?: string;
  payout: string;
  reward_type: string;
  status: 'IMPORTED' | 'PROCESSING' | 'PROCESSED' | 'FAILED' | 'ARCHIVED';
  confidence_score: number;
  created_at: string;
  
  rules?: CampaignRules;
  summary?: CampaignSummary;
  worth_it_score?: WorthItScore;
}

export interface CampaignListResponse {
  data: Campaign[];
  meta: {
    total_count: number;
    skip: number;
    limit: number;
  }
}

export const CampaignService = {
  async importCampaign(contentType: string, source: string): Promise<Campaign> {
    const response = await apiClient.post<Campaign>('/campaigns/import', {
      content_type: contentType,
      source: source
    });
    return response.data;
  },
  
  async getCampaigns(skip: number = 0, limit: number = 50): Promise<CampaignListResponse> {
    const response = await apiClient.get<CampaignListResponse>('/campaigns', {
      params: { skip, limit }
    });
    return response.data;
  },
  
  async getCampaign(id: string): Promise<Campaign> {
    const response = await apiClient.get<Campaign>(`/campaigns/${id}`);
    return response.data;
  }
};
