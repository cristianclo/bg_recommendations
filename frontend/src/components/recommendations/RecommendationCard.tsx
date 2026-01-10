import React, { useState } from 'react';
import type { Recommendation } from '../../types';
import { GameCard } from '../games/GameCard';
import { ChevronDown, ChevronUp, Star } from 'lucide-react';

interface RecommendationCardProps {
  recommendation: Recommendation;
  rank: number;
  onFeedback?: (recommendation: Recommendation) => void;
}

export const RecommendationCard: React.FC<RecommendationCardProps> = ({
  recommendation,
  rank,
  onFeedback,
}) => {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!recommendation.game) return null;

  const scorePercentage = (recommendation.total_score * 100).toFixed(0);
  const scoreColor = 
    recommendation.total_score >= 0.8 ? 'bg-green-500' :
    recommendation.total_score >= 0.6 ? 'bg-blue-500' :
    recommendation.total_score >= 0.4 ? 'bg-yellow-500' :
    'bg-orange-500';

  return (
    <div className="bg-white rounded-lg shadow-md border border-gray-200 overflow-hidden">
      {/* Rank Badge */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 px-4 py-2 flex items-center justify-between">
        <div className="flex items-center">
          <span className="text-2xl font-bold text-white">#{rank}</span>
          <div className="ml-4">
            <div className="text-white text-sm font-medium">Puntuación</div>
            <div className="flex items-center mt-1">
              <div className="w-32 h-2 bg-white/30 rounded-full overflow-hidden">
                <div 
                  className={`h-full ${scoreColor} transition-all`}
                  style={{ width: `${scorePercentage}%` }}
                />
              </div>
              <span className="ml-2 text-white font-bold">{scorePercentage}%</span>
            </div>
          </div>
        </div>
        {onFeedback && (
          <button
            onClick={() => onFeedback(recommendation)}
            className="px-4 py-2 bg-white text-blue-700 rounded-md text-sm font-medium hover:bg-blue-50 transition-colors"
          >
            Dar Feedback
          </button>
        )}
      </div>

      {/* Game Info */}
      <div className="p-4">
        <GameCard game={recommendation.game} showDetails={true} />

        {/* Score Breakdown */}
        <div className="mt-4 grid grid-cols-2 gap-3">
          <div className="bg-gray-50 rounded p-3">
            <div className="text-xs text-gray-500">Habilidades</div>
            <div className="text-lg font-semibold text-gray-900">
              {(recommendation.skill_score * 100).toFixed(0)}%
            </div>
          </div>
          <div className="bg-gray-50 rounded p-3">
            <div className="text-xs text-gray-500">Mecánicas</div>
            <div className="text-lg font-semibold text-gray-900">
              {(recommendation.mechanics_score * 100).toFixed(0)}%
            </div>
          </div>
          <div className="bg-gray-50 rounded p-3">
            <div className="text-xs text-gray-500">Dificultad</div>
            <div className="text-lg font-semibold text-gray-900">
              {(recommendation.difficulty_score * 100).toFixed(0)}%
            </div>
          </div>
          <div className="bg-gray-50 rounded p-3">
            <div className="text-xs text-gray-500">Ranking</div>
            <div className="text-lg font-semibold text-gray-900">
              {(recommendation.ranking_score * 100).toFixed(0)}%
            </div>
          </div>
        </div>

        {/* Explanation Toggle */}
        {recommendation.explanation_text && (
          <div className="mt-4">
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="w-full flex items-center justify-between px-4 py-2 bg-gray-50 hover:bg-gray-100 rounded-md transition-colors"
            >
              <span className="font-medium text-gray-900">
                {isExpanded ? 'Ocultar' : 'Ver'} explicación detallada
              </span>
              {isExpanded ? (
                <ChevronUp className="h-5 w-5 text-gray-500" />
              ) : (
                <ChevronDown className="h-5 w-5 text-gray-500" />
              )}
            </button>
            
            {isExpanded && (
              <div className="mt-3 p-4 bg-blue-50 rounded-md">
                <p className="text-sm text-gray-700 whitespace-pre-line">
                  {recommendation.explanation_text}
                </p>
              </div>
            )}
          </div>
        )}

        {/* Feedback Boost Indicator */}
        {recommendation.feedback_boost > 0 && (
          <div className="mt-3 flex items-center text-sm text-green-700 bg-green-50 px-3 py-2 rounded">
            <Star className="h-4 w-4 mr-2 fill-current" />
            <span>
              Bonificación por feedback positivo: +{(recommendation.feedback_boost * 100).toFixed(0)}%
            </span>
          </div>
        )}
      </div>
    </div>
  );
};
