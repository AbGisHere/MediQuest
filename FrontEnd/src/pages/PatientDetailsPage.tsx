import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { ArrowLeft, User, Phone, Mail, Calendar, Activity, Heart, AlertTriangle, FileText } from 'lucide-react';
import apiService from '../services/api';
import type { Patient, Vital, Alert } from '../types';

const PatientDetailsPage: React.FC = () => {
  const { patientId } = useParams<{ patientId: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [patient, setPatient] = useState<Patient | null>(null);
  const [vitals, setVitals] = useState<Vital[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPatientDetails = async () => {
      if (!patientId) return;
      
      try {
        setLoading(true);
        // Fetch patient details
        const patientData = await apiService.getPatientById(patientId);
        setPatient(patientData);
        
        // Fetch patient vitals
        const vitalsData = await apiService.getPatientVitals(patientId);
        setVitals(vitalsData);
        
        // Fetch patient alerts
        const alertsData = await apiService.getPatientAlerts(patientId);
        setAlerts(alertsData);
      } catch (error: any) {
        console.error('Error fetching patient details:', error);
        if (error?.response?.status === 403) {
          // Handle consent error specifically
          setError('Access denied: You do not have consent to view this patient\'s details.');
        } else if (error?.response?.status === 404) {
          setError('Patient not found.');
        } else {
          setError('Failed to load patient details.');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchPatientDetails();
  }, [patientId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!patient) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold text-gray-900">
          {error || "Patient Not Found"}
        </h2>
        <p className="mt-2 text-gray-600">
          {error || "The patient you're looking for doesn't exist."}
        </p>
        <button
          onClick={() => navigate('/patients')}
          className="mt-4 btn btn-primary"
        >
          Back to Patients
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => navigate('/patients')}
            className="p-2 text-gray-600 hover:text-gray-900"
          >
            <ArrowLeft className="h-5 w-5" />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              {patient.first_name} {patient.last_name}
            </h1>
            <p className="text-sm text-gray-600">Patient Details</p>
          </div>
        </div>
        <div className="flex space-x-3">
          <button className="btn btn-outline btn-md">
            <FileText className="h-4 w-4 mr-2" />
            Generate Report
          </button>
          <button className="btn btn-primary btn-md">
            <Activity className="h-4 w-4 mr-2" />
            Record Vitals
          </button>
        </div>
      </div>

      {/* Patient Information Card */}
      <div className="card p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Patient Information</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="flex items-center space-x-3">
            <div className="h-12 w-12 rounded-full bg-primary-100 flex items-center justify-center">
              <User className="h-6 w-6 text-primary-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-900">Full Name</p>
              <p className="text-sm text-gray-600">{patient.first_name} {patient.last_name}</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-3">
            <div className="h-12 w-12 rounded-full bg-blue-100 flex items-center justify-center">
              <Calendar className="h-6 w-6 text-blue-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-900">Date of Birth</p>
              <p className="text-sm text-gray-600">
                {new Date(patient.date_of_birth).toLocaleDateString()} 
                <span className="ml-2 text-xs text-gray-500">
                  ({Math.floor((new Date().getTime() - new Date(patient.date_of_birth).getTime()) / (365.25 * 24 * 60 * 60 * 1000))} years)
                </span>
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-3">
            <div className="h-12 w-12 rounded-full bg-red-100 flex items-center justify-center">
              <Heart className="h-6 w-6 text-red-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-900">Blood Group</p>
              <p className="text-sm text-gray-600">{patient.blood_group || 'Not specified'}</p>
            </div>
          </div>
          
          {patient.email && (
            <div className="flex items-center space-x-3">
              <div className="h-12 w-12 rounded-full bg-green-100 flex items-center justify-center">
                <Mail className="h-6 w-6 text-green-600" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-900">Email</p>
                <p className="text-sm text-gray-600">{patient.email}</p>
              </div>
            </div>
          )}
          
          {patient.phone && (
            <div className="flex items-center space-x-3">
              <div className="h-12 w-12 rounded-full bg-purple-100 flex items-center justify-center">
                <Phone className="h-6 w-6 text-purple-600" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-900">Phone</p>
                <p className="text-sm text-gray-600">{patient.phone}</p>
              </div>
            </div>
          )}
          
          <div className="flex items-center space-x-3">
            <div className="h-12 w-12 rounded-full bg-yellow-100 flex items-center justify-center">
              <AlertTriangle className="h-6 w-6 text-yellow-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-900">Status</p>
              <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                patient.is_active
                  ? 'bg-green-100 text-green-800'
                  : 'bg-red-100 text-red-800'
              }`}>
                {patient.is_active ? 'Active' : 'Inactive'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Vitals */}
      <div className="card p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">Recent Vitals</h3>
          <Activity className="h-5 w-5 text-gray-400" />
        </div>
        <div className="space-y-3">
          {vitals.length > 0 ? (
            vitals.slice(0, 5).map((vital) => (
              <div key={vital.id} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                <div>
                  <p className="text-sm font-medium text-gray-900">{vital.vital_type}</p>
                  <p className="text-xs text-gray-500">
                    {new Date(vital.recorded_at).toLocaleDateString()}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-semibold text-gray-900">
                    {vital.value} {vital.unit}
                  </p>
                  <p className="text-xs text-gray-500">{vital.source}</p>
                </div>
              </div>
            ))
          ) : (
            <p className="text-sm text-gray-500">No vitals recorded</p>
          )}
        </div>
      </div>

      {/* Active Alerts */}
      <div className="card p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">Active Alerts</h3>
          <AlertTriangle className="h-5 w-5 text-gray-400" />
        </div>
        <div className="space-y-3">
          {alerts.length > 0 ? (
            alerts.slice(0, 5).map((alert) => (
              <div
                key={alert.id}
                className={`p-3 rounded border-l-4 ${
                  alert.severity === 'critical'
                    ? 'bg-red-50 border-red-500'
                    : alert.severity === 'warning'
                      ? 'bg-yellow-50 border-yellow-500'
                      : 'bg-blue-50 border-blue-500'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-900">{alert.title}</p>
                    <p className="text-xs text-gray-500">{alert.description || 'No description available'}</p>
                  </div>
                  <span
                    className={`px-2 py-1 text-xs font-medium rounded ${
                      alert.severity === 'critical'
                        ? 'bg-red-100 text-red-800'
                        : alert.severity === 'warning'
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-blue-100 text-blue-800'
                    }`}
                  >
                    {alert.severity}
                  </span>
                </div>
              </div>
            ))
          ) : (
            <p className="text-sm text-gray-500">No active alerts</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default PatientDetailsPage;
