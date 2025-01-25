import axios, { AxiosError } from 'axios';
import { api, AxiosResponse, AxiosRequestConfig } from './api';
import { Dispatch } from '@reduxjs/toolkit';
import { logout } from '../store/userSlice';

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface AuthToken {
  access_token: string;
  token_type: string;
}

export interface User {
  username: string;
  is_active: boolean;
  is_admin: boolean;
  roles: string[] | undefined;
  picture: string;
}

const AUTH_TOKEN_KEY = 'auth_token';

class AuthService {
  private baseUrl = '/api/v1/auth'; // Add API version prefix

  async login({ username, password }: LoginCredentials) {
    // Clear existing token from memory but don't reload
    localStorage.removeItem(AUTH_TOKEN_KEY);
    api.defaults.headers.common['Authorization'] = '';

    try {
      const formData = new URLSearchParams();
      formData.append('username', username.trim());
      formData.append('password', password.trim());
      formData.append('grant_type', 'password');

      // First get the token
      const tokenResponse = await api.post(
        `${this.baseUrl}/token`,
        formData,
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          }
        }
      );

      if (!tokenResponse.data || !tokenResponse.data.access_token) {
        throw new Error('Invalid response from server');
      }

      const token = {
        access_token: tokenResponse.data.access_token,
        token_type: tokenResponse.data.token_type || 'bearer'
      };

      // Store token and set authorization header
      localStorage.setItem(AUTH_TOKEN_KEY, JSON.stringify(token));
      api.defaults.headers.common['Authorization'] = `Bearer ${token.access_token}`;

      // Fetch user data using login-user endpoint
      const userResponse = await api.get<User>(`${this.baseUrl}/login-user`);
      if (!userResponse.data) {
        throw new Error('Failed to get user information');
      }

      return { token, user: userResponse.data };
    } catch (error) {
      // Clean up but don't reload
      localStorage.removeItem(AUTH_TOKEN_KEY);
      api.defaults.headers.common['Authorization'] = '';
      throw error instanceof Error ? error : new Error('Login failed');
    }
  }

  async getCurrentUser(): Promise<User | null> {
    const token = this.getStoredToken();

    if (!token || window.location.pathname === '/login') {
      return null;
    }

    try {
      // Get basic user info
      const userInfo = await api.get<User>(`${this.baseUrl}/login-user`);
      console.info('userInfo:', userInfo)

      return {
        ...userInfo.data
      };
    } catch (error) {
      console.error('Error fetching user info:', error);
      return null;
    }
  }

  getStoredToken(): AuthToken | null {
    const tokenStr = localStorage.getItem(AUTH_TOKEN_KEY);
    if (!tokenStr) return null;

    try {
      return JSON.parse(tokenStr);
    } catch {
      return null;
    }
  }

  logout(): void {
    localStorage.removeItem(AUTH_TOKEN_KEY);
    api.defaults.headers.common['Authorization'] = '';

    // Only redirect if not already on login page
    if (window.location.pathname !== '/login') {
      window.location.replace('/login');
    }
  }

  isAuthenticated(): boolean {
    return !!this.getStoredToken();
  }

  // Setup axios interceptor to add auth header to all requests
  setupAxiosInterceptors(dispatch: Dispatch): void {
    // Request interceptor
    api.interceptors.request.use((config: AxiosRequestConfig) => {
      const token = this.getStoredToken();
      if (token && config.headers) {
        config.headers['Authorization'] = `Bearer ${token.access_token}`;
      }
      return config as AxiosRequestConfig;
    });

    // Response interceptor with token refresh
    api.interceptors.response.use(
      (response: AxiosResponse) => response,
      async (error: AxiosError) => {
        if (!error.config) return Promise.reject(error);

        const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean };

        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            const newToken = await this.refreshToken();
            if (originalRequest.headers) {
              originalRequest.headers['Authorization'] = `Bearer ${newToken.access_token}`;
            }
            return api.request(originalRequest);
          } catch (refreshError) {
            dispatch(logout());
            this.logout();
            return Promise.reject(refreshError);
          }
        }

        return Promise.reject(error);
      }
    );
  }

  async updateAvatar(formData: FormData): Promise<{ avatarUrl: string }> {
    const token = this.getStoredToken();
    if (!token) throw new Error('Not authenticated');

    const response = await api.post<{ avatarUrl: string }>(
      `${this.baseUrl} / avatar`,
      formData,
      {
        headers: {
          'Authorization': `Bearer ${token.access_token}`,
          'Content-Type': 'multipart/form-data',
        },
      }
    );

    return response.data;
  }

  async updatePassword(currentPassword: string, newPassword: string): Promise<void> {
    const token = this.getStoredToken();
    if (!token) throw new Error('Not authenticated');

    await api.post(
      `${this.baseUrl} / update - password`,
      { current_password: currentPassword, new_password: newPassword },
      {
        headers: {
          Authorization: `Bearer ${token.access_token}`,
        },
      }
    );
  }

  async refreshToken(): Promise<AuthToken> {
    const token = this.getStoredToken();
    if (!token) throw new Error('No token to refresh');

    const response = await api.post<AuthToken>(
      `${this.baseUrl} / refresh - token`,
      {},
      {
        headers: {
          Authorization: `Bearer ${token.access_token}`,
        },
      }
    );

    localStorage.setItem(AUTH_TOKEN_KEY, JSON.stringify(response.data));
    return response.data;
  }
}

export const authService = new AuthService();