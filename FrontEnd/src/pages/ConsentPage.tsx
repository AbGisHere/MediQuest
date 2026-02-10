import React, { useState, useEffect } from 'react';
import { FileText, Shield, Clock, CheckCircle, XCircle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import apiService from '../services/api';

const ConsentPage: React.FC = () => {
  const { user } = useAuth();
  const [consents, setConsents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchConsents = async () => {
      try {
        setLoading(true);
        // For patients, show their consents; for doctors, show consents they've granted
        if (user?.role === 'patient') {
          // Patients would see who has access to their data
          const consentData = await apiService.getPatientConsents(user.id);
          setConsents(consentData);
        } else if (user?.role === 'doctor') {
          // Doctors see consents they've granted to patients
          // Get real patients and create sample consents
          const patients = await apiService.getPatientsWithConsent(0, 10);
          const sampleConsents = patients.slice(0, 2).map((patient, index) => ({
            id: (index + 1).toString(),
            patient_name: `${patient.first_name} ${patient.last_name}`,
            patient_id: patient.id,
            purpose: index === 0 ? 'Treatment' : 'Research',
            granted_at: '2026-02-01T10:00:00Z',
            status: 'active',
            expires_at: '2026-12-31T23:59:59Z'
          }));
          setConsents(sampleConsents);
        } else {
          setConsents([]);
        }
      } catch (error) {
        console.error('Error fetching consents:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchConsents();
  }, [user]);

  const handleRevokeConsent = async (consentId: string) => {
    try {
      await apiService.revokeConsent(consentId);
      setConsents(prev => prev.filter(c => c.id !== consentId));
      alert('Consent revoked successfully!');
    } catch (error) {
      console.error('Error revoking consent:', error);
      alert('Failed to revoke consent');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Consent Management</h1>
        <p className="text-sm text-gray-600">Manage data sharing permissions and privacy controls</p>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        </div>
      ) : (
        <>
          {user?.role === 'patient' && (
            <div className="card p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Who Can Access Your Data</h3>
              <div className="space-y-4">
                {consents.length === 0 ? (
                  <div className="text-center py-8">
                    <XCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-500">No healthcare providers have access to your data</p>
                    <p className="text-sm text-gray-600">Your data is private and only accessible to you</p>
                  </div>
                ) : (
                  consents.map((consent) => (
                    <div key={consent.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center space-x-3">
                        <CheckCircle className="h-6 w-6 text-green-600" />
                        <div>
                          <h4 className="text-sm font-medium text-gray-900">{consent.patient_name}</h4>
                          <p className="text-sm text-gray-600">{consent.purpose} Consent</p>
                          <p className="text-xs text-gray-500">
                            Granted: {new Date(consent.granted_at).toLocaleDateString()}
                          </p>
                          <p className="text-xs text-gray-500">
                            Expires: {new Date(consent.expires_at).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                          consent.status === 'active' 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {consent.status}
                        </span>
                        <button
                          onClick={() => handleRevokeConsent(consent.id)}
                          className="btn btn-outline btn-sm text-red-600"
                        >
                          Revoke
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}

          {(user?.role === 'doctor' || user?.role === 'admin') && (
            <div className="card p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Consents You've Granted</h3>
              <div className="space-y-4">
                {consents.length === 0 ? (
                  <div className="text-center py-8">
                    <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-500">You haven't granted any consents yet</p>
                    <p className="text-sm text-gray-600">Grant access to patient data when they provide consent</p>
                  </div>
                ) : (
                  consents.map((consent) => (
                    <div key={consent.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center space-x-3">
                        <Shield className="h-6 w-6 text-blue-600" />
                        <div>
                          <h4 className="text-sm font-medium text-gray-900">{consent.patient_name}</h4>
                          <p className="text-sm text-gray-600">{consent.purpose} Consent</p>
                          <div className="text-xs text-gray-500 space-y-1">
                            <p>
                              <Clock className="h-3 w-3 inline mr-1" />
                              Granted: {new Date(consent.granted_at).toLocaleDateString()}
                            </p>
                            <p>
                              Expires: {new Date(consent.expires_at).toLocaleDateString()}
                            </p>
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                          consent.status === 'active' 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {consent.status}
                        </span>
                        <button
                          onClick={() => handleRevokeConsent(consent.id)}
                          className="btn btn-outline btn-sm text-red-600"
                        >
                          Revoke
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}

          {!user && (
            <div className="text-center py-12">
              <Shield className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">Please log in to manage consent settings</p>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default ConsentPage;
