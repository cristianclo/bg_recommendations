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

  const levelColor = levelColors[(skill.level || 0) % levelColors.length];

  return (
    <div 
      className={`bg-white rounded-lg border-l-4 shadow-sm p-4 ${levelColor} ${
        onSelect ? 'cursor-pointer hover:shadow-md transition-shadow' : ''
      }`}
      onClick={() => onSelect?.(skill)}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <Star className="h-5 w-5 text-yellow-500" />
            <h3 className="text-lg font-semibold text-gray-900">
              {skill.name}
            </h3>
            {!skill.is_active && (
              <span className="px-2 py-1 text-xs bg-gray-200 text-gray-600 rounded">
                Inactiva
              </span>
            )}
          </div>
          
          {skill.description && (
            <p className="mt-2 text-sm text-gray-600">
              {skill.description}
            </p>
          )}

          {skill.path && (
            <p className="mt-2 text-xs text-gray-500">
              Ruta: {skill.path}
            </p>
          )}
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
