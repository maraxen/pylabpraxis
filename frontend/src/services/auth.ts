import axios from 'axios';

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
  setupAxiosInterceptors(): void {
    axios.interceptors.request.use((config) => {
      const token = this.getStoredToken();
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token.access_token}`;
      }
      return config;
    });

    // Handle 401 responses
    axios.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          this.logout();
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }
}

export const authService = new AuthService();