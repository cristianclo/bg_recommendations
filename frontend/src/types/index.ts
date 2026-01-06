// Game Types
export interface Game {
  id: number;
  name: string;
  bgg_id: number;
  duration_min: number;
  complexity: number;
  min_players: number;
  max_players: number;
  mechanics: string[];
  language_dependency: 'ninguna' | 'baja' | 'media' | 'alta';
  bgg_rank: number | null;
  description: string | null;
  image_url: string | null;
  year_published: number | null;
  available: boolean;
  has_partial_data: boolean;
  created_at: string;
  updated_at: string;
}

// Session Profile Types
export interface SessionProfile {
  id: number;
  session_name: string | null;
  objectives: string[];
  primary_skill_name: string;
  secondary_skill_name: string | null;
  available_time_min: number;
  group_size: number;
  max_language_dependency: 'ninguna' | 'baja' | 'media' | 'alta';
  preferred_modality: 'competitive' | 'cooperative' | 'any';
  additional_constraints: Record<string, any> | null;
  notes: string | null;
  validation_warnings: ValidationWarning[];
  has_warnings: boolean;
  created_at: string;
  updated_at: string;
}

export interface ValidationWarning {
  severity: 'low' | 'medium' | 'high';
  category: 'operational' | 'pedagogical';
  code: string;
  message: string;
  suggestions: string[];
}

// Skill Types
export interface Skill {
  id: string;
  name: string;
  definition: string;
  category: string;
  examples: string[];
  contexts: string;
  parent_id: string | null;
  level: number;
  games_count: number;
  created_at: string;
  updated_at: string;
  children?: Skill[];
  path?: string;
}

// Recommendation Types
export interface Recommendation {
  id: number;
  session_profile_id: number;
  game_id: number;
  rank: number;
  total_score: number;
  skill_score: number;
  mechanics_score: number;
  difficulty_score: number;
  ranking_score: number;
  feedback_boost: number;
  weights_used: Record<string, number>;
  explanation_text: string | null;
  match_reasons: Record<string, any> | null;
  created_at: string;
  // Feedback fields
  was_used: boolean | null;
  user_feedback_score: number | null;
  feedback_asesor: string | null;
  skill_actually_worked: string | null;
  what_worked_well: string | null;
  what_didnt_work: string | null;
  additional_notes: string | null;
  feedback_date: string | null;
  can_edit_until: string | null;
  // Relations
  game?: Game;
}

export interface RecommendationRequest {
  session_profile_id: number;
  top_n?: number;
  config_name?: string;
}

// Scoring Config Types
export interface ScoringConfig {
  id: number;
  name: string;
  description: string | null;
  skill_weight: number;
  mechanics_weight: number;
  difficulty_weight: number;
  ranking_weight: number;
  is_active: boolean;
  is_default: boolean;
  created_at: string;
  updated_at: string;
}

// API Response Types
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  skip: number;
  limit: number;
}

export interface ApiError {
  detail: string;
  status_code: number;
}

// Form Types
export interface SessionProfileFormData {
  session_name?: string;
  objectives: string[];
  primary_skill_id: string;
  secondary_skill_ids?: string[];
  available_time_min: number;
  group_size: number;
  max_language_dependency: 'ninguna' | 'baja' | 'media' | 'alta';
  preferred_modality?: 'competitive' | 'cooperative' | 'any';
  notes?: string | null;
}

export interface FeedbackFormData {
  was_used: boolean;
  user_feedback_score: number;
  feedback_asesor: string;
  skill_actually_worked?: string;
  what_worked_well?: string;
  what_didnt_work?: string;
  additional_notes?: string;
}
