import React from 'react';
import type { Game } from '../../types';
import { GameCard } from './GameCard';
import { LoadingSpinner } from '../common/LoadingSpinner';
import { ErrorAlert } from '../common/ErrorAlert';

interface GameListProps {
  games: Game[];
  loading?: boolean;
  error?: string | null;
  onGameSelect?: (game: Game) => void;
  emptyMessage?: string;
}

export const GameList: React.FC<GameListProps> = ({
  games,
  loading = false,
  error = null,
  onGameSelect,
  emptyMessage = 'No se encontraron juegos',
}) => {
  if (loading) {
    return <LoadingSpinner text="Cargando juegos..." />;
  }

  if (error) {
    return <ErrorAlert message={error} title="Error al cargar juegos" />;
  }

  if (games.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500 text-lg">{emptyMessage}</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {games.map((game) => (
        <GameCard
          key={game.id}
          game={game}
          onSelect={onGameSelect}
        />
      ))}
    </div>
  );
};
