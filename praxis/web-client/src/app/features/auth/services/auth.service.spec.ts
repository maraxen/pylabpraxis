import { TestBed } from '@angular/core/testing';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { provideHttpClient } from '@angular/common/http';
import { AuthService } from './auth.service';
import { LoginRequest, LoginResponse, User } from '../models/auth.models';
import { describe, it, expect, beforeEach, afterEach } from 'vitest';

describe('AuthService', () => {
  let service: AuthService;
  let httpMock: HttpTestingController;
  const API_URL = '/api/v1/auth';

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        AuthService,
        provideHttpClient(),
        provideHttpClientTesting()
      ]
    });

    service = TestBed.inject(AuthService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  describe('login', () => {
    it('should send login request and return response', () => {
      const mockCredentials: LoginRequest = { username: 'testuser', password: 'password123' };
      const mockResponse: LoginResponse = { 
        access_token: 'fake-jwt-token',
        token_type: 'bearer',
        user: { username: 'testuser', email: 'test@example.com', full_name: 'Test User', is_active: true } 
      };

      service.login(mockCredentials).subscribe(response => {
        expect(response).toEqual(mockResponse);
      });

      const req = httpMock.expectOne(`${API_URL}/login`);
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual(mockCredentials);
      req.flush(mockResponse);
    });

    it('should handle login errors', () => {
      const mockCredentials: LoginRequest = { username: 'testuser', password: 'wrongpassword' };

      service.login(mockCredentials).subscribe({
        next: () => expect(true).toBe(false), // Should not reach here
        error: (error) => {
          expect(error.status).toBe(401);
        }
      });

      const req = httpMock.expectOne(`${API_URL}/login`);
      req.flush('Unauthorized', { status: 401, statusText: 'Unauthorized' });
    });
  });

  describe('logout', () => {
    it('should send logout request', () => {
      service.logout().subscribe(response => {
        expect((response as any).message).toBe('Logged out successfully');
      });

      const req = httpMock.expectOne(`${API_URL}/logout`);
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual({});
      req.flush({ message: 'Logged out successfully' });
    });
  });

  describe('getCurrentUser', () => {
    it('should fetch current user', () => {
      const mockUser: User = { username: 'testuser', email: 'test@example.com', full_name: 'Test User', is_active: true };

      service.getCurrentUser().subscribe(user => {
        expect(user).toEqual(mockUser);
      });

      const req = httpMock.expectOne(`${API_URL}/me`);
      expect(req.request.method).toBe('GET');
      req.flush(mockUser);
    });
  });
});