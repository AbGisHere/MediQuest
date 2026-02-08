// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const API_ENDPOINTS = {
  // Authentication
  AUTH: {
    LOGIN: `${API_BASE_URL}/auth/login`,
    REGISTER: `${API_BASE_URL}/auth/register`,
    REFRESH: `${API_BASE_URL}/auth/refresh`,
    LOGOUT: `${API_BASE_URL}/auth/logout`,
  },
  
  // Patients
  PATIENTS: {
    REGISTER: `${API_BASE_URL}/patients/register`,
    LIST: `${API_BASE_URL}/patients/`,
    DETAIL: (id: string) => `${API_BASE_URL}/patients/${id}`,
    VERIFY_BIOMETRIC: `${API_BASE_URL}/patients/verify-biometric`,
    DELETE: (id: string) => `${API_BASE_URL}/patients/${id}`,
  },
  
  // Vitals
  VITALS: {
    UPLOAD: `${API_BASE_URL}/vitals/`,
    BATCH_UPLOAD: `${API_BASE_URL}/vitals/batch`,
    PATIENT_VITALS: (patientId: string) => `${API_BASE_URL}/vitals/${patientId}`,
  },
  
  // Consent
  CONSENT: {
    GRANT: `${API_BASE_URL}/consent/grant`,
    REVOKE: `${API_BASE_URL}/consent/revoke`,
    PATIENT_CONSENTS: (patientId: string) => `${API_BASE_URL}/consent/${patientId}`,
    CHECK: (patientId: string, purpose: string) => `${API_BASE_URL}/consent/${patientId}/check/${purpose}`,
  },
  
  // Emergency
  EMERGENCY: {
    OVERRIDE: `${API_BASE_URL}/emergency/override`,
    ACTIVE: `${API_BASE_URL}/emergency/active`,
  },
  
  // Health Profile
  HEALTH_PROFILE: {
    CREATE: `${API_BASE_URL}/health-profile/`,
    DETAIL: (patientId: string) => `${API_BASE_URL}/health-profile/${patientId}`,
    UPDATE: (patientId: string) => `${API_BASE_URL}/health-profile/${patientId}`,
  },
  
  // System
  HEALTH: `${API_BASE_URL}/health`,
} as const;

export default API_BASE_URL;
