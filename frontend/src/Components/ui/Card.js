import React from 'react';

const Card = ({ children, className }) => {
  return (
    <div className={`bg-white shadow-md rounded-lg p-4 ${className}`}>
      {children}
    </div>
  );
};

export const CardHeader = ({ children }) => (
  <div className="border-b border-gray-200 pb-2 mb-2">{children}</div>
);

export const CardContent = ({ children }) => (
  <div className="text-gray-700">{children}</div>
);

export const CardTitle = ({ children }) => (
  <h3 className="text-lg font-semibold text-gray-900">{children}</h3>
);

export default Card;