import React from 'react';
import type { Recommendation } from '../../types';
import { RecommendationCard } from './RecommendationCard';
import { LoadingSpinner } from '../common/LoadingSpinner';
import { ErrorAlert } from '../common/ErrorAlert';

interface RecommendationListProps {
  recommendations: Recommendation[];
  loading?: boolean;
  error?: string | null;
  onFeedback?: (recommendation: Recommendation) => void;
}

export const RecommendationList: React.FC<RecommendationListProps> = ({
  recommendations,
  loading = false,
  error = null,
  onFeedback,
}) => {
  console.log('📋 RecommendationList props:', {
    recommendationsCount: recommendations?.length || 0,
    loading,
    error,
    recommendations
  });

  if (loading) {
    console.log('⏳ Showing loading state');
    return <LoadingSpinner text="Generando recomendaciones..." />;
  }

  if (error) {
    console.log('❌ Showing error:', error);
    return <ErrorAlert message={error} title="Error al generar recomendaciones" />;
  }

  if (recommendations.length === 0) {
    console.log('⚠️ No recommendations found');
    return (
      <div className="text-center py-12 bg-white rounded-lg shadow">
        <p className="text-gray-500 text-lg">
          No se encontraron recomendaciones para los criterios especificados
        </p>
        <p className="text-gray-400 text-sm mt-2">
          Intenta ajustar los parámetros de búsqueda
        </p>
      </div>
    );
  }

  console.log('✅ Rendering', recommendations.length, 'recommendations');

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold text-gray-900">
          Recomendaciones ({recommendations.length})
        </h2>
      </div>
      
      {recommendations.map((recommendation) => (
        <RecommendationCard
          key={recommendation.id}
          recommendation={recommendation}
          rank={recommendation.rank}
          onFeedback={onFeedback}
        />
      ))}
    </div>
  );
};
