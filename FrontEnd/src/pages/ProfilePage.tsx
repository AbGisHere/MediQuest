import React, { useState, useEffect } from 'react';
import { User, Camera, Edit, Shield, Bell } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const ProfilePage: React.FC = () => {
  const { user } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    first_name: user?.first_name || '',
    last_name: user?.last_name || '',
    email: user?.email || '',
    phone: user?.phone || '',
    date_of_birth: user?.date_of_birth || '',
    blood_group: user?.blood_group || '',
    address: user?.address || '',
    emergency_contact_name: user?.emergency_contact_name || '',
    emergency_contact_phone: user?.emergency_contact_phone || ''
  });

  useEffect(() => {
    if (user) {
      setFormData({
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        email: user.email || '',
        phone: user.phone || '',
        date_of_birth: user.date_of_birth || '',
        blood_group: user.blood_group || '',
        address: user.address || '',
        emergency_contact_name: user.emergency_contact_name || '',
        emergency_contact_phone: user.emergency_contact_phone || ''
      });
    }
  }, [user]);

  const handleSaveProfile = async () => {
    try {
      console.log('Saving profile...', formData);
      // In a real app, this would call API to update profile
      alert('Profile updated successfully!');
      setIsEditing(false);
    } catch (error) {
      console.error('Error saving profile:', error);
      alert('Failed to update profile');
    }
  };

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">My Profile</h1>
          <p className="text-sm text-gray-600">Manage your personal information and preferences</p>
        </div>
        <div className="flex space-x-3">
          {!isEditing ? (
            <button 
              onClick={() => setIsEditing(true)}
              className="btn btn-primary"
            >
              <Edit className="h-4 w-4 mr-2" />
              Edit Profile
            </button>
          ) : (
            <div className="flex space-x-3">
              <button 
                onClick={handleSaveProfile}
                className="btn btn-primary"
              >
                Save Changes
              </button>
              <button 
                onClick={() => setIsEditing(false)}
                className="btn btn-outline"
              >
                Cancel
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Profile Information */}
      <div className="card p-6">
        <div className="flex items-center mb-6">
          <div className="h-24 w-24 rounded-full bg-gray-200 flex items-center justify-center mr-6">
            <User className="h-12 w-12 text-gray-400" />
          </div>
          <div className="flex-1">
            <h2 className="text-xl font-semibold text-gray-900">
              {user?.first_name} {user?.last_name}
            </h2>
            <p className="text-sm text-gray-600">{user?.email}</p>
          </div>
          {!isEditing && (
            <button className="p-2 rounded-full bg-blue-100 text-blue-600 hover:bg-blue-200">
              <Camera className="h-4 w-4" />
            </button>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Basic Information</h3>
            
            <div>
              <label className="block text-sm font-medium text-gray-700">First Name</label>
              <input
                type="text"
                value={formData.first_name}
                onChange={(e) => handleInputChange('first_name', e.target.value)}
                disabled={!isEditing}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:border-primary-500 focus:ring-primary-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Last Name</label>
              <input
                type="text"
                value={formData.last_name}
                onChange={(e) => handleInputChange('last_name', e.target.value)}
                disabled={!isEditing}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:border-primary-500 focus:ring-primary-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Email</label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) => handleInputChange('email', e.target.value)}
                disabled={!isEditing}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:border-primary-500 focus:ring-primary-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Phone</label>
              <input
                type="tel"
                value={formData.phone}
                onChange={(e) => handleInputChange('phone', e.target.value)}
                disabled={!isEditing}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:border-primary-500 focus:ring-primary-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Date of Birth</label>
              <input
                type="date"
                value={formData.date_of_birth}
                onChange={(e) => handleInputChange('date_of_birth', e.target.value)}
                disabled={!isEditing}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:border-primary-500 focus:ring-primary-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Blood Group</label>
              <select
                value={formData.blood_group}
                onChange={(e) => handleInputChange('blood_group', e.target.value)}
                disabled={!isEditing}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:border-primary-500 focus:ring-primary-500"
              >
                <option value="">Select Blood Group</option>
                <option value="A+">A+</option>
                <option value="A-">A-</option>
                <option value="B+">B+</option>
                <option value="B-">B-</option>
                <option value="AB+">AB+</option>
                <option value="AB-">AB-</option>
                <option value="O+">O+</option>
                <option value="O-">O-</option>
              </select>
            </div>
          </div>

          <div className="space-y-4">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Address</h3>
            
            <div>
              <label className="block text-sm font-medium text-gray-700">Address</label>
              <textarea
                value={formData.address}
                onChange={(e) => handleInputChange('address', e.target.value)}
                disabled={!isEditing}
                rows={3}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:border-primary-500 focus:ring-primary-500"
              />
            </div>
          </div>

          <div className="space-y-4">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Emergency Contact</h3>
            
            <div>
              <label className="block text-sm font-medium text-gray-700">Contact Name</label>
              <input
                type="text"
                value={formData.emergency_contact_name}
                onChange={(e) => handleInputChange('emergency_contact_name', e.target.value)}
                disabled={!isEditing}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:border-primary-500 focus:ring-primary-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Contact Phone</label>
              <input
                type="tel"
                value={formData.emergency_contact_phone}
                onChange={(e) => handleInputChange('emergency_contact_phone', e.target.value)}
                disabled={!isEditing}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:border-primary-500 focus:ring-primary-500"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Security Settings */}
      <div className="card p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Security Settings</h3>
        <div className="space-y-4">
          <button className="w-full text-left btn btn-outline">
            <Shield className="h-4 w-4 mr-2" />
            Change Password
          </button>
          <button className="w-full text-left btn btn-outline">
            <Bell className="h-4 w-4 mr-2" />
            Notification Preferences
          </button>
          <button className="w-full text-left btn btn-outline">
            <User className="h-4 w-4 mr-2" />
            Privacy Settings
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;
