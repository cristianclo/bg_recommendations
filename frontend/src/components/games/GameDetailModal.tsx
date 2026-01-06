import React from 'react';
import type { Game } from '../../types';
import { X, Users, Clock, BarChart3, Languages, Star } from 'lucide-react';

interface GameDetailModalProps {
  game: Game | null;
  isOpen: boolean;
  onClose: () => void;
}

export const GameDetailModal: React.FC<GameDetailModalProps> = ({
  game,
  isOpen,
  onClose,
}) => {
  if (!isOpen || !game) return null;

  const languageDependencyLabels = {
    ninguna: 'Ninguna',
    baja: 'Baja',
    media: 'Media',
    alta: 'Alta',
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/50" 
        onClick={onClose}
      />
      
      {/* Modal */}
      <div className="relative bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b px-6 py-4 flex items-center justify-between">
          <h2 className="text-2xl font-bold text-gray-900">{game.name}</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
            aria-label="Cerrar"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Image */}
            <div>
              {game.image_url ? (
                <img
                  src={game.image_url}
                  alt={game.name}
                  className="w-full rounded-lg shadow-md"
                  onError={(e) => {
                    (e.target as HTMLImageElement).src = 'https://via.placeholder.com/400x300?text=No+Image';
                  }}
                />
              ) : (
                <div className="w-full h-64 bg-gray-200 rounded-lg flex items-center justify-center">
                  <span className="text-gray-400">Sin imagen</span>
                </div>
              )}

              {/* Availability Badge */}
              <div className="mt-4">
                {game.available ? (
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                    Disponible
                  </span>
                ) : (
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-red-100 text-red-800">
                    No disponible
                  </span>
                )}
              </div>
            </div>

            {/* Details */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Información del Juego
              </h3>

              <div className="space-y-3">
                <div className="flex items-center text-gray-700">
                  <Users className="h-5 w-5 mr-3 text-gray-400" />
                  <span>
                    <strong>Jugadores:</strong> {game.min_players}-{game.max_players}
                  </span>
                </div>

                <div className="flex items-center text-gray-700">
                  <Clock className="h-5 w-5 mr-3 text-gray-400" />
                  <span>
                    <strong>Duración:</strong> {game.duration_min} minutos
                  </span>
                </div>

                <div className="flex items-center text-gray-700">
                  <BarChart3 className="h-5 w-5 mr-3 text-gray-400" />
                  <span>
                    <strong>Complejidad:</strong> {game.complexity.toFixed(1)}/5.0
                  </span>
                </div>

                <div className="flex items-center text-gray-700">
                  <Languages className="h-5 w-5 mr-3 text-gray-400" />
                  <span>
                    <strong>Dependencia del idioma:</strong> {languageDependencyLabels[game.language_dependency]}
                  </span>
                </div>

                {game.bgg_rank && (
                  <div className="flex items-center text-gray-700">
                    <Star className="h-5 w-5 mr-3 text-gray-400" />
                    <span>
                      <strong>BGG Rank:</strong> #{game.bgg_rank}
                    </span>
                  </div>
                )}

                {game.year_published && (
                  <div className="text-gray-700">
                    <strong>Año de publicación:</strong> {game.year_published}
                  </div>
                )}
              </div>

              {/* Mechanics */}
              {game.mechanics && game.mechanics.length > 0 && (
                <div className="mt-6">
                  <h4 className="text-md font-semibold text-gray-900 mb-2">
                    Mecánicas
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {game.mechanics.map((mechanic, index) => (
                      <span
                        key={index}
                        className="px-3 py-1 text-sm bg-blue-50 text-blue-700 rounded-full"
                      >
                        {mechanic}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Description */}
          {game.description && (
            <div className="mt-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Descripción
              </h3>
              <p className="text-gray-700 leading-relaxed">
                {game.description}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
