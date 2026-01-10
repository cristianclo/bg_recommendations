import React from 'react';
import type { Skill } from '../../types';
import { SkillCard } from './SkillCard';

interface SkillListProps {
  skills: Skill[];
  onSkillSelect?: (skill: Skill) => void;
  showChildren?: boolean;
}

export const SkillList: React.FC<SkillListProps> = ({
  skills,
  onSkillSelect,
  showChildren = false,
}) => {
  if (skills.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500 text-lg">No se encontraron habilidades</p>
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
      <div className="mb-4 text-sm text-gray-600">
        Mostrando {rootSkills.length} habilidades principales con {childSkills.length} sub-habilidades
      </div>
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
