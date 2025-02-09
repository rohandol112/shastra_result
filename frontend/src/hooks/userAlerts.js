import { useState, useCallback } from 'react';

const useAlerts = () => {
  const [alerts, setAlerts] = useState([]);

  const addAlert = useCallback((alert) => {
    const id = Date.now().toString();
    const newAlert = {
      id,
      variant: 'info',
      duration: 5000,
      ...alert
    };

    setAlerts(current => [...current, newAlert]);

    // Auto-remove alert after duration if specified
    if (newAlert.duration) {
      setTimeout(() => {
        removeAlert(id);
      }, newAlert.duration);
    }

    return id;
  }, []);

  const removeAlert = useCallback((id) => {
    setAlerts(current => current.filter(alert => alert.id !== id));
  }, []);

  const showSuccess = useCallback((message, options = {}) => {
    return addAlert({ variant: 'success', message, ...options });
  }, [addAlert]);

  const showError = useCallback((message, options = {}) => {
    return addAlert({ variant: 'error', message, ...options });
  }, [addAlert]);

  const showWarning = useCallback((message, options = {}) => {
    return addAlert({ variant: 'warning', message, ...options });
  }, [addAlert]);

  const showInfo = useCallback((message, options = {}) => {
    return addAlert({ variant: 'info', message, ...options });
  }, [addAlert]);

  return {
    alerts,
    addAlert,
    removeAlert,
    showSuccess,
    showError,
    showWarning,
    showInfo
  };
};

export default useAlerts;