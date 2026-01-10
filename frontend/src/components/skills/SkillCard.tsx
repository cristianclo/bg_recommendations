import React from 'react';
import type { Skill } from '../../types';
import { Star, ChevronRight } from 'lucide-react';

interface SkillCardProps {
  skill: Skill;
  onSelect?: (skill: Skill) => void;
  showChildren?: boolean;
}

export const SkillCard: React.FC<SkillCardProps> = ({ 
  skill, 
  onSelect,
  showChildren = false 
}) => {
  const levelColors = [
    'border-blue-500 bg-blue-50',
    'border-green-500 bg-green-50',
    'border-purple-500 bg-purple-50',
    'border-orange-500 bg-orange-50',
  ];

  const levelColor = levelColors[(skill.level - 1) % levelColors.length];

  const categoryColors: Record<string, string> = {
    cognitiva: 'bg-blue-100 text-blue-800',
    social: 'bg-green-100 text-green-800',
    emocional: 'bg-purple-100 text-purple-800',
    practica: 'bg-orange-100 text-orange-800',
  };

  return (
    <div 
      className={`bg-white rounded-lg border-l-4 shadow-sm p-4 ${levelColor} ${
        onSelect ? 'cursor-pointer hover:shadow-md transition-shadow' : ''
      }`}
      onClick={() => onSelect?.(skill)}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <Star className="h-5 w-5 text-yellow-500" />
            <h3 className="text-lg font-semibold text-gray-900">
              {skill.name}
            </h3>
            <span className={`px-2 py-1 text-xs rounded ${categoryColors[skill.category] || 'bg-gray-100 text-gray-800'}`}>
              {skill.category}
            </span>
            <span className="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded">
              Nivel {skill.level}
            </span>
          </div>
          
          <p className="mt-2 text-sm text-gray-700 font-medium">
            {skill.definition}
          </p>

          {skill.examples && skill.examples.length > 0 && (
            <div className="mt-3">
              <p className="text-xs font-semibold text-gray-600 mb-1">Ejemplos:</p>
              <ul className="text-sm text-gray-600 list-disc list-inside">
                {skill.examples.map((example, idx) => (
                  <li key={idx}>{example}</li>
                ))}
              </ul>
            </div>
          )}

          {skill.contexts && (
            <div className="mt-3">
              <p className="text-xs font-semibold text-gray-600 mb-1">Contextos de aplicación:</p>
              <p className="text-sm text-gray-600">{skill.contexts}</p>
            </div>
          )}

          <div className="mt-3 flex items-center gap-4 text-xs text-gray-500">
            <span>🎮 {skill.games_count} juegos asociados</span>
            {skill.parent_id && <span>↳ Sub-habilidad</span>}
          </div>
        </div>

        {showChildren && skill.children && skill.children.length > 0 && (
          <div className="ml-4">
            <ChevronRight className="h-5 w-5 text-gray-400" />
            <span className="text-xs text-gray-500">
              {skill.children.length} sub-habilidades
            </span>
          </div>
        )}
      </div>

      {/* Children */}
      {showChildren && skill.children && skill.children.length > 0 && (
        <div className="mt-4 ml-6 space-y-2">
          {skill.children.map((child) => (
            <div key={child.id} className="text-sm text-gray-700">
              • {child.name}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
