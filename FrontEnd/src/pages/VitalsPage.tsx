import React, { useState, useEffect } from 'react';
import { Activity, TrendingUp, AlertTriangle, Plus, Filter, Download } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import apiService from '../services/api';
import type { Vital } from '../types';

const VitalsPage: React.FC = () => {
  const { user } = useAuth();
  const [vitals, setVitals] = useState<Vital[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedPatient, setSelectedPatient] = useState<string>('aa7e877b-10cd-442b-bd38-b622cecb9629');
  const [selectedFilter, setSelectedFilter] = useState<string>('all');
  const [showAddForm, setShowAddForm] = useState(false);

  useEffect(() => {
    const fetchVitals = async () => {
      try {
        setLoading(true);
        // For doctors/admins, fetch vitals for selected patient
        if (user?.role !== 'patient') {
          const vitalsData = await apiService.getPatientVitals(selectedPatient, undefined, 50);
          setVitals(vitalsData);
        } else {
          setVitals([]);
        }
      } catch (error) {
        console.error('Error fetching vitals:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchVitals();
  }, [user, selectedPatient]);

  const handleAddVital = async (vitalData: any) => {
    try {
      const newVital = await apiService.uploadVital({
        ...vitalData,
        patient_id: selectedPatient,
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

  const filteredVitals = vitals.filter(vital => {
    if (selectedFilter === 'all') return true;
    return vital.vital_type.includes(selectedFilter);
  });

  const vitalStats = {
    total: filteredVitals.length,
    average: filteredVitals.length > 0 ? filteredVitals.reduce((sum, v) => sum + v.value, 0) / filteredVitals.length : 0,
    latest: filteredVitals[0],
    critical: filteredVitals.filter(v => v.value > 120).length // Example threshold
  };

  const vitalTypes = [
    { value: 'all', label: 'All Vitals' },
    { value: 'heart', label: 'Heart Rate' },
    { value: 'blood', label: 'Blood Pressure' },
    { value: 'temperature', label: 'Temperature' },
    { value: 'oxygen', label: 'Oxygen Saturation' },
    { value: 'sugar', label: 'Blood Sugar' }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Vitals Monitoring</h1>
          <p className="text-sm text-gray-600">Monitor and analyze patient vital signs</p>
        </div>
        <div className="flex space-x-3">
          <button 
            onClick={() => setShowAddForm(true)}
            className="btn btn-primary"
          >
            <Plus className="h-4 w-4 mr-2" />
            Record Vitals
          </button>
          <button className="btn btn-outline">
            <Download className="h-4 w-4 mr-2" />
            Export Data
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="card p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Filter className="h-4 w-4 text-gray-400" />
            <select 
              value={selectedFilter}
              onChange={(e) => setSelectedFilter(e.target.value)}
              className="border-gray-300 rounded-md shadow-sm focus:border-primary-500 focus:ring-primary-500"
            >
              {vitalTypes.map(type => (
                <option key={type.value} value={type.value}>{type.label}</option>
              ))}
            </select>
          </div>
          
          {user?.role !== 'patient' && (
            <div className="flex items-center space-x-2">
              <label className="text-sm font-medium text-gray-700">Patient:</label>
              <select 
                value={selectedPatient}
                onChange={(e) => setSelectedPatient(e.target.value)}
                className="border-gray-300 rounded-md shadow-sm focus:border-primary-500 focus:ring-primary-500"
              >
                <option value="aa7e877b-10cd-442b-bd38-b622cecb9629">John Doe</option>
                <option value="faff2b22-170b-428e-ba2e-4b7afcf1509d">Jane Smith</option>
                <option value="c036d38c-d4ce-4ac2-b124-f7d55d7fc2e4">Robert Johnson</option>
              </select>
            </div>
          )}
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="card p-6">
          <div className="flex items-center">
            <div className="p-3 rounded-full bg-blue-100 mr-4">
              <Activity className="h-6 w-6 text-blue-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-900">Total Vitals</p>
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
              <p className="text-sm font-medium text-gray-900">Average Value</p>
              <p className="text-2xl font-bold text-green-600">{vitalStats.average.toFixed(1)}</p>
            </div>
          </div>
        </div>
        
        <div className="card p-6">
          <div className="flex items-center">
            <div className="p-3 rounded-full bg-purple-100 mr-4">
              <Activity className="h-6 w-6 text-purple-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-900">Latest Reading</p>
              <p className="text-lg font-bold text-purple-600">
                {vitalStats.latest ? `${vitalStats.latest.value} ${vitalStats.latest.unit}` : 'N/A'}
              </p>
            </div>
          </div>
        </div>
        
        <div className="card p-6">
          <div className="flex items-center">
            <div className="p-3 rounded-full bg-red-100 mr-4">
              <AlertTriangle className="h-6 w-6 text-red-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-900">Critical Alerts</p>
              <p className="text-2xl font-bold text-red-600">{vitalStats.critical}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Add Vital Form */}
      {showAddForm && (
        <div className="card p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Record New Vital</h3>
          <form onSubmit={(e) => { e.preventDefault(); handleAddVital(e.target); }}>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
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
                Record Vital
              </button>
              <button type="button" onClick={() => setShowAddForm(false)} className="btn btn-outline">
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Vitals Table */}
      <div className="card p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Vitals History</h3>
        
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          </div>
        ) : filteredVitals.length === 0 ? (
          <div className="text-center py-12">
            <Activity className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">No vitals found</p>
            <p className="text-sm text-gray-600">Try adjusting filters or recording new vitals</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Value</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Unit</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Source</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredVitals.map((vital) => (
                  <tr key={vital.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {vital.vital_type.replace(/_/g, ' ').toUpperCase()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      <span className={`font-semibold ${
                        vital.value > 120 ? 'text-red-600' : 
                        vital.value > 100 ? 'text-yellow-600' : 
                        'text-green-600'
                      }`}>
                        {vital.value}
                      </span> {vital.unit}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {vital.source}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(vital.recorded_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <span className={`px-2 py-1 text-xs font-medium rounded ${
                        vital.value > 120 
                          ? 'bg-red-100 text-red-800' 
                          : vital.value > 100
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-green-100 text-green-800'
                      }`}>
                        {vital.value > 120 ? 'Critical' : vital.value > 100 ? 'Warning' : 'Normal'}
                      </span>
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

export default VitalsPage;
