import React, { createContext, useContext, useReducer, useEffect } from 'react';
import type { ReactNode } from 'react';
import type { User, AuthContextType, LoginCredentials, RegisterData } from '../types';
import apiService from '../services/api';

interface AuthState {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;
}

type AuthAction =
  | { type: 'AUTH_START' }
  | { type: 'AUTH_SUCCESS'; payload: { user: User; token: string } }
  | { type: 'AUTH_FAILURE' }
  | { type: 'LOGOUT' }
  | { type: 'SET_USER'; payload: User }
  | { type: 'CLEAR_LOADING' };

const initialState: AuthState = {
  user: null,
  token: localStorage.getItem('access_token'),
  isLoading: false,
  isAuthenticated: false,
};

const authReducer = (state: AuthState, action: AuthAction): AuthState => {
  switch (action.type) {
    case 'AUTH_START':
      return {
        ...state,
        isLoading: true,
      };
    case 'AUTH_SUCCESS':
      return {
        ...state,
        user: action.payload.user,
        token: action.payload.token,
        isLoading: false,
        isAuthenticated: true,
      };
    case 'AUTH_FAILURE':
      return {
        ...state,
        user: null,
        token: null,
        isLoading: false,
        isAuthenticated: false,
      };
    case 'LOGOUT':
      return {
        ...state,
        user: null,
        token: null,
        isLoading: false,
        isAuthenticated: false,
      };
    case 'SET_USER':
      return {
        ...state,
        user: action.payload,
        isAuthenticated: true,
      };
    case 'CLEAR_LOADING':
      return {
        ...state,
        isLoading: false,
      };
    default:
      return state;
  }
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('access_token');
      if (token) {
        try {
          // Validate token by making a health check or user info request
          const response = await apiService.healthCheck();
          if (response.status === 'healthy') {
            // Token is valid, but we need user info
            // For now, we'll set a minimal user state
            // In a real app, you'd have an endpoint to get current user info
            dispatch({
              type: 'AUTH_SUCCESS',
              payload: {
                user: {
                  id: 'temp',
                  username: 'user',
                  email: 'user@example.com',
                  role: 'patient',
                  is_active: true,
                  created_at: new Date().toISOString(),
                },
                token,
              },
            });
          } else {
            dispatch({ type: 'AUTH_FAILURE' });
          }
        } catch {
          dispatch({ type: 'AUTH_FAILURE' });
        }
      } else {
        dispatch({ type: 'CLEAR_LOADING' });
      }
    };

    initAuth();
  }, []);

  const login = async (credentials: LoginCredentials): Promise<void> => {
    dispatch({ type: 'AUTH_START' });
    try {
      const response = await apiService.login(credentials);

      // Create user object from response
      const user: User = {
        id: response.user_id,
        username: credentials.username,
        email: '', // Will be populated from backend in real implementation
        role: response.role as 'admin' | 'doctor' | 'patient',
        is_active: true,
        created_at: new Date().toISOString(),
      };

      dispatch({
        type: 'AUTH_SUCCESS',
        payload: { user, token: response.access_token },
      });
    } catch (error) {
      dispatch({ type: 'AUTH_FAILURE' });
      throw error;
    }
  };

  const register = async (data: RegisterData): Promise<void> => {
    dispatch({ type: 'AUTH_START' });
    try {
      const response = await apiService.register(data);

      // Create user object from response
      const user: User = {
        id: response.user_id,
        username: data.username,
        email: data.email,
        role: data.role,
        is_active: true,
        created_at: new Date().toISOString(),
      };

      dispatch({
        type: 'AUTH_SUCCESS',
        payload: { user, token: response.access_token },
      });
    } catch (error) {
      dispatch({ type: 'AUTH_FAILURE' });
      throw error;
    }
  };

  const logout = async (): Promise<void> => {
    try {
      await apiService.logout();
    } catch (error) {
      // Continue with logout even if API call fails
      console.error('Logout error:', error);
    } finally {
      dispatch({ type: 'LOGOUT' });
    }
  };

  const refreshToken = async (): Promise<void> => {
    try {
      // The API service handles token refresh automatically
      // This is just for the context to know about it
      const token = localStorage.getItem('access_token');
      if (token) {
        dispatch({
          type: 'AUTH_SUCCESS',
          payload: {
            user: state.user!,
            token,
          },
        });
      }
    } catch (error) {
      dispatch({ type: 'AUTH_FAILURE' });
      throw error;
    }
  };

  const value: AuthContextType = {
    user: state.user,
    token: state.token,
    login,
    register,
    logout,
    refreshToken,
    isLoading: state.isLoading,
    isAuthenticated: state.isAuthenticated,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// eslint-disable-next-line react-refresh/only-export-components
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
