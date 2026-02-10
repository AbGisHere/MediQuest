import React, { useState } from 'react';
import { Settings, User, Bell, Shield, Database } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const SettingsPage: React.FC = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('profile');
  const [notifications, setNotifications] = useState({
    email: true,
    push: true,
    alerts: true,
    reports: false
  });

  const handleSaveSettings = () => {
    console.log('Saving settings...');
    // In a real app, this would save to backend
    alert('Settings saved successfully!');
  };

  const tabs = [
    { id: 'profile', label: 'Profile Settings', icon: User },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'privacy', label: 'Privacy & Security', icon: Shield },
    { id: 'data', label: 'Data Management', icon: Database }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
        <p className="text-sm text-gray-600">Manage your account settings and preferences</p>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon className="h-5 w-5 mr-2" />
                {tab.label}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="mt-6">
        {activeTab === 'profile' && (
          <div className="card p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Profile Settings</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Full Name</label>
                <input
                  type="text"
                  defaultValue={`${user?.first_name || ''} ${user?.last_name || ''}`}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:border-primary-500 focus:ring-primary-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Email</label>
                <input
                  type="email"
                  defaultValue={user?.email || ''}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:border-primary-500 focus:ring-primary-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Role</label>
                <input
                  type="text"
                  value={user?.role || ''}
                  disabled
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm bg-gray-100"
                />
              </div>
            </div>
          </div>
        )}

        {activeTab === 'notifications' && (
          <div className="card p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Notification Preferences</h3>
            <div className="space-y-4">
              {Object.entries(notifications).map(([key, value]) => (
                <div key={key} className="flex items-center justify-between">
                  <div className="flex items-center">
                    <Bell className="h-4 w-4 text-gray-400 mr-3" />
                    <span className="text-sm font-medium text-gray-700 capitalize">{key}</span>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={value}
                      onChange={(e) => setNotifications(prev => ({ ...prev, [key]: e.target.checked }))}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-500 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-primary-600 peer-checked:after:bg-primary-600 after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                  </label>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'privacy' && (
          <div className="card p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Privacy & Security</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Current Password</label>
                <input
                  type="password"
                  placeholder="•••••••••"
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:border-primary-500 focus:ring-primary-500"
                />
              </div>
              <button className="btn btn-outline">Change Password</button>
              <button className="btn btn-outline">Enable Two-Factor Authentication</button>
            </div>
          </div>
        )}

        {activeTab === 'data' && (
          <div className="card p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Data Management</h3>
            <div className="space-y-4">
              <button className="w-full text-left btn btn-outline">
                <Database className="h-4 w-4 mr-2" />
                Export My Data
              </button>
              <button className="w-full text-left btn btn-outline">
                <Shield className="h-4 w-4 mr-2" />
                Privacy Settings
              </button>
              <button className="w-full text-left btn btn-outline text-red-600">
                Delete My Account
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Save Button */}
      <div className="flex justify-end">
        <button
          onClick={handleSaveSettings}
          className="btn btn-primary"
        >
          Save Settings
        </button>
      </div>
    </div>
  );
};

export default SettingsPage;
