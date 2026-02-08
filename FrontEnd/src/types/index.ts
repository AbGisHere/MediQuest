// Type definitions for the MediQuest application

export interface User {
  id: string;
  username: string;
  email: string;
  role: 'admin' | 'doctor' | 'patient';
  is_active: boolean;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user_id: string;
  role: string;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
  role: 'admin' | 'doctor' | 'patient';
}

export interface Patient {
  id: string;
  first_name: string;
  last_name: string;
  date_of_birth: string;
  gender?: string;
  blood_group?: string;
  email?: string;
  phone?: string;
  address?: string;
  city?: string;
  state?: string;
  country: string;
  postal_code?: string;
  emergency_contact_name?: string;
  emergency_contact_phone?: string;
  emergency_contact_relationship?: string;
  is_active: boolean;
  created_at: string;
}

export interface PatientRegisterData {
  first_name: string;
  last_name: string;
  date_of_birth: string;
  gender?: string;
  blood_group?: string;
  email?: string;
  phone?: string;
  address?: string;
  city?: string;
  state?: string;
  country: string;
  postal_code?: string;
  emergency_contact_name?: string;
  emergency_contact_phone?: string;
  emergency_contact_relationship?: string;
  fingerprint_data: string;
}

export interface BiometricVerifyData {
  fingerprint_data: string;
}

export interface BiometricVerifyResponse {
  verified: boolean;
  patient_id: string;
  patient_name: string;
}

export interface Vital {
  id: string;
  patient_id: string;
  vital_type: string;
  value: number;
  unit: string;
  source: string;
  source_id?: string;
  recorded_at: string;
  notes?: string;
  checksum?: string;
  batch_id?: string;
  uploaded_by: string;
  created_at: string;
}

export interface VitalCreateData {
  patient_id: string;
  vital_type: string;
  value: number;
  unit: string;
  source: string;
  source_id?: string;
  recorded_at: string;
  notes?: string;
  checksum?: string;
}

export interface VitalBatchData {
  batch_id?: string;
  vitals: VitalCreateData[];
}

export interface Consent {
  id: string;
  patient_id: string;
  purpose: string;
  granted_by_id: string;
  granted_to_id?: string;
  consent_text?: string;
  is_active: boolean;
  created_at: string;
  expires_at?: string;
  revoked_at?: string;
  revoked_by_id?: string;
}

export interface ConsentGrantData {
  patient_id: string;
  purpose: string;
  granted_to_id?: string;
  consent_text?: string;
  expiry_date?: string;
}

export interface ConsentRevokeData {
  patient_id: string;
  purpose: string;
  granted_to_id?: string;
}

export interface EmergencyOverrideData {
  patient_id: string;
  reason: string;
  duration_hours?: number;
}

export interface Alert {
  id: string;
  patient_id: string;
  vital_id?: string;
  alert_type: string;
  severity: string;
  message: string;
  is_active: boolean;
  created_at: string;
  resolved_at?: string;
  resolved_by?: string;
}

export interface HealthProfile {
  id: string;
  patient_id: string;
  allergies?: string[];
  medications?: string[];
  medical_conditions?: string[];
  family_history?: string[];
  surgical_history?: string[];
  created_at: string;
  updated_at: string;
}

export interface ApiResponse<T = any> {
  data?: T;
  error?: string;
  message?: string;
  status: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  has_next: boolean;
  has_prev: boolean;
}

// Context types
export interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
  refreshToken: () => Promise<void>;
  isLoading: boolean;
  isAuthenticated: boolean;
}

export interface NotificationType {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  timestamp: Date;
  autoClose?: boolean;
}

// Form types
export interface VitalFormData {
  patient_id: string;
  vital_type: string;
  value: string;
  unit: string;
  source: string;
  recorded_at: string;
  notes?: string;
}

export interface PatientFormData {
  first_name: string;
  last_name: string;
  date_of_birth: string;
  gender?: string;
  blood_group?: string;
  email?: string;
  phone?: string;
  address?: string;
  city?: string;
  state?: string;
  country: string;
  postal_code?: string;
  emergency_contact_name?: string;
  emergency_contact_phone?: string;
  emergency_contact_relationship?: string;
}

// Chart data types
export interface ChartDataPoint {
  timestamp: string;
  value: number;
  label?: string;
}

export interface VitalsChartData {
  [vitalType: string]: ChartDataPoint[];
}
