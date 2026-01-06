import React from 'react';
import type { Game } from '../../types';
import { Users, Clock, BarChart3, Languages } from 'lucide-react';

interface GameCardProps {
  game: Game;
  onSelect?: (game: Game) => void;
  showDetails?: boolean;
}

export const GameCard: React.FC<GameCardProps> = ({ 
  game, 
  onSelect,
  showDetails = true 
}) => {
  const languageDependencyLabels = {
    ninguna: 'Ninguna',
    baja: 'Baja',
    media: 'Media',
    alta: 'Alta',
  };

  return (
    <div 
      className={`bg-white rounded-lg shadow-md overflow-hidden border border-gray-200 transition-all ${
        onSelect ? 'cursor-pointer hover:shadow-lg hover:scale-[1.02]' : ''
      }`}
      onClick={() => onSelect?.(game)}
    >
      {/* Game Image */}
      {game.image_url && (
        <div className="w-full h-48 bg-gray-200">
          <img
            src={game.image_url}
            alt={game.name}
            className="w-full h-full object-cover"
            onError={(e) => {
              (e.target as HTMLImageElement).src = 'https://via.placeholder.com/400x300?text=No+Image';
            }}
          />
        </div>
      )}

      {/* Game Info */}
      <div className="p-4">
        <div className="flex items-start justify-between mb-2">
          <h3 className="text-lg font-semibold text-gray-900 flex-1">
            {game.name}
          </h3>
          {!game.available && (
            <span className="ml-2 px-2 py-1 text-xs font-semibold bg-red-100 text-red-800 rounded">
              No disponible
            </span>
          )}
        </div>

        {showDetails && (
          <>
            {/* Game Stats */}
            <div className="grid grid-cols-2 gap-3 mt-4">
              <div className="flex items-center text-sm text-gray-600">
                <Users className="h-4 w-4 mr-2 text-gray-400" />
                <span>{game.min_players}-{game.max_players} jugadores</span>
              </div>
              <div className="flex items-center text-sm text-gray-600">
                <Clock className="h-4 w-4 mr-2 text-gray-400" />
                <span>{game.duration_min} min</span>
              </div>
              <div className="flex items-center text-sm text-gray-600">
                <BarChart3 className="h-4 w-4 mr-2 text-gray-400" />
                <span>Complejidad: {game.complexity.toFixed(1)}</span>
              </div>
              <div className="flex items-center text-sm text-gray-600">
                <Languages className="h-4 w-4 mr-2 text-gray-400" />
                <span>{languageDependencyLabels[game.language_dependency]}</span>
              </div>
            </div>

            {/* Mechanics */}
            {game.mechanics && game.mechanics.length > 0 && (
              <div className="mt-3">
                <div className="flex flex-wrap gap-1">
                  {game.mechanics.slice(0, 3).map((mechanic, index) => (
                    <span
                      key={index}
                      className="px-2 py-1 text-xs bg-blue-50 text-blue-700 rounded"
                    >
                      {mechanic}
                    </span>
                  ))}
                  {game.mechanics.length > 3 && (
                    <span className="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded">
                      +{game.mechanics.length - 3} más
                    </span>
                  )}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};
