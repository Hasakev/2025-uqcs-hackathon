import React from 'react';
import { Link, useLocation } from 'react-router-dom';

const Navigation = () => {
  const { pathname } = useLocation();

  return (
    <nav className="bg-white border-b">
      <div className="container mx-auto px-4 h-14 flex items-center justify-between">
        <div className="text-lg font-semibold">Blackboard Bets</div>
        <div className="flex items-center gap-4">
          <Link
            to="/"
            className={`px-3 py-2 rounded-md text-sm ${
              pathname === '/'
                ? 'text-blue-700 bg-blue-100'
                : 'text-gray-600 hover:text-blue-600 hover:bg-blue-50'
            }`}
          >
            Dashboard
          </Link>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;