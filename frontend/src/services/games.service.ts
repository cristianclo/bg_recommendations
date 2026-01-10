import apiClient from '../lib/api-client';
import type { Game, PaginatedResponse } from '../types';

export const gamesService = {
  getAll: async (params?: {
    skip?: number;
    limit?: number;
    available?: boolean;
    min_players?: number;
    max_players?: number;
    min_duration?: number;
    max_duration?: number;
    min_complexity?: number;
    max_complexity?: number;
    mechanics?: string[];
    search?: string;
    name?: string;  // Add name parameter for searching by name
  }): Promise<PaginatedResponse<Game>> => {
    const response = await apiClient.get('/games', { params });
    return response.data;
  },

  getById: async (id: number): Promise<Game> => {
    const response = await apiClient.get(`/games/${id}`);
    return response.data;
  },

  getStatistics: async () => {
    const response = await apiClient.get('/games/statistics');
    return response.data;
  },
};

export default gamesService;
