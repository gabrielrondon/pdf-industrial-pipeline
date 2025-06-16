import React from 'react';

function Header() {
  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold text-gray-900">
          PDF Industrial Pipeline
        </h1>
        <div className="flex items-center space-x-4">
          <span className="text-sm text-gray-500">v0.0.6</span>
        </div>
      </div>
    </header>
  );
}

export default Header; 