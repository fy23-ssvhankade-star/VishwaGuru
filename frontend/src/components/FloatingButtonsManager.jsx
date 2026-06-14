import React from 'react';

const FloatingButtonsManager = ({ setView }) => (
  <div className="fixed bottom-4 right-4 flex flex-col gap-2 z-40">
    <button onClick={() => setView('report')} className="bg-blue-600 text-white p-4 rounded-full shadow-lg hover:bg-blue-700 transition">
      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 5v14M5 12h14"/></svg>
    </button>
  </div>
);

export default FloatingButtonsManager;
