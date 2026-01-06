import apiClient from '../lib/api-client';
import type { Recommendation, RecommendationRequest, FeedbackFormData } from '../types';

export const recommendationsService = {
  generate: async (data: RecommendationRequest): Promise<Recommendation[]> => {
    const response = await apiClient.post('/recommendations/generate', data);
    return response.data;
  },

  getById: async (id: number): Promise<Recommendation> => {
    const response = await apiClient.get(`/recommendations/${id}`);
    return response.data;
  },

  getBySession: async (sessionId: number): Promise<Recommendation[]> => {
    const response = await apiClient.get(`/recommendations/session/${sessionId}`);
    return response.data;
  },

  submitFeedback: async (id: number, data: FeedbackFormData): Promise<Recommendation> => {
    const response = await apiClient.post(`/recommendations/${id}/feedback`, data);
    return response.data;
  },

  updateFeedback: async (id: number, data: FeedbackFormData): Promise<Recommendation> => {
    const response = await apiClient.put(`/recommendations/${id}/feedback`, data);
    return response.data;
  },
};

export default recommendationsService;
