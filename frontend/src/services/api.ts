import axios, { AxiosInstance, InternalAxiosRequestConfig, AxiosResponse } from 'axios';

// Use import.meta.env for Vite environment variables
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
console.log('API URL:', API_URL);

export const api: AxiosInstance = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  withCredentials: true,
});

// For form data requests, create a separate interceptor
api.interceptors.request.use((config) => {
  // Log all requests in development
  if (import.meta.env.DEV) {
    console.log('Request URL:', {
      baseURL: API_URL,
      path: config.url,
      fullUrl: `${API_URL}${config.url}`,
      method: config.method?.toUpperCase()
    });
  }

  // Log auth-related requests
  if (config.url?.includes('auth')) {
    console.log('Full request URL:', `${API_URL}${config.url}`);
    let logData: Record<string, string | number | boolean>;

    if (config.data instanceof FormData) {
      logData = {};
      config.data.forEach((value, key) => {
        if (typeof value === 'string') {
          logData[key] = value;
        } else {
          logData[key] = String(value);
        }
      });
      config.headers['Content-Type'] = 'multipart/form-data';
    } else {
      logData = config.data as Record<string, string | number | boolean>;
    }

    console.log('Auth Request:', {
      url: config.url,
      method: config.method,
      data: logData,
      contentType: config.headers['Content-Type']
    });
  }
  return config;
});

// Add response interceptor for debugging
api.interceptors.response.use(
  response => {
    console.log(`${response.config.method?.toUpperCase()} ${response.config.url}:`, response);
    return response;
  },
  error => {
    if (error.response) {
      console.error('API Error Details:', {
        endpoint: error.config.url,
        method: error.config.method,
        status: error.response.status,
        data: error.response.data,
        headers: error.config.headers
      });
    }
    return Promise.reject(error);
  }
);

export type ApiResponse<T = any> = AxiosResponse<T>;

export interface ApiError {
  message: string;
  status?: number;
  details?: any;
}

export type {
  AxiosResponse,
  InternalAxiosRequestConfig as AxiosRequestConfig
};
