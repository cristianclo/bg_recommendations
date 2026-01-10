import React from 'react';
import { Star, TrendingUp, MessageSquare } from 'lucide-react';

interface FeedbackSummaryProps {
  gameId?: number;
  gameName?: string;
  totalUses?: number;
  averageUtility?: number;
  ratingDistribution?: Record<number, number>;
  recentComments?: Array<{
    asesor: string;
    date: string;
    what_worked_well?: string;
    what_didnt_work?: string;
  }>;
}

export const FeedbackSummary: React.FC<FeedbackSummaryProps> = ({
  gameId: _gameId,
  gameName: _gameName,
  totalUses = 0,
  averageUtility = 0,
  ratingDistribution = {},
  recentComments = [],
}) => {
  if (totalUses === 0) {
    return (
      <div className="bg-gray-50 rounded-lg p-6 text-center">
        <p className="text-gray-500">
          Aún no hay feedback para este juego
        </p>
      </div>
    );
  }

  const getRatingColor = (rating: number) => {
    if (rating >= 4) return 'text-green-600';
    if (rating >= 3) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="space-y-6">
      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Total de usos</p>
              <p className="text-3xl font-bold text-gray-900 mt-1">{totalUses}</p>
            </div>
            <TrendingUp className="h-8 w-8 text-blue-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Utilidad promedio</p>
              <div className="flex items-center mt-1">
                <p className={`text-3xl font-bold ${getRatingColor(averageUtility)}`}>
                  {averageUtility.toFixed(1)}
                </p>
                <Star className="h-6 w-6 text-yellow-400 fill-current ml-2" />
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Comentarios</p>
              <p className="text-3xl font-bold text-gray-900 mt-1">{recentComments.length}</p>
            </div>
            <MessageSquare className="h-8 w-8 text-purple-500" />
          </div>
        </div>
      </div>

      {/* Rating Distribution */}
      {Object.keys(ratingDistribution).length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Distribución de Calificaciones
          </h3>
          <div className="space-y-2">
            {[5, 4, 3, 2, 1].map((rating) => {
              const count = ratingDistribution[rating] || 0;
              const percentage = totalUses > 0 ? (count / totalUses) * 100 : 0;
              
              return (
                <div key={rating} className="flex items-center gap-3">
                  <div className="flex items-center w-20">
                    <span className="text-sm font-medium text-gray-700">{rating}</span>
                    <Star className="h-4 w-4 text-yellow-400 fill-current ml-1" />
                  </div>
                  <div className="flex-1 h-4 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-yellow-400"
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                  <span className="text-sm text-gray-600 w-12 text-right">
                    {count}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Recent Comments */}
      {recentComments.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Comentarios Recientes
          </h3>
          <div className="space-y-4">
            {recentComments.map((comment, index) => (
              <div key={index} className="border-l-4 border-blue-500 pl-4 py-2">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium text-gray-900">{comment.asesor}</span>
                  <span className="text-sm text-gray-500">
                    {new Date(comment.date).toLocaleDateString('es-CO')}
                  </span>
                </div>
                {comment.what_worked_well && (
                  <div className="mb-2">
                    <p className="text-sm font-medium text-green-700">Lo que funcionó bien:</p>
                    <p className="text-sm text-gray-600">{comment.what_worked_well}</p>
                  </div>
                )}
                {comment.what_didnt_work && (
                  <div>
                    <p className="text-sm font-medium text-red-700">Lo que no funcionó:</p>
                    <p className="text-sm text-gray-600">{comment.what_didnt_work}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
