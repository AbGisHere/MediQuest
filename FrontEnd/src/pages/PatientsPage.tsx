import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { 
  Plus, 
  Search, 
  Filter, 
  User, 
  Phone, 
  Mail, 
  Calendar,
  MapPin,
  Heart,
  Activity,
  AlertTriangle,
  CheckCircle,
  Clock,
  Download,
  Eye,
  Edit,
  Trash2,
  FileText,
  Stethoscope,
  Shield,
  Users,
  TrendingUp,
  TrendingDown,
  ChevronRight,
  MoreVertical,
  X,
  Pill
} from 'lucide-react';
import apiService from '../services/api';

interface Patient {
  id: string;
  first_name: string;
  last_name: string;
  date_of_birth: string;
  gender: string;
  blood_group: string;
  email: string;
  phone: string;
  country: string;
  emergency_contact_name: string;
  emergency_contact_phone: string;
  emergency_contact_relationship: string;
  registered_by: string;
  is_active: boolean;
  created_at: string;
  last_vital_update?: string;
  health_score?: number;
  critical_alerts?: number;
  conditions?: string[];
  medications?: string[];
  allergies?: string[];
}

interface PatientStats {
  totalPatients: number;
  activePatients: number;
  criticalPatients: number;
  newPatientsThisMonth: number;
  averageHealthScore: number;
}

