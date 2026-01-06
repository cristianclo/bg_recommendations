import { useQuery } from '@tanstack/react-query';
import { PageHeader, SkillList } from '../components';
import { skillsService } from '../services/skills.service';

export default function SkillsPage() {
  const { data: skillsData, isLoading, error } = useQuery({
    queryKey: ['skills'],
    queryFn: () => skillsService.getAll(),
  });

  const skills = skillsData?.items || [];

  return (
    <div>
      <PageHeader
        title="Taxonomía de Habilidades"
        description="Explora la jerarquía completa de habilidades pedagógicas"
      />

      <div className="bg-white rounded-lg shadow-sm p-6">
        <SkillList
          skills={skills}
          loading={isLoading}
          error={error instanceof Error ? error.message : null}
          showChildren={true}
          emptyMessage="No se han definido habilidades en el sistema"
        />
      </div>

      {/* Info Box */}
      {skills.length > 0 && (
        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="font-semibold text-blue-900 mb-2">
            Acerca de las Habilidades
          </h3>
          <p className="text-sm text-blue-800">
            Las habilidades están organizadas jerárquicamente para facilitar la búsqueda y 
            selección al crear perfiles de sesión. Cada juego puede estar asociado con una 
            habilidad primaria y secundaria, lo que permite recomendaciones más precisas.
          </p>
        </div>
      )}
    </div>
  );
}
