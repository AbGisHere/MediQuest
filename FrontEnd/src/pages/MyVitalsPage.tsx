import React, { useState, useEffect } from 'react';
import { Activity, TrendingUp, Plus, Download } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import apiService from '../services/api';
import type { Vital } from '../types';

const MyVitalsPage: React.FC = () => {
  const { user } = useAuth();
  const [vitals, setVitals] = useState<Vital[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);

  useEffect(() => {
    const fetchMyVitals = async () => {
      try {
        setLoading(true);
        // For patients, show their own vitals (for demo, use first available patient)
        if (user?.role === 'patient') {
          // Get patients and use first one for demo
          const patients = await apiService.getPatientsWithConsent(0, 10);
          if (patients.length > 0) {
            const vitalsData = await apiService.getPatientVitals(patients[0].id, undefined, 20);
            setVitals(vitalsData);
          }
        } else {
          setVitals([]);
        }
      } catch (error) {
        console.error('Error fetching vitals:', error);
        setVitals([]);
      } finally {
        setLoading(false);
      }
    };

    fetchMyVitals();
  }, [user]);

  const handleAddVital = async (vitalData: any) => {
    try {
      // Get first patient for demo
      const patients = await apiService.getPatientsWithConsent(0, 10);
      if (patients.length === 0) {
        alert('No patients available');
        return;
      }
      
      const newVital = await apiService.uploadVital({
        ...vitalData,
        patient_id: patients[0].id,
        recorded_at: new Date().toISOString(),
        source: 'manual'
      });
      
      setVitals(prev => [newVital, ...prev]);
      setShowAddForm(false);
      alert('Vital added successfully!');
    } catch (error) {
      console.error('Error adding vital:', error);
      alert('Failed to add vital');
    }
  };

  const vitalStats = {
    latest: vitals[0],
    total: vitals.length,
    average: vitals.length > 0 ? vitals.reduce((sum, v) => sum + v.value, 0) / vitals.length : 0
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">My Vitals</h1>
          <p className="text-sm text-gray-600">Track and monitor your personal health metrics</p>
        </div>
        <button 
          onClick={() => setShowAddForm(true)}
          className="btn btn-primary"
        >
          <Plus className="h-4 w-4 mr-2" />
          Add Vital
        </button>
      </div>

      {/* Add Vital Form */}
      {showAddForm && (
        <div className="card p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Add New Vital</h3>
          <form onSubmit={(e) => { e.preventDefault(); handleAddVital(e.target); }}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Vital Type</label>
                <select name="vital_type" required className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:border-primary-500 focus:ring-primary-500">
                  <option value="heart_rate">Heart Rate</option>
                  <option value="blood_pressure_systolic">Blood Pressure (Systolic)</option>
                  <option value="blood_pressure_diastolic">Blood Pressure (Diastolic)</option>
                  <option value="temperature">Body Temperature</option>
                  <option value="oxygen_saturation">Oxygen Saturation</option>
                  <option value="blood_sugar">Blood Sugar</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Value</label>
                <input
                  type="number"
                  name="value"
                  step="0.1"
                  required
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:border-primary-500 focus:ring-primary-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Unit</label>
                <input
                  type="text"
                  name="unit"
                  placeholder="e.g., bpm, mmHg, °F, %"
                  required
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:border-primary-500 focus:ring-primary-500"
                />
              </div>
            </div>
            <div className="flex justify-end space-x-3 mt-4">
              <button type="submit" className="btn btn-primary">
                Add Vital
              </button>
              <button type="button" onClick={() => setShowAddForm(false)} className="btn btn-outline">
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card p-6">
          <div className="flex items-center">
            <div className="p-3 rounded-full bg-blue-100 mr-4">
              <Activity className="h-6 w-6 text-blue-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-900">Total Records</p>
              <p className="text-2xl font-bold text-blue-600">{vitalStats.total}</p>
            </div>
          </div>
        </div>
        
        <div className="card p-6">
          <div className="flex items-center">
            <div className="p-3 rounded-full bg-green-100 mr-4">
              <TrendingUp className="h-6 w-6 text-green-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-900">Latest Reading</p>
              <p className="text-lg font-bold text-green-600">
                {vitalStats.latest ? `${vitalStats.latest.value} ${vitalStats.latest.unit}` : 'N/A'}
              </p>
            </div>
          </div>
        </div>
        
        <div className="card p-6">
          <div className="flex items-center">
            <div className="p-3 rounded-full bg-purple-100 mr-4">
              <Download className="h-6 w-6 text-purple-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-900">Export Data</p>
              <button className="mt-2 btn btn-outline btn-sm">
                Download CSV
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Vitals History */}
      <div className="card p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Vitals History</h3>
        
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          </div>
        ) : vitals.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-500">No vitals recorded yet</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Value</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Unit</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Source</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {vitals.map((vital) => (
                  <tr key={vital.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {vital.vital_type.replace(/_/g, ' ').toUpperCase()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {vital.value} {vital.unit}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(vital.recorded_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {vital.source}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default MyVitalsPage;
