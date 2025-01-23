import axios from 'axios';
import { Dispatch } from '@reduxjs/toolkit';
import { sessionExpired } from '../store/userSlice';

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
  avatarUrl?: string;
}

const AUTH_TOKEN_KEY = 'auth_token';

class AuthService {
  private baseUrl = '/api/auth';

  async login(credentials: LoginCredentials): Promise<AuthToken> {
    const formData = new FormData();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);

    const response = await axios.post<AuthToken>(`${this.baseUrl}/token`, formData);
    const token = response.data;

    // Store the token
    localStorage.setItem(AUTH_TOKEN_KEY, JSON.stringify(token));

    return token;
  }

  async getCurrentUser(): Promise<User | null> {
    try {
      const token = this.getStoredToken();
      if (!token) return null;

      const response = await axios.get<User>(`${this.baseUrl}/users/me`, {
        headers: {
          Authorization: `Bearer ${token.access_token}`,
        },
      });

      return response.data;
    } catch (error) {
      this.logout();
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
  }

  isAuthenticated(): boolean {
    return !!this.getStoredToken();
  }

  // Setup axios interceptor to add auth header to all requests
  setupAxiosInterceptors(dispatch: Dispatch): void {
    // Request interceptor
    axios.interceptors.request.use((config) => {
      const token = this.getStoredToken();
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token.access_token}`;
      }
      return config;
    });

    // Response interceptor with token refresh
    axios.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            const newToken = await this.refreshToken();
            originalRequest.headers.Authorization = `Bearer ${newToken.access_token}`;
            return axios(originalRequest);
          } catch (refreshError) {
            this.logout();
            window.location.href = '/login';
            return Promise.reject(refreshError);
          }
        }

        if (error.response?.status === 401) {
          // Try to refresh the token first
          try {
            await this.refreshToken();
            return axios(error.config);
          } catch (refreshError) {
            // If refresh fails, mark the session as expired
            dispatch(sessionExpired());
            this.logout();
            window.location.href = '/login';
          }
        }
        return Promise.reject(error);
      }
    );
  }

  async updateAvatar(formData: FormData): Promise<{ avatarUrl: string }> {
    const token = this.getStoredToken();
    if (!token) throw new Error('Not authenticated');

    const response = await axios.post<{ avatarUrl: string }>(
      `${this.baseUrl}/avatar`,
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

    await axios.post(
      `${this.baseUrl}/update-password`,
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

    const response = await axios.post<AuthToken>(
      `${this.baseUrl}/refresh-token`,
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