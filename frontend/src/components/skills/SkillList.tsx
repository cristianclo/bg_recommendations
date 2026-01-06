import React from 'react';
import type { Skill } from '../../types';
import { SkillCard } from './SkillCard';
import { LoadingSpinner } from '../common/LoadingSpinner';
import { ErrorAlert } from '../common/ErrorAlert';

interface SkillListProps {
  skills: Skill[];
  loading?: boolean;
  error?: string | null;
  onSkillSelect?: (skill: Skill) => void;
  showChildren?: boolean;
  emptyMessage?: string;
}

export const SkillList: React.FC<SkillListProps> = ({
  skills,
  loading = false,
  error = null,
  onSkillSelect,
  showChildren = false,
  emptyMessage = 'No se encontraron habilidades',
}) => {
  if (loading) {
    return <LoadingSpinner text="Cargando habilidades..." />;
  }

  if (error) {
    return <ErrorAlert message={error} title="Error al cargar habilidades" />;
  }

  if (skills.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500 text-lg">{emptyMessage}</p>
      </div>
    );
  }

  // Group skills by parent if they have parent_id
  const rootSkills = skills.filter(s => !s.parent_id);
  const childSkills = skills.filter(s => s.parent_id);

  // Attach children to parents
  const skillsWithChildren = rootSkills.map(parent => ({
    ...parent,
    children: childSkills.filter(child => child.parent_id === parent.id),
  }));

  return (
    <div className="space-y-4">
      {skillsWithChildren.map((skill) => (
        <SkillCard
          key={skill.id}
          skill={skill}
          onSelect={onSkillSelect}
          showChildren={showChildren}
        />
      ))}
    </div>
  );
};
