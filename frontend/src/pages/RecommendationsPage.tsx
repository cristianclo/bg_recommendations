import { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { ArrowLeft, FileText, Calendar, Users, Clock } from 'lucide-react';
import {
  PageHeader,
  RecommendationList,
  FeedbackForm,
  LoadingSpinner,
  ErrorAlert,
} from '../components';
import { recommendationsService } from '../services/recommendations.service';
import { sessionsService } from '../services/sessions.service';
import type { Recommendation, FeedbackFormData } from '../types';

export default function RecommendationsPage() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const [selectedRecommendation, setSelectedRecommendation] = useState<Recommendation | null>(null);
  const [isFeedbackModalOpen, setIsFeedbackModalOpen] = useState(false);

  // Fetch session profile
  const { data: session, isLoading: sessionLoading } = useQuery({
    queryKey: ['session', sessionId],
    queryFn: () => sessionsService.getById(Number(sessionId)),
    enabled: !!sessionId,
  });

  // Fetch recommendations for this session
  const {
    data: recommendations,
    isLoading: recommendationsLoading,
    error: recommendationsError,
    refetch: refetchRecommendations,
  } = useQuery({
    queryKey: ['recommendations', sessionId],
    queryFn: () => recommendationsService.getBySession(Number(sessionId!)),
    enabled: !!sessionId,
  });

  const handleFeedbackClick = (recommendation: Recommendation) => {
    setSelectedRecommendation(recommendation);
    setIsFeedbackModalOpen(true);
  };

  const handleFeedbackSubmit = async (data: FeedbackFormData) => {
    if (!selectedRecommendation) return;

    try {
      await recommendationsService.submitFeedback(selectedRecommendation.id, data);
      setIsFeedbackModalOpen(false);
      setSelectedRecommendation(null);
      // Refetch recommendations to show updated feedback
      refetchRecommendations();
    } catch (error) {
      console.error('Error submitting feedback:', error);
    }
  };

  const handleCloseFeedbackModal = () => {
    setIsFeedbackModalOpen(false);
    setSelectedRecommendation(null);
  };

  if (sessionLoading) {
    return <LoadingSpinner text="Cargando sesión..." />;
  }

  if (!session) {
    return (
      <div>
        <ErrorAlert
          message="No se encontró la sesión solicitada"
          title="Sesión no encontrada"
        />
        <Link
          to="/sessions/new"
          className="mt-4 inline-flex items-center text-blue-600 hover:text-blue-700"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Crear nueva sesión
        </Link>
      </div>
    );
  }

  return (
    <div>
      {/* Back Button */}
      <Link
        to="/sessions/new"
        className="inline-flex items-center text-blue-600 hover:text-blue-700 mb-6"
      >
        <ArrowLeft className="h-4 w-4 mr-2" />
        Crear nueva sesión
      </Link>

      <PageHeader
        title="Recomendaciones de Juegos"
        description={`Basadas en el perfil de sesión${session.session_name ? `: ${session.session_name}` : ''}`}
      />

      {/* Session Summary Card */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center">
            <FileText className="h-6 w-6 text-blue-600 mr-3" />
            <h2 className="text-xl font-semibold text-gray-900">
              Resumen de la Sesión
            </h2>
          </div>
          {session.has_warnings && (
            <span className="px-3 py-1 bg-yellow-100 text-yellow-800 text-sm font-medium rounded-full">
              Con advertencias
            </span>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
          <div className="flex items-center text-gray-700">
            <Clock className="h-5 w-5 text-gray-400 mr-2" />
            <div>
              <div className="text-xs text-gray-500">Tiempo</div>
              <div className="font-medium">{session.available_time_min} minutos</div>
            </div>
          </div>

          <div className="flex items-center text-gray-700">
            <Users className="h-5 w-5 text-gray-400 mr-2" />
            <div>
              <div className="text-xs text-gray-500">Participantes</div>
              <div className="font-medium">{session.group_size} personas</div>
            </div>
          </div>

          <div className="flex items-center text-gray-700">
            <Calendar className="h-5 w-5 text-gray-400 mr-2" />
            <div>
              <div className="text-xs text-gray-500">Modalidad</div>
              <div className="font-medium capitalize">
                {session.preferred_modality === 'any'
                  ? 'Sin preferencia'
                  : session.preferred_modality}
              </div>
            </div>
          </div>

          <div className="flex items-center text-gray-700">
            <div className="text-xs text-gray-500">Idioma</div>
            <div className="font-medium ml-2 capitalize">
              {session.max_language_dependency}
            </div>
          </div>
        </div>

        {/* Skills */}
        <div className="mb-4">
          <h3 className="text-sm font-semibold text-gray-700 mb-2">Habilidades:</h3>
          <div className="flex flex-wrap gap-2">
            <span className="px-3 py-1 bg-blue-100 text-blue-800 text-sm font-medium rounded-full">
              {session.primary_skill_name} (Principal)
            </span>
            {session.secondary_skill_name && (
              <span className="px-3 py-1 bg-purple-100 text-purple-800 text-sm font-medium rounded-full">
                {session.secondary_skill_name} (Secundaria)
              </span>
            )}
          </div>
        </div>

        {/* Objectives */}
        {session.objectives && session.objectives.length > 0 && (
          <div>
            <h3 className="text-sm font-semibold text-gray-700 mb-2">Objetivos:</h3>
            <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
              {session.objectives.map((objective, index) => (
                <li key={index}>{objective}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Notes */}
        {session.notes && (
          <div className="mt-4 pt-4 border-t">
            <h3 className="text-sm font-semibold text-gray-700 mb-2">Notas:</h3>
            <p className="text-sm text-gray-600">{session.notes}</p>
          </div>
        )}
      </div>

      {/* Recommendations List */}
      {recommendationsError ? (
        <ErrorAlert
          message={
            recommendationsError instanceof Error
              ? recommendationsError.message
              : 'Error al cargar las recomendaciones'
          }
          title="Error"
        />
      ) : (
        <RecommendationList
          recommendations={recommendations || []}
          loading={recommendationsLoading}
          onFeedback={handleFeedbackClick}
        />
      )}

      {/* Feedback Form Modal */}
      <FeedbackForm
        isOpen={isFeedbackModalOpen}
        onClose={handleCloseFeedbackModal}
        onSubmit={handleFeedbackSubmit}
        gameName={selectedRecommendation?.game?.name}
      />

      {/* Help Section */}
      {recommendations && recommendations.length > 0 && (
        <div className="mt-8 bg-green-50 border border-green-200 rounded-lg p-6">
          <h3 className="font-semibold text-green-900 mb-3">
            📊 Después de usar un juego
          </h3>
          <p className="text-sm text-green-800">
            Te invitamos a proporcionar feedback sobre cómo funcionó el juego en tu sesión. 
            Esta información nos ayuda a mejorar las recomendaciones futuras y beneficia a 
            toda la comunidad CJEI.
          </p>
        </div>
      )}
    </div>
  );
}
