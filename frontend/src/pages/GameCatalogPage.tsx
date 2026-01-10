import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Search, Filter } from 'lucide-react';
import { PageHeader, GameList, GameDetailModal } from '../components';
import { gamesService } from '../services/games.service';
import type { Game } from '../types';

export default function GameCatalogPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedGame, setSelectedGame] = useState<Game | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [availableOnly, setAvailableOnly] = useState(false);

  const { data: gamesData, isLoading, error } = useQuery({
    queryKey: ['games', searchTerm, availableOnly],
    queryFn: () => gamesService.getAll({ 
      name: searchTerm || undefined,
      available: availableOnly || undefined,
    }),
  });

  const handleGameSelect = (game: Game) => {
    setSelectedGame(game);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedGame(null);
  };

  return (
    <div>
      <PageHeader
        title="Catálogo de Juegos"
        description="Explora nuestra colección completa de juegos de mesa"
      />

      {/* Search and Filters */}
      <div className="bg-white rounded-lg shadow-sm p-4 mb-6">
        <div className="flex flex-col md:flex-row gap-4">
          {/* Search */}
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Buscar juegos por nombre..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Available Filter */}
          <div className="flex items-center gap-2">
            <Filter className="h-5 w-5 text-gray-500" />
            <label className="flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={availableOnly}
                onChange={(e) => setAvailableOnly(e.target.checked)}
                className="h-4 w-4 text-blue-600 rounded border-gray-300 focus:ring-2 focus:ring-blue-500"
              />
              <span className="ml-2 text-sm text-gray-700">
                Solo disponibles
              </span>
            </label>
          </div>
        </div>
      </div>

      {/* Results Count */}
      {gamesData && !isLoading && (
        <div className="mb-4 text-sm text-gray-600">
          {gamesData.total} {gamesData.total === 1 ? 'juego encontrado' : 'juegos encontrados'}
        </div>
      )}

      {/* Game List */}
      <GameList
        games={gamesData?.items || []}
        loading={isLoading}
        error={error instanceof Error ? error.message : null}
        onGameSelect={handleGameSelect}
        emptyMessage={
          searchTerm
            ? `No se encontraron juegos que coincidan con "${searchTerm}"`
            : 'No hay juegos en el catálogo'
        }
      />

      {/* Game Detail Modal */}
      <GameDetailModal
        game={selectedGame}
        isOpen={isModalOpen}
        onClose={handleCloseModal}
      />
    </div>
  );
}
