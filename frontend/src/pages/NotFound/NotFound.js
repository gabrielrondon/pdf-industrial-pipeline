import React from 'react';
import { Link } from 'react-router-dom';

function NotFound() {
  return (
    <div className="text-center py-12">
      <h1 className="text-4xl font-bold text-gray-900">404</h1>
      <p className="text-lg text-gray-600 mt-2">Página não encontrada</p>
      <Link to="/dashboard" className="btn-primary mt-4">
        Voltar ao Dashboard
      </Link>
    </div>
  );
}

export default NotFound; 