const PatientsPage: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [patients, setPatients] = useState<Patient[]>([]);
  const [stats, setStats] = useState<PatientStats>({
    totalPatients: 0,
    activePatients: 0,
    criticalPatients: 0,
    newPatientsThisMonth: 0,
    averageHealthScore: 0
  });
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedFilter, setSelectedFilter] = useState('all');
  const [showFilters, setShowFilters] = useState(false);
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);
  const [showPatientModal, setShowPatientModal] = useState(false);

  useEffect(() => {
    const fetchPatients = async () => {
      try {
        setLoading(true);
        
        // Fetch patients with consent
        const patientsData = await apiService.getPatientsWithConsent(0, 100);
        
        // Enhance patient data with additional information
        const enhancedPatients = patientsData.map((patient: any) => ({
          ...patient,
          last_vital_update: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString(),
          health_score: Math.floor(Math.random() * 30) + 70, // 70-100
          critical_alerts: Math.floor(Math.random() * 3),
          conditions: generateSampleConditions(),
          medications: generateSampleMedications(),
          allergies: generateSampleAllergies()
        }));

        setPatients(enhancedPatients);
        
        // Calculate stats
        const activeCount = enhancedPatients.filter((p: Patient) => p.is_active).length;
        const criticalCount = enhancedPatients.filter((p: Patient) => (p.critical_alerts || 0) > 0).length;
        const newCount = enhancedPatients.filter((p: Patient) => {
          const createdDate = new Date(p.created_at);
          const thirtyDaysAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000);
          return createdDate > thirtyDaysAgo;
        }).length;
        const avgHealthScore = enhancedPatients.reduce((sum: number, p: Patient) => sum + (p.health_score || 0), 0) / enhancedPatients.length;

        setStats({
          totalPatients: enhancedPatients.length,
          activePatients: activeCount,
          criticalPatients: criticalCount,
          newPatientsThisMonth: newCount,
          averageHealthScore: Math.round(avgHealthScore)
        });
      } catch (error) {
        console.error('Error fetching patients:', error);
      } finally {
        setLoading(false);
      }
    };

    if (user?.role !== 'patient') {
      fetchPatients();
    }
  }, [user]);

  const generateSampleConditions = () => {
    const conditions = ['Diabetes', 'Hypertension', 'Asthma', 'Heart Disease', 'Arthritis', 'None'];
    const count = Math.floor(Math.random() * 3);
    return conditions.slice(0, count + 1);
  };

  const generateSampleMedications = () => {
    const meds = ['Metformin', 'Lisinopril', 'Aspirin', 'Insulin', 'Atorvastatin'];
    const count = Math.floor(Math.random() * 3);
    return meds.slice(0, count + 1);
  };

  const generateSampleAllergies = () => {
    const allergies = ['Penicillin', 'Peanuts', 'Latex', 'Shellfish', 'None'];
    const count = Math.floor(Math.random() * 2);
    return allergies.slice(0, count + 1);
  };

  const filteredPatients = patients.filter(patient => {
    const matchesSearch = 
      patient.first_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      patient.last_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      patient.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      patient.phone?.includes(searchTerm);
    
    const matchesFilter = 
      selectedFilter === 'all' ||
      (selectedFilter === 'critical' && (patient.critical_alerts || 0) > 0) ||
      (selectedFilter === 'active' && patient.is_active) ||
      (selectedFilter === 'inactive' && !patient.is_active);
    
    return matchesSearch && matchesFilter;
  });

  const getAge = (dateOfBirth: string) => {
    const birth = new Date(dateOfBirth);
    const today = new Date();
    let age = today.getFullYear() - birth.getFullYear();
    const monthDiff = today.getMonth() - birth.getMonth();
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
      age--;
    }
    return age;
  };

  const getHealthScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-600 bg-green-100';
    if (score >= 70) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getGenderIcon = (gender: string) => {
    return gender.toLowerCase() === 'male' ? '♂️' : '♀️';
  };

  const handleViewDetails = (patient: Patient) => {
    setSelectedPatient(patient);
    setShowPatientModal(true);
  };

  const handleViewVitals = (patientId: string) => {
    navigate(`/vitals?patient=${patientId}`);
  };

  const handleViewReports = (patientId: string) => {
    navigate(`/blood-reports?patient=${patientId}`);
  };

  if (user?.role === 'patient') {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <Shield className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900">Access Denied</h2>
          <p className="mt-2 text-gray-600">Patients cannot view other patients' information.</p>
        </div>
      </div>
    );
  }

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
          <h1 className="text-3xl font-bold text-gray-900">Patients</h1>
          <p className="mt-1 text-sm text-gray-600">Manage patient records and health information</p>
        </div>
        <div className="flex space-x-3">
          {user?.role === 'admin' && (
            <button className="btn btn-primary">
              <Plus className="h-4 w-4 mr-2" />
              Add Patient
            </button>
          )}
          <button className="btn btn-outline">
            <Download className="h-4 w-4 mr-2" />
            Export
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-6">
        <div className="card p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0 bg-blue-100 rounded-lg p-3">
              <Users className="h-6 w-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Patients</p>
              <p className="text-2xl font-bold text-gray-900">{stats.totalPatients}</p>
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0 bg-green-100 rounded-lg p-3">
              <CheckCircle className="h-6 w-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Active</p>
              <p className="text-2xl font-bold text-gray-900">{stats.activePatients}</p>
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0 bg-red-100 rounded-lg p-3">
              <AlertTriangle className="h-6 w-6 text-red-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Critical</p>
              <p className="text-2xl font-bold text-gray-900">{stats.criticalPatients}</p>
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0 bg-purple-100 rounded-lg p-3">
              <TrendingUp className="h-6 w-6 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">New This Month</p>
              <p className="text-2xl font-bold text-gray-900">{stats.newPatientsThisMonth}</p>
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0 bg-yellow-100 rounded-lg p-3">
              <Heart className="h-6 w-6 text-yellow-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Avg Health Score</p>
              <p className="text-2xl font-bold text-gray-900">{stats.averageHealthScore}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters and Search */}
      <div className="card p-4">
        <div className="flex flex-col lg:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search patients by name, email, or phone..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 w-full"
              />
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <select
              value={selectedFilter}
              onChange={(e) => setSelectedFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="all">All Patients</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
              <option value="critical">Critical</option>
            </select>
            
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="btn btn-outline"
            >
              <Filter className="h-4 w-4 mr-2" />
              Filters
            </button>
          </div>
        </div>
      </div>

      {/* Patients Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {filteredPatients.map((patient) => (
          <div key={patient.id} className="card hover:shadow-lg transition-shadow">
            <div className="p-6">
              {/* Patient Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold text-lg">
                    {patient.first_name[0]}{patient.last_name[0]}
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">
                      {patient.first_name} {patient.last_name}
                    </h3>
                    <div className="flex items-center space-x-2 text-sm text-gray-600">
                      <span>{getGenderIcon(patient.gender)}</span>
                      <span>{getAge(patient.date_of_birth)} years</span>
                      <span>•</span>
                      <span>{patient.blood_group}</span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  {patient.critical_alerts && patient.critical_alerts > 0 && (
                    <div className="bg-red-100 text-red-800 px-2 py-1 rounded-full text-xs font-medium">
                      {patient.critical_alerts} Critical
                    </div>
                  )}
                  <button className="text-gray-400 hover:text-gray-600">
                    <MoreVertical className="h-4 w-4" />
                  </button>
                </div>
              </div>

              {/* Health Score */}
              <div className="mb-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700">Health Score</span>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getHealthScoreColor(patient.health_score || 0)}`}>
                    {patient.health_score}/100
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-gradient-to-r from-green-500 to-blue-500 h-2 rounded-full"
                    style={{ width: `${patient.health_score || 0}%` }}
                  ></div>
                </div>
              </div>

              {/* Contact Info */}
              <div className="space-y-2 mb-4">
                <div className="flex items-center text-sm text-gray-600">
                  <Mail className="h-4 w-4 mr-2" />
                  {patient.email}
                </div>
                <div className="flex items-center text-sm text-gray-600">
                  <Phone className="h-4 w-4 mr-2" />
                  {patient.phone}
                </div>
                <div className="flex items-center text-sm text-gray-600">
                  <MapPin className="h-4 w-4 mr-2" />
                  {patient.country}
                </div>
              </div>

              {/* Quick Stats */}
              <div className="grid grid-cols-3 gap-2 mb-4 text-center">
                <div className="bg-gray-50 rounded p-2">
                  <p className="text-xs text-gray-600">Conditions</p>
                  <p className="text-sm font-semibold text-gray-900">{patient.conditions?.length || 0}</p>
                </div>
                <div className="bg-gray-50 rounded p-2">
                  <p className="text-xs text-gray-600">Meds</p>
                  <p className="text-sm font-semibold text-gray-900">{patient.medications?.length || 0}</p>
                </div>
                <div className="bg-gray-50 rounded p-2">
                  <p className="text-xs text-gray-600">Allergies</p>
                  <p className="text-sm font-semibold text-gray-900">{patient.allergies?.length || 0}</p>
                </div>
              </div>

              {/* Last Activity */}
              {patient.last_vital_update && (
                <div className="flex items-center text-xs text-gray-500 mb-4">
                  <Clock className="h-3 w-3 mr-1" />
                  Last vital update: {new Date(patient.last_vital_update).toLocaleDateString()}
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex space-x-2 pt-4 border-t">
                <button
                  onClick={() => handleViewDetails(patient)}
                  className="flex-1 btn btn-outline btn-sm"
                >
                  <Eye className="h-4 w-4 mr-1" />
                  View
                </button>
                <button
                  onClick={() => handleViewVitals(patient.id)}
                  className="flex-1 btn btn-outline btn-sm"
                >
                  <Activity className="h-4 w-4 mr-1" />
                  Vitals
                </button>
                <button
                  onClick={() => handleViewReports(patient.id)}
                  className="flex-1 btn btn-outline btn-sm"
                >
                  <FileText className="h-4 w-4 mr-1" />
                  Reports
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Empty State */}
      {filteredPatients.length === 0 && (
        <div className="text-center py-12">
          <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No patients found</h3>
          <p className="text-sm text-gray-600">
            {searchTerm || selectedFilter !== 'all' 
              ? 'Try adjusting your search or filters' 
              : 'No patients have been registered yet'}
          </p>
        </div>
      )}

      {/* Patient Detail Modal */}
      {showPatientModal && selectedPatient && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-6xl w-full max-h-[90vh] overflow-y-auto shadow-xl">
            {/* Header */}
            <div className="sticky top-0 bg-white border-b border-gray-200 p-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold text-3xl">
                    {selectedPatient.first_name[0]}{selectedPatient.last_name[0]}
                  </div>
                  <div>
                    <h2 className="text-3xl font-bold text-gray-900">
                      {selectedPatient.first_name} {selectedPatient.last_name}
                    </h2>
                    <div className="flex items-center space-x-3 mt-1">
                      <span className="text-sm text-gray-600">
                        {getAge(selectedPatient.date_of_birth)} years
                      </span>
                      <span className="text-sm text-gray-600">•</span>
                      <span className="text-sm text-gray-600">{selectedPatient.gender}</span>
                      <span className="text-sm text-gray-600">•</span>
                      <span className="text-sm text-gray-600">{selectedPatient.blood_group}</span>
                    </div>
                    <div className="flex items-center space-x-2 mt-2">
                      <div className={`px-3 py-1 rounded-full text-xs font-medium ${selectedPatient.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                        {selectedPatient.is_active ? 'Active' : 'Inactive'}
                      </div>
                      {selectedPatient.critical_alerts && selectedPatient.critical_alerts > 0 && (
                        <div className="px-3 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                          {selectedPatient.critical_alerts} Critical Alerts
                        </div>
                      )}
                    </div>
                  </div>
                </div>
                <button
                  onClick={() => setShowPatientModal(false)}
                  className="text-gray-400 hover:text-gray-600 p-2"
                >
                  <X className="h-6 w-6" />
                </button>
              </div>
            </div>
            
            <div className="p-6">
              {/* Quick Stats */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
                <div className="bg-gradient-to-r from-blue-50 to-blue-100 p-4 rounded-lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-blue-700">Health Score</p>
                      <p className="text-2xl font-bold text-blue-900">{selectedPatient.health_score || 0}/100</p>
                    </div>
                    <Heart className="h-8 w-8 text-blue-500" />
                  </div>
                </div>
                <div className="bg-gradient-to-r from-green-50 to-green-100 p-4 rounded-lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-green-700">Conditions</p>
                      <p className="text-2xl font-bold text-green-900">{selectedPatient.conditions?.length || 0}</p>
                    </div>
                    <Activity className="h-8 w-8 text-green-500" />
                  </div>
                </div>
                <div className="bg-gradient-to-r from-purple-50 to-purple-100 p-4 rounded-lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-purple-700">Medications</p>
                      <p className="text-2xl font-bold text-purple-900">{selectedPatient.medications?.length || 0}</p>
                    </div>
                    <Pill className="h-8 w-8 text-purple-500" />
                  </div>
                </div>
                <div className="bg-gradient-to-r from-orange-50 to-orange-100 p-4 rounded-lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-orange-700">Allergies</p>
                      <p className="text-2xl font-bold text-orange-900">{selectedPatient.allergies?.length || 0}</p>
                    </div>
                    <AlertTriangle className="h-8 w-8 text-orange-500" />
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Contact Information */}
                <div className="lg:col-span-1">
                  <div className="card p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                      <User className="h-5 w-5 mr-2 text-gray-600" />
                      Contact Information
                    </h3>
                    <div className="space-y-4">
                      <div>
                        <p className="text-sm font-medium text-gray-700 mb-1">Email</p>
                        <div className="flex items-center text-sm">
                          <Mail className="h-4 w-4 mr-2 text-gray-400" />
                          <span>{selectedPatient.email}</span>
                        </div>
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-700 mb-1">Phone</p>
                        <div className="flex items-center text-sm">
                          <Phone className="h-4 w-4 mr-2 text-gray-400" />
                          <span>{selectedPatient.phone}</span>
                        </div>
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-700 mb-1">Location</p>
                        <div className="flex items-center text-sm">
                          <MapPin className="h-4 w-4 mr-2 text-gray-400" />
                          <span>{selectedPatient.country}</span>
                        </div>
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-700 mb-1">Date of Birth</p>
                        <div className="flex items-center text-sm">
                          <Calendar className="h-4 w-4 mr-2 text-gray-400" />
                          <span>{new Date(selectedPatient.date_of_birth).toLocaleDateString()}</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Emergency Contact */}
                  <div className="card p-6 mt-4">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                      <AlertTriangle className="h-5 w-5 mr-2 text-gray-600" />
                      Emergency Contact
                    </h3>
                    <div className="space-y-4">
                      <div>
                        <p className="text-sm font-medium text-gray-700 mb-1">Name</p>
                        <div className="flex items-center text-sm">
                          <User className="h-4 w-4 mr-2 text-gray-400" />
                          <span>{selectedPatient.emergency_contact_name}</span>
                        </div>
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-700 mb-1">Phone</p>
                        <div className="flex items-center text-sm">
                          <Phone className="h-4 w-4 mr-2 text-gray-400" />
                          <span>{selectedPatient.emergency_contact_phone}</span>
                        </div>
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-700 mb-1">Relationship</p>
                        <div className="flex items-center text-sm">
                          <Heart className="h-4 w-4 mr-2 text-gray-400" />
                          <span>{selectedPatient.emergency_contact_relationship}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Medical Information */}
                <div className="lg:col-span-2">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {/* Conditions */}
                    <div className="card p-6">
                      <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                        <Activity className="h-5 w-5 mr-2 text-gray-600" />
                        Medical Conditions
                      </h3>
                      <div className="flex flex-wrap gap-2">
                        {selectedPatient.conditions?.map((condition, index) => (
                          <span key={index} className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
                            {condition}
                          </span>
                        ))}
                        {(!selectedPatient.conditions || selectedPatient.conditions.length === 0) && (
                          <span className="text-sm text-gray-500">No conditions recorded</span>
                        )}
                      </div>
                    </div>

                    {/* Medications */}
                    <div className="card p-6">
                      <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                        <Pill className="h-5 w-5 mr-2 text-gray-600" />
                        Current Medications
                      </h3>
                      <div className="flex flex-wrap gap-2">
                        {selectedPatient.medications?.map((med, index) => (
                          <span key={index} className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">
                            {med}
                          </span>
                        ))}
                        {(!selectedPatient.medications || selectedPatient.medications.length === 0) && (
                          <span className="text-sm text-gray-500">No medications recorded</span>
                        )}
                      </div>
                    </div>

                    {/* Allergies */}
                    <div className="card p-6">
                      <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                        <AlertTriangle className="h-5 w-5 mr-2 text-gray-600" />
                        Allergies
                      </h3>
                      <div className="flex flex-wrap gap-2">
                        {selectedPatient.allergies?.map((allergy, index) => (
                          <span key={index} className="px-3 py-1 bg-red-100 text-red-800 rounded-full text-sm font-medium">
                            {allergy}
                          </span>
                        ))}
                        {(!selectedPatient.allergies || selectedPatient.allergies.length === 0) && (
                          <span className="text-sm text-gray-500">No allergies recorded</span>
                        )}
                      </div>
                    </div>

                    {/* Health Metrics */}
                    <div className="card p-6">
                      <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                        <Heart className="h-5 w-5 mr-2 text-gray-600" />
                        Health Metrics
                      </h3>
                      <div className="space-y-4">
                        <div>
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-sm font-medium text-gray-700">Overall Health Score</span>
                            <span className={`px-3 py-1 rounded-full text-sm font-medium ${getHealthScoreColor(selectedPatient.health_score || 0)}`}>
                              {selectedPatient.health_score || 0}/100
                            </span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-3">
                            <div 
                              className="bg-gradient-to-r from-green-500 to-blue-500 h-3 rounded-full"
                              style={{ width: `${selectedPatient.health_score || 0}%` }}
                            ></div>
                          </div>
                        </div>
                        {selectedPatient.last_vital_update && (
                          <div className="flex items-center text-sm text-gray-600">
                            <Clock className="h-4 w-4 mr-2" />
                            Last vital update: {new Date(selectedPatient.last_vital_update).toLocaleDateString()}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex justify-between items-center pt-6 border-t mt-6">
                <div className="text-sm text-gray-500">
                  Patient ID: {selectedPatient.id}
                </div>
                <div className="flex space-x-3">
                  <button className="btn btn-outline">
                    <Edit className="h-4 w-4 mr-2" />
                    Edit Patient
                  </button>
                  <button
                    onClick={() => handleViewVitals(selectedPatient.id)}
                    className="btn btn-outline"
                  >
                    <Activity className="h-4 w-4 mr-2" />
                    View Vitals
                  </button>
                  <button
                    onClick={() => handleViewReports(selectedPatient.id)}
                    className="btn btn-primary"
                  >
                    <FileText className="h-4 w-4 mr-2" />
                    View Reports
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PatientsPage;
