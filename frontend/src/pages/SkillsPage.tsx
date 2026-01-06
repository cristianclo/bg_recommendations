import { useQuery } from '@tanstack/react-query';
import { PageHeader, SkillList, LoadingSpinner, ErrorAlert } from '../components';
import { skillsService } from '../services/skills.service';

export default function SkillsPage() {
  const { data: skillsData, isLoading, error } = useQuery({
    queryKey: ['skills'],
    queryFn: () => skillsService.getAll({ page_size: 100 }),
  });

  const skills = skillsData || [];

  if (isLoading) {
    return (
      <div>
        <PageHeader
          title="Taxonomía de Habilidades"
          description="Explora la jerarquía completa de habilidades pedagógicas"
        />
        <LoadingSpinner text="Cargando habilidades..." />
      </div>
    );
  }

  if (error) {
    return (
      <div>
        <PageHeader
          title="Taxonomía de Habilidades"
          description="Explora la jerarquía completa de habilidades pedagógicas"
        />
        <ErrorAlert
          message={error instanceof Error ? error.message : 'Error desconocido al cargar habilidades'}
          title="Error al cargar habilidades"
        />
      </div>
    );
  }

  return (
    <div>
      <PageHeader
        title="Taxonomía de Habilidades"
        description="Explora la jerarquía completa de habilidades pedagógicas"
      />

      <div className="bg-white rounded-lg shadow-sm p-6">
        {skills.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-500 text-lg">No se han definido habilidades en el sistema</p>
          </div>
        ) : (
          <SkillList
            skills={skills}
            showChildren={true}
          />
        )}
      </div>

      {/* Info Box */}
      {skills.length > 0 && (
        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="font-semibold text-blue-900 mb-2">
            📚 Acerca de las Habilidades
          </h3>
          <p className="text-sm text-blue-800 mb-2">
            Las habilidades están organizadas jerárquicamente en 4 niveles para facilitar la búsqueda y 
            selección al crear perfiles de sesión.
          </p>
          <p className="text-sm text-blue-800">
            <strong>Total de habilidades:</strong> {skills.length}
          </p>
        </div>
      )}
    </div>
  );
}
