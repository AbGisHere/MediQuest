import React, { useState, useEffect } from 'react';
import { Activity, Plus, Filter, Download, Clock, Heart, Thermometer, Droplets, Weight, FootprintsIcon, Moon, Flame } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import apiService from '../services/api';
import type { Vital } from '../types';

const VitalsPage: React.FC = () => {
  const { user } = useAuth();
  const [vitals, setVitals] = useState<Vital[]>([]);
  const [patients, setPatients] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedPatient, setSelectedPatient] = useState<string>('');
  const [selectedFilter, setSelectedFilter] = useState<string>('all');
  const [showAddForm, setShowAddForm] = useState(false);
  const [timeRange, setTimeRange] = useState<string>('7d');

  // Vital type configurations with icons and colors
  const vitalConfig = {
    heart_rate: { icon: Heart, color: 'red', unit: 'bpm', label: 'Heart Rate' },
    bp_systolic: { icon: Activity, color: 'orange', unit: 'mmHg', label: 'BP Systolic' },
    bp_diastolic: { icon: Activity, color: 'orange', unit: 'mmHg', label: 'BP Diastolic' },
    spo2: { icon: Droplets, color: 'blue', unit: '%', label: 'Oxygen Saturation' },
    temperature: { icon: Thermometer, color: 'yellow', unit: '°F', label: 'Temperature' },
    glucose: { icon: Flame, color: 'purple', unit: 'mg/dL', label: 'Blood Glucose' },
    weight: { icon: Weight, color: 'green', unit: 'kg', label: 'Weight' },
    height: { icon: Activity, color: 'gray', unit: 'cm', label: 'Height' },
    bmi: { icon: Activity, color: 'indigo', unit: 'kg/m²', label: 'BMI' },
    respiratory_rate: { icon: Activity, color: 'cyan', unit: 'bpm', label: 'Respiratory Rate' },
    steps: { icon: FootprintsIcon, color: 'pink', unit: 'steps', label: 'Steps' },
    sleep_hours: { icon: Moon, color: 'purple', unit: 'hours', label: 'Sleep Hours' },
    calories: { icon: Flame, color: 'orange', unit: 'kcal', label: 'Calories' }
  };

  useEffect(() => {
    const fetchPatients = async () => {
      if (user?.role !== 'patient') {
        try {
          const patientsData = await apiService.getPatientsWithConsent(0, 50);
          console.log('Fetched patients with consent:', patientsData);
          setPatients(patientsData);
          if (patientsData.length > 0 && !selectedPatient) {
            setSelectedPatient(patientsData[0].id);
            console.log('Auto-selected patient:', patientsData[0].id);
          }
        } catch (error) {
          console.error('Error fetching patients:', error);
          setPatients([]);
        }
      }
    };

    fetchPatients();
  }, [user, selectedPatient]);

  useEffect(() => {
    const fetchVitals = async () => {
      if (!selectedPatient) return;
      
      try {
        setLoading(true);
        const vitalsData = await apiService.getPatientVitals(selectedPatient, undefined, 100);
        console.log('Fetched vitals for patient:', selectedPatient, vitalsData);
        setVitals(vitalsData);
      } catch (error) {
        console.error('Error fetching vitals:', error);
        setVitals([]);
      } finally {
        setLoading(false);
      }
    };

    if (selectedPatient) {
      fetchVitals();
    }
  }, [selectedPatient]);

  const filteredVitals = vitals.filter(vital => {
    if (selectedFilter !== 'all' && vital.vital_type !== selectedFilter) {
      return false;
    }
    return true;
  });

  // Get latest readings for each vital type
  const getLatestReadings = () => {
    const latestReadings: { [key: string]: Vital } = {};
    
    filteredVitals.forEach((vital: Vital) => {
      if (!latestReadings[vital.vital_type] || 
          new Date(vital.recorded_at) > new Date(latestReadings[vital.vital_type].recorded_at)) {
        latestReadings[vital.vital_type] = vital;
      }
    });
    
    return Object.values(latestReadings);
  };

  // Get historical readings (all except latest)
  const getHistoricalReadings = () => {
    const latestReadings = getLatestReadings();
    const latestIds = new Set(latestReadings.map((v: Vital) => v.id));
    
    return filteredVitals.filter((vital: Vital) => !latestIds.has(vital.id))
                      .sort((a: Vital, b: Vital) => new Date(b.recorded_at).getTime() - new Date(a.recorded_at).getTime());
  };

  const latestReadings = getLatestReadings();
  const historicalReadings = getHistoricalReadings();

  const roundToTwo = (value: number): number => {
    return Math.round(value * 100) / 100;
  };

  const getVitalStatus = (type: string, value: number): 'normal' | 'warning' | 'critical' => {
    const config = vitalConfig[type as keyof typeof vitalConfig];
    if (!config) return 'normal';
    
    // Add basic status logic
    if (type === 'heart_rate') {
      if (value < 60 || value > 100) return 'warning';
      if (value < 40 || value > 120) return 'critical';
    } else if (type === 'spo2') {
      if (value < 95) return 'warning';
      if (value < 90) return 'critical';
    } else if (type === 'temperature') {
      if (value < 97 || value > 99) return 'warning';
      if (value < 95 || value > 101) return 'critical';
    }
    
    return 'normal';
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'normal': return 'text-green-600 bg-green-100';
      case 'warning': return 'text-yellow-600 bg-yellow-100';
      case 'critical': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Vital Signs</h1>
          <p className="mt-1 text-sm text-gray-600">Monitor and manage patient vital signs</p>
        </div>
        <div className="flex space-x-3">
          <button 
            onClick={() => setShowAddForm(true)}
            className="btn btn-primary"
          >
            <Plus className="h-4 w-4 mr-2" />
            Add Vitals
          </button>
          <button className="btn btn-outline">
            <Download className="h-4 w-4 mr-2" />
            Export
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="card p-4">
        <div className="flex flex-col lg:flex-row gap-4">
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-2">Patient</label>
            <select 
              value={selectedPatient}
              onChange={(e) => setSelectedPatient(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:border-primary-500 focus:ring-primary-500"
            >
              <option value="">Select a patient</option>
              {patients.map((patient) => (
                <option key={patient.id} value={patient.id}>
                  {patient.first_name} {patient.last_name}
                </option>
              ))}
            </select>
          </div>
          
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-2">Vital Type</label>
            <select 
              value={selectedFilter}
              onChange={(e) => setSelectedFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:border-primary-500 focus:ring-primary-500"
            >
              <option value="all">All Vitals</option>
              {Object.entries(vitalConfig).map(([key, config]) => (
                <option key={key} value={key}>{config.label}</option>
              ))}
            </select>
          </div>
          
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-2">Time Range</label>
            <select 
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:border-primary-500 focus:ring-primary-500"
            >
              <option value="24h">Last 24 Hours</option>
              <option value="7d">Last 7 Days</option>
              <option value="30d">Last 30 Days</option>
              <option value="90d">Last 90 Days</option>
            </select>
          </div>
        </div>
      </div>

      {/* Latest Readings Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {latestReadings.map((vital) => {
          const config = vitalConfig[vital.vital_type as keyof typeof vitalConfig];
          const Icon = config?.icon || Activity;
          const status = getVitalStatus(vital.vital_type, vital.value);
          
          return (
            <div key={vital.id} className="card p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className={`p-2 rounded-lg bg-${config?.color || 'gray'}-100`}>
                    <Icon className={`h-5 w-5 text-${config?.color || 'gray'}-600`} />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">{config?.label || vital.vital_type}</h3>
                    <p className="text-sm text-gray-600">
                      {new Date(vital.recorded_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>
                <div className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(status)}`}>
                  {status}
                </div>
              </div>
              
              <div className="text-center">
                <p className="text-3xl font-bold text-gray-900">{roundToTwo(vital.value)}</p>
                <p className="text-sm text-gray-600">{vital.unit}</p>
              </div>
              
              <div className="mt-4 pt-4 border-t">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">Source</span>
                  <span className="text-gray-900">{vital.source}</span>
                </div>
                <div className="flex items-center justify-between text-sm mt-1">
                  <span className="text-gray-600">Recorded</span>
                  <span className="text-gray-900">{new Date(vital.recorded_at).toLocaleTimeString()}</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Historical Readings List */}
      {historicalReadings.length > 0 && (
        <div className="card">
          <div className="p-6 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">Historical Readings</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Vital Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Value
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Source
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Recorded
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {historicalReadings.map((vital) => {
                  const config = vitalConfig[vital.vital_type as keyof typeof vitalConfig];
                  const Icon = config?.icon || Activity;
                  const status = getVitalStatus(vital.vital_type, vital.value);
                  
                  return (
                    <tr key={vital.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <Icon className={`h-4 w-4 mr-2 text-${config?.color || 'gray'}-600`} />
                          <span className="text-sm font-medium text-gray-900">
                            {config?.label || vital.vital_type}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          <span className="font-semibold">{roundToTwo(vital.value)}</span>
                          <span className="text-gray-500 ml-1">{vital.unit}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(status)}`}>
                          {status}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {vital.source}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(vital.recorded_at).toLocaleString()}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Empty State */}
      {filteredVitals.length === 0 && (
        <div className="text-center py-12">
          <Activity className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No vitals found</h3>
          <p className="text-sm text-gray-600">
            {selectedPatient ? 'No vitals have been recorded for this patient yet.' : 'Please select a patient to view their vitals.'}
          </p>
        </div>
      )}

      {/* Add Vitals Form Modal */}
      {showAddForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Add Vital Signs</h2>
            <form className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Vital Type</label>
                <select className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:border-primary-500 focus:ring-primary-500">
                  {Object.entries(vitalConfig).map(([key, config]) => (
                    <option key={key} value={key}>{config.label}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Value</label>
                <input type="number" step="0.1" className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:border-primary-500 focus:ring-primary-500" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Source</label>
                <input type="text" className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:border-primary-500 focus:ring-primary-500" />
              </div>
              <div className="flex space-x-3 pt-4">
                <button type="submit" className="btn btn-primary flex-1">Save</button>
                <button type="button" onClick={() => setShowAddForm(false)} className="btn btn-outline flex-1">Cancel</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default VitalsPage;
