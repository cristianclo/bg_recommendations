import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation, useQuery } from '@tanstack/react-query';
import { PageHeader, SessionProfileForm, ValidationWarnings, LoadingSpinner, ErrorAlert } from '../components';
import { sessionsService } from '../services/sessions.service';
import { skillsService } from '../services/skills.service';
import { recommendationsService } from '../services/recommendations.service';
import type { SessionProfileFormData, SessionProfile } from '../types';

export default function SessionCreatePage() {
  const navigate = useNavigate();
  const [createdSession, setCreatedSession] = useState<SessionProfile | null>(null);
  const [showWarnings, setShowWarnings] = useState(false);

  // Fetch skills for the form dropdown
  const { data: skillsData, isLoading: isLoadingSkills } = useQuery({
    queryKey: ['skills'],
    queryFn: () => skillsService.getAll({ page_size: 100 }),
  });

  // Create session mutation
  const createSessionMutation = useMutation({
    mutationFn: (data: SessionProfileFormData) => sessionsService.create(data),
    onSuccess: (session) => {
      setCreatedSession(session);
      if (session.has_warnings) {
        setShowWarnings(true);
      } else {
        // If no warnings, proceed directly to generate recommendations
        generateRecommendationsMutation.mutate(session.id);
      }
    },
  });

  // Generate recommendations mutation
  const generateRecommendationsMutation = useMutation({
    mutationFn: (sessionId: number) =>
      recommendationsService.generate({ session_profile_id: sessionId }),
    onSuccess: (_data, sessionId) => {
      // Navigate to recommendations page
      navigate(`/recommendations/${sessionId}`);
    },
  });

  const handleFormSubmit = (data: SessionProfileFormData) => {
    createSessionMutation.mutate(data);
  };

  const handleProceedWithWarnings = () => {
    if (createdSession) {
      generateRecommendationsMutation.mutate(createdSession.id);
    }
  };

  const handleEditSession = () => {
    setShowWarnings(false);
    setCreatedSession(null);
  };

  const skills = skillsData || [];

  // Show loading for skills if needed
  if (isLoadingSkills && skills.length === 0) {
    return (
      <div>
        <PageHeader
          title="Crear Perfil de Sesión"
          description="Define los objetivos y características de tu sesión para obtener recomendaciones personalizadas"
        />
        <div className="bg-white rounded-lg shadow-sm p-8">
          <LoadingSpinner text="Cargando habilidades..." />
        </div>
      </div>
    );
  }

  return (
    <div>
      <PageHeader
        title="Crear Perfil de Sesión"
        description="Define los objetivos y características de tu sesión para obtener recomendaciones personalizadas"
      />

      {/* Show warnings if session was created with warnings */}
      {showWarnings && createdSession && createdSession.validation_warnings.length > 0 && (
        <div className="mb-6 space-y-4">
          <ValidationWarnings warnings={createdSession.validation_warnings} />
          
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              ¿Deseas continuar?
            </h3>
            <p className="text-gray-600 mb-6">
              Las advertencias anteriores son informativas. Puedes proceder con la generación 
              de recomendaciones o editar el perfil de sesión.
            </p>
            <div className="flex gap-4">
              <button
                onClick={handleProceedWithWarnings}
                disabled={generateRecommendationsMutation.isPending}
                className="px-6 py-3 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 disabled:bg-gray-400 transition-colors"
              >
                {generateRecommendationsMutation.isPending
                  ? 'Generando recomendaciones...'
                  : 'Continuar y generar recomendaciones'}
              </button>
              <button
                onClick={handleEditSession}
                className="px-6 py-3 bg-white text-gray-700 font-medium rounded-md border border-gray-300 hover:bg-gray-50 transition-colors"
              >
                Editar sesión
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Show form if no warnings are being displayed */}
      {!showWarnings && (
        <>
          {/* Error Display */}
          {createSessionMutation.isError && (
            <div className="mb-6">
              <ErrorAlert
                message={
                  createSessionMutation.error instanceof Error
                    ? createSessionMutation.error.message
                    : 'Error al crear el perfil de sesión'
                }
                title="Error"
              />
            </div>
          )}

          {generateRecommendationsMutation.isError && (
            <div className="mb-6">
              <ErrorAlert
                message={
                  generateRecommendationsMutation.error instanceof Error
                    ? generateRecommendationsMutation.error.message
                    : 'Error al generar recomendaciones'
                }
                title="Error"
              />
            </div>
          )}

          {/* Loading State */}
          {(createSessionMutation.isPending || generateRecommendationsMutation.isPending) && (
            <div className="mb-6">
              <LoadingSpinner
                text={
                  createSessionMutation.isPending
                    ? 'Creando perfil de sesión...'
                    : 'Generando recomendaciones...'
                }
              />
            </div>
          )}

          {/* Session Profile Form */}
          <SessionProfileForm
            onSubmit={handleFormSubmit}
            loading={createSessionMutation.isPending}
            skills={skills}
          />
        </>
      )}

      {/* Info Box */}
      <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="font-semibold text-blue-900 mb-3">
          💡 Consejos para crear un buen perfil de sesión
        </h3>
        <ul className="text-sm text-blue-800 space-y-2">
          <li>
            <strong>Objetivos claros:</strong> Define objetivos específicos y medibles para tu sesión.
          </li>
          <li>
            <strong>Habilidades relevantes:</strong> Selecciona habilidades que realmente quieras desarrollar en tus participantes.
          </li>
          <li>
            <strong>Tiempo realista:</strong> Considera tiempo para explicar reglas, jugar y reflexionar (típicamente 60-90 minutos).
          </li>
          <li>
            <strong>Tamaño del grupo:</strong> Ten en cuenta que grupos grandes (&gt;20) pueden requerir múltiples estaciones.
          </li>
        </ul>
      </div>
    </div>
  );
}
