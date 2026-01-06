import apiClient from '../lib/api-client';
import type { Skill, PaginatedResponse } from '../types';

export const skillsService = {
  getAll: async (params?: {
    page?: number;
    page_size?: number;
    category?: string;
    parent_id?: string;
  }): Promise<Skill[]> => {
    const response = await apiClient.get('/skills', { params });
    return response.data;
  },

  getById: async (id: string): Promise<Skill> => {
    const response = await apiClient.get(`/skills/${id}`);
    return response.data;
  },

  getTree: async (params?: {
    root_id?: string;
  }): Promise<Skill[]> => {
    const response = await apiClient.get('/skills/tree', { params });
    return response.data;
  },

  getAncestors: async (skillId: string): Promise<Skill[]> => {
    const response = await apiClient.get(`/skills/${skillId}/ancestors`);
    return response.data;
  },

  getDescendants: async (skillId: string): Promise<Skill[]> => {
    const response = await apiClient.get(`/skills/${skillId}/descendants`);
    return response.data;
  },
};

export default skillsService;
