import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { X, Star } from 'lucide-react';

const feedbackSchema = z.object({
  was_used: z.boolean(),
  user_feedback_score: z.number().min(1).max(5),
  feedback_asesor: z.string().min(1, 'El nombre del asesor es requerido'),
  skill_actually_worked: z.string().optional(),
  what_worked_well: z.string().max(500).optional(),
  what_didnt_work: z.string().max(500).optional(),
  additional_notes: z.string().max(500).optional(),
});

type FeedbackFormData = z.infer<typeof feedbackSchema>;

interface FeedbackFormProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: FeedbackFormData) => void;
  loading?: boolean;
  gameName?: string;
}

export const FeedbackForm: React.FC<FeedbackFormProps> = ({
  isOpen,
  onClose,
  onSubmit,
  loading = false,
  gameName = 'este juego',
}) => {
  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue,
  } = useForm<FeedbackFormData>({
    resolver: zodResolver(feedbackSchema),
    defaultValues: {
      was_used: true,
      user_feedback_score: 3,
    },
  });

  const [rating, setRating] = React.useState(3);
  const [hoveredRating, setHoveredRating] = React.useState(0);

  if (!isOpen) return null;

  const handleRatingClick = (value: number) => {
    setRating(value);
    setValue('user_feedback_score', value);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/50" 
        onClick={onClose}
      />
      
      {/* Modal */}
      <div className="relative bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b px-6 py-4 flex items-center justify-between">
          <h2 className="text-xl font-bold text-gray-900">
            Feedback para {gameName}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
            aria-label="Cerrar"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-6">
          {/* Was Used */}
          <div>
            <label className="flex items-center">
              <input
                {...register('was_used')}
                type="checkbox"
                className="h-4 w-4 text-blue-600 rounded border-gray-300 focus:ring-2 focus:ring-blue-500"
              />
              <span className="ml-2 text-sm font-medium text-gray-700">
                ¿Se utilizó este juego en la sesión?
              </span>
            </label>
          </div>

          {/* Rating */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Calificación de utilidad *
            </label>
            <div className="flex gap-2">
              {[1, 2, 3, 4, 5].map((value) => (
                <button
                  key={value}
                  type="button"
                  onClick={() => handleRatingClick(value)}
                  onMouseEnter={() => setHoveredRating(value)}
                  onMouseLeave={() => setHoveredRating(0)}
                  className="focus:outline-none"
                >
                  <Star
                    className={`h-8 w-8 ${
                      value <= (hoveredRating || rating)
                        ? 'fill-yellow-400 text-yellow-400'
                        : 'text-gray-300'
                    }`}
                  />
                </button>
              ))}
            </div>
            {errors.user_feedback_score && (
              <p className="mt-1 text-sm text-red-600">{errors.user_feedback_score.message}</p>
            )}
          </div>

          {/* Asesor Name */}
          <div>
            <label htmlFor="feedback_asesor" className="block text-sm font-medium text-gray-700 mb-1">
              Nombre del asesor *
            </label>
            <input
              {...register('feedback_asesor')}
              type="text"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Tu nombre"
            />
            {errors.feedback_asesor && (
              <p className="mt-1 text-sm text-red-600">{errors.feedback_asesor.message}</p>
            )}
          </div>

          {/* Skill Actually Worked */}
          <div>
            <label htmlFor="skill_actually_worked" className="block text-sm font-medium text-gray-700 mb-1">
              Habilidad que realmente se trabajó
            </label>
            <input
              {...register('skill_actually_worked')}
              type="text"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Ej: Pensamiento crítico"
            />
          </div>

          {/* What Worked Well */}
          <div>
            <label htmlFor="what_worked_well" className="block text-sm font-medium text-gray-700 mb-1">
              ¿Qué funcionó bien?
            </label>
            <textarea
              {...register('what_worked_well')}
              rows={3}
              maxLength={500}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Describe los aspectos positivos..."
            />
            {errors.what_worked_well && (
              <p className="mt-1 text-sm text-red-600">{errors.what_worked_well.message}</p>
            )}
          </div>

          {/* What Didn't Work */}
          <div>
            <label htmlFor="what_didnt_work" className="block text-sm font-medium text-gray-700 mb-1">
              ¿Qué no funcionó?
            </label>
            <textarea
              {...register('what_didnt_work')}
              rows={3}
              maxLength={500}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Describe los aspectos a mejorar..."
            />
            {errors.what_didnt_work && (
              <p className="mt-1 text-sm text-red-600">{errors.what_didnt_work.message}</p>
            )}
          </div>

          {/* Additional Notes */}
          <div>
            <label htmlFor="additional_notes" className="block text-sm font-medium text-gray-700 mb-1">
              Notas adicionales
            </label>
            <textarea
              {...register('additional_notes')}
              rows={2}
              maxLength={500}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Cualquier otra observación..."
            />
            {errors.additional_notes && (
              <p className="mt-1 text-sm text-red-600">{errors.additional_notes.message}</p>
            )}
          </div>

          {/* Edit Window Notice */}
          <div className="bg-blue-50 border border-blue-200 rounded-md p-3">
            <p className="text-sm text-blue-800">
              <strong>Nota:</strong> Podrás editar este feedback durante los próximos 7 días.
            </p>
          </div>

          {/* Actions */}
          <div className="flex justify-end gap-3 pt-4 border-t">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              {loading ? 'Enviando...' : 'Enviar Feedback'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
