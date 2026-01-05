// Game types
export interface Game {
  id: number;
  name: string;
  description?: string;
  min_players?: number;
  max_players?: number;
  min_age?: number;
  duration_minutes?: number;
  complexity?: number;
  year_published?: number;
  image_url?: string;
  is_active: boolean;
  created_at: string;
  categories: string[];
  mechanics: string[];
}

// User types
export interface User {
  id: number;
  email: string;
  username: string;
  full_name?: string;
  is_active: boolean;
  is_admin: boolean;
  created_at: string;
}

// Recommendation types
export interface Recommendation {
  id: number;
  game_id: number;
  game_name: string;
  score: number;
  explanation: string;
  algorithm_used: string;
  created_at: string;
}

// Rating types
export interface Rating {
  id: number;
  user_id: number;
  game_id: number;
  rating: number;
  review?: string;
  created_at: string;
}

// Feedback types
export interface Feedback {
  id: number;
  recommendation_id: number;
  was_useful: boolean;
  comment?: string;
  created_at: string;
}

// Auth types
export interface LoginCredentials {
  username: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}
