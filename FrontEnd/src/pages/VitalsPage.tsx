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
      if (!selectedPatient) {
        console.log('No patient selected, skipping vitals fetch');
        return;
      }
      
      try {
        setLoading(true);
        console.log('Fetching vitals for patient:', selectedPatient);
        
        if (user?.role !== 'patient') {
          const vitalsData = await apiService.getPatientVitals(selectedPatient, undefined, 100);
          console.log('Received vitals:', vitalsData);
          setVitals(vitalsData);
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

    if (selectedPatient) {
      fetchVitals();
    }
  }, [user, selectedPatient]);

  // Filter vitals based on selected type
  const filteredVitals = vitals.filter(vital => {
    if (selectedFilter === 'all') return true;
    return vital.vital_type === selectedFilter;
  });

  // Get latest readings for each vital type
  const getLatestReadings = () => {
    const latest: { [key: string]: Vital } = {};
    vitals.forEach(vital => {
      if (!latest[vital.vital_type] || vital.recorded_at > latest[vital.vital_type].recorded_at) {
        latest[vital.vital_type] = vital;
      }
    });
    return latest;
  };

  const latestReadings = getLatestReadings();

  // Helper function to round values to 2 decimal places
  const roundToTwo = (value: number): number => {
    return Math.round(value * 100) / 100;
  };

  const getNormalRange = (vitalType: string, value: number) => {
    const ranges: { [key: string]: { min: number; max: number } } = {
      heart_rate: { min: 60, max: 100 },
      bp_systolic: { min: 90, max: 120 },
      bp_diastolic: { min: 60, max: 80 },
      spo2: { min: 95, max: 100 },
      temperature: { min: 97.0, max: 99.0 },
      glucose: { min: 70, max: 100 },
      respiratory_rate: { min: 12, max: 20 }
    };
    
    const range = ranges[vitalType];
    if (!range) return 'normal';
    
    if (value < range.min) return 'low';
    if (value > range.max) return 'high';
    return 'normal';
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'low': return 'text-blue-600 bg-blue-50';
      case 'high': return 'text-red-600 bg-red-50';
      default: return 'text-green-600 bg-green-50';
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
          <h1 className="text-3xl font-bold text-gray-900">Vitals Monitoring</h1>
          <p className="mt-1 text-sm text-gray-600">Comprehensive vital signs analysis and tracking</p>
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

      {/* Patient Selection */}
      {user?.role !== 'patient' && (
        <div className="card p-4">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div className="flex items-center space-x-2">
              <label className="text-sm font-medium text-gray-700">Patient:</label>
              <select 
                value={selectedPatient}
                onChange={(e) => setSelectedPatient(e.target.value)}
                className="border-gray-300 rounded-md shadow-sm focus:border-primary-500 focus:ring-primary-500 min-w-[200px]"
              >
                {patients.map((patient) => (
                  <option key={patient.id} value={patient.id}>
                    {patient.first_name} {patient.last_name}
                  </option>
                ))}
              </select>
            </div>
            
            <div className="flex items-center space-x-2">
              <label className="text-sm font-medium text-gray-700">Time Range:</label>
              <select 
                value={timeRange}
                onChange={(e) => setTimeRange(e.target.value)}
                className="border-gray-300 rounded-md shadow-sm focus:border-primary-500 focus:ring-primary-500"
              >
                <option value="24h">Last 24 Hours</option>
                <option value="7d">Last 7 Days</option>
                <option value="30d">Last 30 Days</option>
                <option value="all">All Time</option>
              </select>
            </div>
          </div>
        </div>
      )}

      {/* Latest Readings Dashboard */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {Object.entries(latestReadings).map(([vitalType, vital]) => {
          const config = vitalConfig[vitalType as keyof typeof vitalConfig];
          const status = getNormalRange(vitalType, vital.value);
          const statusColor = getStatusColor(status);
          const Icon = config?.icon || Activity;
          
          return (
            <div key={vitalType} className="card p-6 hover:shadow-lg transition-shadow">
              <div className="flex items-center justify-between mb-4">
                <div className={`p-2 rounded-lg bg-${config?.color}-100`}>
                  <Icon className={`h-5 w-5 text-${config?.color}-600`} />
                </div>
                <span className={`px-2 py-1 text-xs font-medium rounded-full ${statusColor}`}>
                  {status}
                </span>
              </div>
              
              <div>
                <p className="text-sm font-medium text-gray-600">{config?.label}</p>
                <p className="text-2xl font-bold text-gray-900">
                  {roundToTwo(vital.value)} <span className="text-sm text-gray-500">{config?.unit}</span>
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  {new Date(vital.recorded_at).toLocaleString()}
                </p>
              </div>
            </div>
          );
        })}
      </div>

      {/* Filters and Detailed View */}
      <div className="card p-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
          <div className="flex items-center space-x-2">
            <Filter className="h-4 w-4 text-gray-400" />
            <select 
              value={selectedFilter}
              onChange={(e) => setSelectedFilter(e.target.value)}
              className="border-gray-300 rounded-md shadow-sm focus:border-primary-500 focus:ring-primary-500"
            >
              <option value="all">All Vitals</option>
              {Object.entries(vitalConfig).map(([key, config]) => (
                <option key={key} value={key}>{config.label}</option>
              ))}
            </select>
          </div>
          
          <div className="text-sm text-gray-500">
            Showing {filteredVitals.length} of {vitals.length} measurements
          </div>
        </div>

        {/* Vitals Table */}
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Date & Time
                </th>
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
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredVitals.length > 0 ? (
                filteredVitals.map((vital) => {
                  const config = vitalConfig[vital.vital_type as keyof typeof vitalConfig];
                  const status = getNormalRange(vital.vital_type, vital.value);
                  const statusColor = getStatusColor(status);
                  const Icon = config?.icon || Activity;
                  
                  return (
                    <tr key={vital.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        <div className="flex items-center">
                          <Clock className="h-4 w-4 text-gray-400 mr-2" />
                          {new Date(vital.recorded_at).toLocaleString()}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <Icon className={`h-4 w-4 text-${config?.color}-600 mr-2`} />
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
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${statusColor}`}>
                          {status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {vital.source}
                      </td>
                    </tr>
                  );
                })
              ) : (
                <tr>
                  <td colSpan={5} className="px-6 py-12 text-center text-gray-500">
                    <Activity className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-lg font-medium text-gray-900 mb-2">No vitals found</p>
                    <p className="text-sm">
                      {selectedFilter === 'all' 
                        ? 'No vitals recorded for this patient yet.' 
                        : `No ${vitalConfig[selectedFilter as keyof typeof vitalConfig]?.label || selectedFilter} measurements found.`
                      }
                    </p>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Add Vital Form Modal - Placeholder */}
      {showAddForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full shadow-xl">
            <h2 className="text-xl font-bold mb-4 text-gray-900">Record New Vital</h2>
            <p className="text-gray-600 mb-6">Add a new vital measurement for {patients.find(p => p.id === selectedPatient)?.first_name}</p>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Vital Type</label>
                <select className="w-full border-gray-300 rounded-md shadow-sm focus:border-primary-500 focus:ring-primary-500">
                  {Object.entries(vitalConfig).map(([key, config]) => (
                    <option key={key} value={key}>{config.label}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Value</label>
                <input type="number" className="w-full border-gray-300 rounded-md shadow-sm focus:border-primary-500 focus:ring-primary-500" placeholder="Enter value" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Notes (optional)</label>
                <textarea className="w-full border-gray-300 rounded-md shadow-sm focus:border-primary-500 focus:ring-primary-500" rows={3} placeholder="Add any notes..."></textarea>
              </div>
            </div>
            <div className="flex justify-end space-x-3 mt-6">
              <button
                onClick={() => setShowAddForm(false)}
                className="btn btn-secondary"
              >
                Cancel
              </button>
              <button
                onClick={() => setShowAddForm(false)}
                className="btn btn-primary"
              >
                Save Vital
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default VitalsPage;
