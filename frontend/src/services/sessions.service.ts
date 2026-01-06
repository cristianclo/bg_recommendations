import apiClient from '../lib/api-client';
import type { SessionProfile, SessionProfileFormData, PaginatedResponse } from '../types';

export const sessionsService = {
  create: async (data: SessionProfileFormData): Promise<SessionProfile> => {
    const response = await apiClient.post('/sessions', data);
    return response.data;
  },

  getAll: async (params?: {
    skip?: number;
    limit?: number;
    has_warnings?: boolean;
  }): Promise<PaginatedResponse<SessionProfile>> => {
    const response = await apiClient.get('/sessions', { params });
    return response.data;
  },

  getById: async (id: number): Promise<SessionProfile> => {
    const response = await apiClient.get(`/sessions/${id}`);
    return response.data;
  },

  update: async (id: number, data: Partial<SessionProfileFormData>): Promise<SessionProfile> => {
    const response = await apiClient.put(`/sessions/${id}`, data);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`/sessions/${id}`);
  },

  getStatistics: async () => {
    const response = await apiClient.get('/sessions/statistics');
    return response.data;
  },
};

export default sessionsService;
