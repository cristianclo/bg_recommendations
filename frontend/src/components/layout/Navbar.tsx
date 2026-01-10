import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Home, Gamepad2, Star, FileText } from 'lucide-react';

export const Navbar: React.FC = () => {
  const location = useLocation();
  
  const isActive = (path: string) => {
    return location.pathname === path || location.pathname.startsWith(path);
  };

  const navItems = [
    { path: '/', label: 'Inicio', icon: Home },
    { path: '/sessions/new', label: 'Nueva Sesión', icon: FileText },
    { path: '/games', label: 'Catálogo', icon: Gamepad2 },
    { path: '/skills', label: 'Habilidades', icon: Star },
  ];

  return (
    <nav className="bg-white shadow-sm border-b">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            {/* Logo */}
            <div className="flex-shrink-0 flex items-center">
              <Link to="/" className="flex items-center">
                <Gamepad2 className="h-8 w-8 text-blue-600" />
                <span className="ml-2 text-xl font-bold text-gray-900">
                  CJEI Recomendaciones
                </span>
              </Link>
            </div>
            
            {/* Navigation Links */}
            <div className="hidden sm:ml-8 sm:flex sm:space-x-4">
              {navItems.map((item) => {
                const Icon = item.icon;
                const active = isActive(item.path);
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={`inline-flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                      active
                        ? 'bg-blue-50 text-blue-700'
                        : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
                    }`}
                  >
                    <Icon className={`mr-2 h-4 w-4 ${active ? 'text-blue-700' : 'text-gray-500'}`} />
                    {item.label}
                  </Link>
                );
              })}
            </div>
          </div>

          {/* Right side - could add user menu here */}
          <div className="flex items-center">
            <span className="text-sm text-gray-500">
              Sistema de Recomendación CJEI
            </span>
          </div>
        </div>
      </div>

      {/* Mobile menu */}
      <div className="sm:hidden border-t">
        <div className="px-2 pt-2 pb-3 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const active = isActive(item.path);
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center px-3 py-2 text-base font-medium rounded-md ${
                  active
                    ? 'bg-blue-50 text-blue-700'
                    : 'text-gray-700 hover:bg-gray-50'
                }`}
              >
                <Icon className="mr-3 h-5 w-5" />
                {item.label}
              </Link>
            );
          })}
        </div>
      </div>
    </nav>
  );
};
