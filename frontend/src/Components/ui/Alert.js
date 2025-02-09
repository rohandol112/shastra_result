import React from 'react';
import { AlertCircle, CheckCircle, Info, XCircle } from 'lucide-react';

const AlertVariants = {
  success: {
    containerClass: 'bg-green-50 border-green-200',
    iconClass: 'text-green-400',
    textClass: 'text-green-800',
    Icon: CheckCircle
  },
  error: {
    containerClass: 'bg-red-50 border-red-200',
    iconClass: 'text-red-400',
    textClass: 'text-red-800',
    Icon: XCircle
  },
  warning: {
    containerClass: 'bg-yellow-50 border-yellow-200',
    iconClass: 'text-yellow-400',
    textClass: 'text-yellow-800',
    Icon: AlertCircle
  },
  info: {
    containerClass: 'bg-blue-50 border-blue-200',
    iconClass: 'text-blue-400',
    textClass: 'text-blue-800',
    Icon: Info
  }
};

const Alert = ({ 
  variant = 'info', 
  message, 
  onClose 
}) => {
  const style = AlertVariants[variant];
  
  return (
    <div className={`flex items-start p-4 mb-4 border rounded-lg ${style.containerClass}`}>
      <div className="flex-shrink-0">
        <style.Icon className={`h-5 w-5 ${style.iconClass}`} />
      </div>
      <div className="ml-3 w-full">
        <div className="flex justify-between">
          <div>
            <div className={`text-sm ${style.textClass}`}>
              {message}
            </div>
          </div>
          {onClose && (
            <button
              type="button"
              className={`ml-auto -mx-1.5 -my-1.5 rounded-lg focus:ring-2 p-1.5 inline-flex h-8 w-8 ${style.textClass} hover:bg-opacity-20`}
              onClick={onClose}
            >
              <span className="sr-only">Dismiss</span>
              <XCircle className="h-5 w-5" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

// Toast notification component for temporary alerts
const Toast = ({ 
  variant = 'info', 
  message, 
  onClose,
  duration = 5000 
}) => {
  React.useEffect(() => {
    if (duration && onClose) {
      const timer = setTimeout(onClose, duration);
      return () => clearTimeout(timer);
    }
  }, [duration, onClose]);

  return (
    <div className="fixed top-4 right-4 z-50 animate-slide-in">
      <Alert
        variant={variant}
        message={message}
        onClose={onClose}
        className="shadow-lg"
      />
    </div>
  );
};

// Alert Container for managing multiple alerts
const AlertContainer = ({ alerts = [], removeAlert }) => {
  return (
    <div className="fixed top-4 right-4 z-50 space-y-2">
      {alerts.map((alert) => (
        <Alert
          key={alert.id}
          variant={alert.variant}
          message={alert.message}
          title={alert.title}
          onClose={() => removeAlert(alert.id)}
          className="shadow-lg animate-slide-in"
        />
      ))}
    </div>
  );
};

export { Alert, Toast, AlertContainer };