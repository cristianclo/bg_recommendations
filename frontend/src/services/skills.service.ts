import apiClient from '../lib/api-client';
import type { Skill, PaginatedResponse } from '../types';

export const skillsService = {
  getAll: async (params?: {
    skip?: number;
    limit?: number;
    root_only?: boolean;
    parent_id?: number;
    search?: string;
    active_only?: boolean;
  }): Promise<PaginatedResponse<Skill>> => {
    const response = await apiClient.get('/skills', { params });
    return response.data;
  },

  getById: async (id: number): Promise<Skill> => {
    const response = await apiClient.get(`/skills/${id}`);
    return response.data;
  },

  getTree: async (params?: {
    root_id?: number;
    active_only?: boolean;
  }): Promise<Skill[]> => {
    const response = await apiClient.get('/skills/tree', { params });
    return response.data;
  },

  getGamesForSkill: async (skillId: number, params?: {
    skip?: number;
    limit?: number;
  }): Promise<PaginatedResponse<any>> => {
    const response = await apiClient.get(`/skills/${skillId}/games`, { params });
    return response.data;
  },
};

export default skillsService;
