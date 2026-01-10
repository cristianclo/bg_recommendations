import React from 'react';
import type { ValidationWarning as ValidationWarningType } from '../../types';
import { AlertTriangle, Info } from 'lucide-react';

interface ValidationWarningsProps {
  warnings: ValidationWarningType[];
}

export const ValidationWarnings: React.FC<ValidationWarningsProps> = ({ warnings }) => {
  if (warnings.length === 0) return null;

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high':
        return 'bg-red-50 border-red-200 text-red-800';
      case 'medium':
        return 'bg-yellow-50 border-yellow-200 text-yellow-800';
      case 'low':
        return 'bg-blue-50 border-blue-200 text-blue-800';
      default:
        return 'bg-gray-50 border-gray-200 text-gray-800';
    }
  };

  const getSeverityIcon = (severity: string) => {
    return severity === 'high' ? AlertTriangle : Info;
  };

  return (
    <div className="space-y-3 mb-6">
      <h3 className="text-lg font-semibold text-gray-900">
        Advertencias de Validación
      </h3>
      {warnings.map((warning, index) => {
        const Icon = getSeverityIcon(warning.severity);
        return (
          <div
            key={index}
            className={`border-l-4 p-4 rounded ${getSeverityColor(warning.severity)}`}
          >
            <div className="flex items-start">
              <Icon className="h-5 w-5 mr-3 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <p className="font-medium">{warning.message}</p>
                {warning.suggestions && warning.suggestions.length > 0 && (
                  <ul className="mt-2 text-sm list-disc list-inside space-y-1">
                    {warning.suggestions.map((suggestion, idx) => (
                      <li key={idx}>{suggestion}</li>
                    ))}
                  </ul>
                )}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};
