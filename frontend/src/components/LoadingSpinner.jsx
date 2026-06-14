import React from 'react';

const LoadingSpinner = ({ size, variant }) => (
  <div className={`animate-spin rounded-full border-b-2 border-orange-500 ${size === 'xl' ? 'h-12 w-12' : 'h-8 w-8'}`}></div>
);

export default LoadingSpinner;
