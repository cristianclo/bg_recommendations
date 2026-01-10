import React from 'react';
import { AlertCircle, XCircle } from 'lucide-react';

interface ErrorAlertProps {
  message: string;
  title?: string;
  onDismiss?: () => void;
  variant?: 'error' | 'warning';
}

export const ErrorAlert: React.FC<ErrorAlertProps> = ({ 
  message, 
  title = 'Error',
  onDismiss,
  variant = 'error'
}) => {
  const bgColor = variant === 'error' ? 'bg-red-50' : 'bg-yellow-50';
  const borderColor = variant === 'error' ? 'border-red-200' : 'border-yellow-200';
  const textColor = variant === 'error' ? 'text-red-800' : 'text-yellow-800';
  const Icon = variant === 'error' ? AlertCircle : AlertCircle;

  return (
    <div className={`${bgColor} ${borderColor} border-l-4 p-4 rounded`} role="alert">
      <div className="flex items-start">
        <Icon className={`h-5 w-5 ${textColor} mr-3 flex-shrink-0`} />
        <div className="flex-1">
          <p className={`font-medium ${textColor}`}>{title}</p>
          <p className={`text-sm ${textColor} mt-1`}>{message}</p>
        </div>
        {onDismiss && (
          <button
            onClick={onDismiss}
            className={`ml-4 ${textColor} hover:opacity-75`}
            aria-label="Dismiss"
          >
            <XCircle className="h-5 w-5" />
          </button>
        )}
      </div>
    </div>
  );
};
