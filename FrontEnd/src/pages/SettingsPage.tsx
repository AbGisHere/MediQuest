import React from 'react';
import { Settings } from 'lucide-react';

const SettingsPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
        <p className="mt-1 text-sm text-gray-600">Manage your account settings</p>
      </div>
      
      <div className="card p-6">
        <div className="flex items-center justify-center py-12">
          <Settings className="h-12 w-12 text-gray-400 mr-4" />
          <div>
            <h3 className="text-lg font-medium text-gray-900">Settings Page</h3>
            <p className="text-gray-500">This page is under construction</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;
