import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import type { Skill } from '../../types';

const sessionProfileSchema = z.object({
  session_name: z.string().optional(),
  objectives: z.array(z.string()).min(1, 'Debe especificar al menos un objetivo'),
  primary_skill_id: z.string().min(1, 'Debe seleccionar una habilidad primaria'),
  secondary_skill_ids: z.array(z.string()).optional(),
  available_time_min: z.number().min(15, 'Mínimo 15 minutos').max(240, 'Máximo 240 minutos'),
  group_size: z.number().min(1, 'Mínimo 1 persona').max(100, 'Máximo 100 personas'),
  max_language_dependency: z.enum(['ninguna', 'baja', 'media', 'alta']),
  preferred_modality: z.enum(['competitive', 'cooperative', 'any']).optional(),
  notes: z.string().max(500, 'Máximo 500 caracteres').optional().nullable(),
});

type SessionProfileFormData = z.infer<typeof sessionProfileSchema>;

interface SessionProfileFormProps {
  onSubmit: (data: SessionProfileFormData) => void;
  loading?: boolean;
  skills?: Skill[];
}

export const SessionProfileForm: React.FC<SessionProfileFormProps> = ({
  onSubmit,
  loading = false,
  skills = [],
}) => {
  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue,
  } = useForm<SessionProfileFormData>({
    resolver: zodResolver(sessionProfileSchema),
    defaultValues: {
      objectives: [''],
      available_time_min: 60,
      group_size: 4,
      max_language_dependency: 'baja',
      preferred_modality: 'any',
    },
  });

  const [objectives, setObjectives] = React.useState<string[]>(['']);

  const addObjective = () => {
    const newObjectives = [...objectives, ''];
    setObjectives(newObjectives);
    setValue('objectives', newObjectives);
  };

  const removeObjective = (index: number) => {
    const newObjectives = objectives.filter((_, i) => i !== index);
    setObjectives(newObjectives);
    setValue('objectives', newObjectives);
  };

  const updateObjective = (index: number, value: string) => {
    const newObjectives = [...objectives];
    newObjectives[index] = value;
    setObjectives(newObjectives);
    setValue('objectives', newObjectives);
  };

  const handleFormSubmit = (data: SessionProfileFormData) => {
    // Filter out empty objectives
    const filteredObjectives = objectives.filter(obj => obj.trim() !== '');
    onSubmit({
      ...data,
      objectives: filteredObjectives,
    });
  };

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-6 bg-white p-6 rounded-lg shadow">
      {/* Session Name */}
      <div>
        <label htmlFor="session_name" className="block text-sm font-medium text-gray-700 mb-1">
          Nombre de la sesión (opcional)
        </label>
        <input
          {...register('session_name')}
          type="text"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="Ej: Taller de Trabajo en Equipo"
        />
      </div>

      {/* Objectives */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Objetivos de la sesión *
        </label>
        {objectives.map((objective, index) => (
          <div key={index} className="flex gap-2 mb-2">
            <input
              type="text"
              value={objective}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Ej: Fomentar el pensamiento crítico"
              onChange={(e) => updateObjective(index, e.target.value)}
            />
            {objectives.length > 1 && (
              <button
                type="button"
                onClick={() => removeObjective(index)}
                className="px-3 py-2 text-red-600 hover:bg-red-50 rounded-md"
              >
                Eliminar
              </button>
            )}
          </div>
        ))}
        <button
          type="button"
          onClick={addObjective}
          className="text-sm text-blue-600 hover:text-blue-700"
        >
          + Agregar objetivo
        </button>
        {errors.objectives && (
          <p className="mt-1 text-sm text-red-600">{errors.objectives.message}</p>
        )}
      </div>

      {/* Skills */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label htmlFor="primary_skill_id" className="block text-sm font-medium text-gray-700 mb-1">
            Habilidad primaria *
          </label>
          <select
            {...register('primary_skill_id')}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">Seleccionar...</option>
            {skills.map((skill) => (
              <option key={skill.id} value={skill.id}>
                {skill.name} ({skill.category})
              </option>
            ))}
          </select>
          {errors.primary_skill_id && (
            <p className="mt-1 text-sm text-red-600">{errors.primary_skill_id.message}</p>
          )}
        </div>

        <div>
          <label htmlFor="secondary_skill_ids" className="block text-sm font-medium text-gray-700 mb-1">
            Habilidades secundarias (opcional)
          </label>
          <select
            {...register('secondary_skill_ids')}
            multiple
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            size={4}
          >
            {skills.map((skill) => (
              <option key={skill.id} value={skill.id}>
                {skill.name} ({skill.category})
              </option>
            ))}
          </select>
          <p className="mt-1 text-xs text-gray-500">
            Mantén presionado Cmd/Ctrl para seleccionar múltiples
          </p>
        </div>
      </div>

      {/* Time and Group Size */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label htmlFor="available_time_min" className="block text-sm font-medium text-gray-700 mb-1">
            Tiempo disponible (minutos) *
          </label>
          <input
            {...register('available_time_min', { valueAsNumber: true })}
            type="number"
            min="15"
            max="240"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          {errors.available_time_min && (
            <p className="mt-1 text-sm text-red-600">{errors.available_time_min.message}</p>
          )}
        </div>

        <div>
          <label htmlFor="group_size" className="block text-sm font-medium text-gray-700 mb-1">
            Tamaño del grupo *
          </label>
          <input
            {...register('group_size', { valueAsNumber: true })}
            type="number"
            min="1"
            max="100"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          {errors.group_size && (
            <p className="mt-1 text-sm text-red-600">{errors.group_size.message}</p>
          )}
        </div>
      </div>

      {/* Language and Modality */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label htmlFor="max_language_dependency" className="block text-sm font-medium text-gray-700 mb-1">
            Dependencia máxima del idioma *
          </label>
          <select
            {...register('max_language_dependency')}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="ninguna">Ninguna</option>
            <option value="baja">Baja</option>
            <option value="media">Media</option>
            <option value="alta">Alta</option>
          </select>
        </div>

        <div>
          <label htmlFor="preferred_modality" className="block text-sm font-medium text-gray-700 mb-1">
            Modalidad preferida
          </label>
          <select
            {...register('preferred_modality')}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="any">Sin preferencia</option>
            <option value="competitive">Competitivo</option>
            <option value="cooperative">Cooperativo</option>
          </select>
        </div>
      </div>

      {/* Notes */}
      <div>
        <label htmlFor="notes" className="block text-sm font-medium text-gray-700 mb-1">
          Notas adicionales
        </label>
        <textarea
          {...register('notes')}
          rows={3}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="Cualquier otra consideración o restricción..."
        />
        {errors.notes && (
          <p className="mt-1 text-sm text-red-600">{errors.notes.message}</p>
        )}
      </div>

      {/* Submit Button */}
      <div className="flex justify-end">
        <button
          type="submit"
          disabled={loading}
          className="px-6 py-3 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? 'Generando...' : 'Generar Recomendaciones'}
        </button>
      </div>
    </form>
  );
};
