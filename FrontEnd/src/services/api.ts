import axios from 'axios';
import type { AxiosInstance, AxiosResponse } from 'axios';
import { API_ENDPOINTS } from '../config/api';
import type { AuthResponse, LoginCredentials, RegisterData, ApiResponse } from '../types';

class ApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor for error handling
    this.api.interceptors.response.use(
      (response: AxiosResponse) => response,
      async (error) => {
        const originalRequest = error.config;

        // Handle 401 Unauthorized - token refresh
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            await this.refreshToken();
            const token = localStorage.getItem('access_token');
            if (token) {
              originalRequest.headers.Authorization = `Bearer ${token}`;
              return this.api(originalRequest);
            }
          } catch (refreshError) {
            // Refresh failed, logout user
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            window.location.href = '/login';
            return Promise.reject(refreshError);
          }
        }

        return Promise.reject(error);
      }
    );
  }

  private async refreshToken(): Promise<void> {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    const response = await axios.post(
      API_ENDPOINTS.AUTH.REFRESH,
      { refresh_token: refreshToken }
    );

    const { access_token, refresh_token: newRefreshToken } = response.data;
    localStorage.setItem('access_token', access_token);
    if (newRefreshToken) {
      localStorage.setItem('refresh_token', newRefreshToken);
    }
  }

  // Authentication methods
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const response = await this.api.post<AuthResponse>(
      API_ENDPOINTS.AUTH.LOGIN,
      credentials
    );
    
    // Store tokens
    localStorage.setItem('access_token', response.data.access_token);
    localStorage.setItem('refresh_token', response.data.refresh_token);
    
    return response.data;
  }

  async register(data: RegisterData): Promise<AuthResponse> {
    const response = await this.api.post<AuthResponse>(
      API_ENDPOINTS.AUTH.REGISTER,
      data
    );
    
    // Store tokens
    localStorage.setItem('access_token', response.data.access_token);
    localStorage.setItem('refresh_token', response.data.refresh_token);
    
    return response.data;
  }

  async logout(): Promise<void> {
    try {
      await this.api.post(API_ENDPOINTS.AUTH.LOGOUT);
    } finally {
      // Always clear tokens locally
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }
  }

  // Patient methods
  async getPatients(page = 0, limit = 100) {
    const response = await this.api.get(API_ENDPOINTS.PATIENTS.LIST, {
      params: { skip: page * limit, limit }
    });
    return response.data;
  }

  async getPatientsWithConsent(page = 0, limit = 100) {
    const response = await this.api.get(API_ENDPOINTS.PATIENTS.LIST, {
      params: { skip: page * limit, limit, with_consent: true }
    });
    return response.data;
  }

  async getPatient(patientId: string) {
    const response = await this.api.get(API_ENDPOINTS.PATIENTS.DETAIL(patientId));
    return response.data;
  }

  async getPatientById(patientId: string) {
    const response = await this.api.get(API_ENDPOINTS.PATIENTS.DETAIL(patientId));
    return response.data;
  }

  async getPatientAlerts(patientId: string) {
    const response = await this.api.get(API_ENDPOINTS.HEALTH_PROFILE.DETAIL(patientId));
    return response.data.recent_alerts || [];
  }

  async registerPatient(data: any) {
    const response = await this.api.post(
      API_ENDPOINTS.PATIENTS.REGISTER,
      data
    );
    return response.data;
  }

  async verifyBiometric(data: { fingerprint_data: string }) {
    const response = await this.api.post(
      API_ENDPOINTS.PATIENTS.VERIFY_BIOMETRIC,
      data
    );
    return response.data;
  }

  // Vitals methods
  async uploadVital(data: any) {
    const response = await this.api.post(
      API_ENDPOINTS.VITALS.UPLOAD,
      data
    );
    return response.data;
  }

  async batchUploadVitals(data: any) {
    const response = await this.api.post(
      API_ENDPOINTS.VITALS.BATCH_UPLOAD,
      data
    );
    return response.data;
  }

  async getPatientVitals(patientId: string, vitalType?: string, limit = 100) {
    const response = await this.api.get(
      API_ENDPOINTS.VITALS.PATIENT_VITALS(patientId),
      {
        params: { vital_type: vitalType, limit }
      }
    );
    return response.data;
  }

  // Consent methods
  async grantConsent(data: any) {
    const response = await this.api.post(
      API_ENDPOINTS.CONSENT.GRANT,
      data
    );
    return response.data;
  }

  async revokeConsent(data: any) {
    const response = await this.api.post(
      API_ENDPOINTS.CONSENT.REVOKE,
      data
    );
    return response.data;
  }

  async getPatientConsents(patientId: string) {
    const response = await this.api.get(
      API_ENDPOINTS.CONSENT.PATIENT_CONSENTS(patientId)
    );
    return response.data;
  }

  async checkConsent(patientId: string, purpose: string, doctorId?: string) {
    const response = await this.api.get(
      API_ENDPOINTS.CONSENT.CHECK(patientId, purpose),
      {
        params: { doctor_id: doctorId }
      }
    );
    return response.data;
  }

  // Emergency methods
  async emergencyOverride(data: any) {
    const response = await this.api.post(
      API_ENDPOINTS.EMERGENCY.OVERRIDE,
      data
    );
    return response.data;
  }

  async getActiveEmergencyOverrides() {
    const response = await this.api.get(API_ENDPOINTS.EMERGENCY.ACTIVE);
    return response.data;
  }

  // Health Profile methods
  async createHealthProfile(data: any) {
    const response = await this.api.post(
      API_ENDPOINTS.HEALTH_PROFILE.CREATE,
      data
    );
    return response.data;
  }

  async getHealthProfile(patientId: string) {
    const response = await this.api.get(
      API_ENDPOINTS.HEALTH_PROFILE.DETAIL(patientId)
    );
    return response.data;
  }

  async updateHealthProfile(patientId: string, data: any) {
    const response = await this.api.put(
      API_ENDPOINTS.HEALTH_PROFILE.UPDATE(patientId),
      data
    );
    return response.data;
  }

  // Blood Reports methods
  async getPatientBloodReports(patientId: string) {
    const response = await this.api.get(API_ENDPOINTS.BLOOD_REPORTS.LIST(patientId));
    return response.data;
  }

  async getBloodReport(reportId: string) {
    const response = await this.api.get(API_ENDPOINTS.BLOOD_REPORTS.DETAIL(reportId));
    return response.data;
  }

  async uploadBloodReport(patientId: string, file: File, testDate?: string, labName?: string) {
    const formData = new FormData();
    formData.append('patient_id', patientId);
    formData.append('file', file);
    if (testDate) formData.append('test_date', testDate);
    if (labName) formData.append('lab_name', labName);

    const response = await this.api.post(API_ENDPOINTS.BLOOD_REPORTS.UPLOAD, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  async downloadBloodReport(reportId: string) {
    const response = await this.api.get(API_ENDPOINTS.BLOOD_REPORTS.DOWNLOAD(reportId), {
      responseType: 'blob',
    });
    return response.data;
  }

  async deleteBloodReport(reportId: string) {
    const response = await this.api.delete(API_ENDPOINTS.BLOOD_REPORTS.DELETE(reportId));
    return response.data;
  }

  // System health check
  async healthCheck() {
    const response = await this.api.get(API_ENDPOINTS.HEALTH);
    return response.data;
  }

  // Get current user info
  async getCurrentUser() {
    const response = await this.api.get('/auth/me');
    return response.data;
  }

  // Generic request method
  async request<T = any>(config: any): Promise<ApiResponse<T>> {
    try {
      const response = await this.api.request<T>(config);
      return {
        data: response.data,
        status: response.status,
      };
    } catch (error: any) {
      return {
        error: error.response?.data?.detail || error.message,
        status: error.response?.status || 500,
      };
    }
  }
}

// Create singleton instance
const apiService = new ApiService();
export default apiService;
