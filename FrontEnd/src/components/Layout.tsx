import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Heart, Activity, Users, FileText, Settings, LogOut, User } from 'lucide-react';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { user, logout } = useAuth();

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: Heart },
    { name: 'Vitals', href: '/vitals', icon: Activity },
    { name: 'Patients', href: '/patients', icon: Users },
    { name: 'Blood Reports', href: '/blood-reports', icon: FileText },
    { name: 'Reports', href: '/reports', icon: FileText },
    { name: 'Settings', href: '/settings', icon: Settings },
  ];

  const patientNavigation = [
    { name: 'Dashboard', href: '/dashboard', icon: Heart },
    { name: 'My Vitals', href: '/my-vitals', icon: Activity },
    { name: 'My Profile', href: '/profile', icon: User },
    { name: 'Consent', href: '/consent', icon: FileText },
    { name: 'Settings', href: '/settings', icon: Settings },
  ];

  const currentNavigation = user?.role === 'patient' ? patientNavigation : navigation;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              {/* Logo */}
              <div className="flex-shrink-0 flex items-center">
                <Heart className="h-8 w-8 text-primary-600" />
                <span className="ml-2 text-xl font-bold text-gray-900">MediQuest</span>
              </div>

              {/* Navigation Links */}
              <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                {currentNavigation.map((item) => {
                  const Icon = item.icon;
                  return (
                    <NavLink
                      key={item.name}
                      to={item.href}
                      className={({ isActive }) =>
                        `inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${
                          isActive
                            ? 'border-primary-500 text-gray-900'
                            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                        }`
                      }
                    >
                      <Icon className="h-4 w-4 mr-2" />
                      {item.name}
                    </NavLink>
                  );
                })}
              </div>
            </div>

            {/* User Menu */}
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className="text-sm">
                  <p className="font-medium text-gray-900">{user?.username}</p>
                  <p className="text-gray-500 capitalize">{user?.role}</p>
                </div>
                <div className="h-8 w-8 rounded-full bg-primary-100 flex items-center justify-center">
                  <User className="h-4 w-4 text-primary-600" />
                </div>
              </div>
              <button
                onClick={logout}
                className="btn btn-outline btn-sm flex items-center"
              >
                <LogOut className="h-4 w-4 mr-2" />
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {children}
        </div>
      </main>
    </div>
  );
};

export default Layout;
