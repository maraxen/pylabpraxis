import React from 'react';
import '@testing-library/jest-dom';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { Login } from '../Login';
import { authService } from '../../services/auth';
import { useNavigate } from 'react-router-dom';
import { useToast } from '@chakra-ui/toast';

// Mock the required dependencies
jest.mock('react-router-dom', () => ({
  useNavigate: jest.fn(),
}));

jest.mock('@chakra-ui/react', () => ({
  ...jest.requireActual('@chakra-ui/react'),
  useToast: jest.fn(),
}));

jest.mock('../../services/auth', () => ({
  authService: {
    login: jest.fn(),
    getCurrentUser: jest.fn(),
  },
}));

describe('Login Component', () => {
  const mockNavigate = jest.fn();
  const mockToast = jest.fn();

  beforeEach(() => {
    (useNavigate as jest.Mock).mockReturnValue(mockNavigate);
    (useToast as jest.Mock).mockReturnValue(mockToast);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('renders login form', () => {
    render(<Login />);
    expect(screen.getByText('Login to Praxis')).toBeInTheDocument();
    expect(screen.getByLabelText(/username/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
  });

  it('handles successful login', async () => {
    const mockUser = { username: 'testuser' };
    (authService.login as jest.Mock).mockResolvedValueOnce({});
    (authService.getCurrentUser as jest.Mock).mockResolvedValueOnce(mockUser);

    render(<Login />);

    fireEvent.change(screen.getByLabelText(/username/i), {
      target: { value: 'testuser' },
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'password123' },
    });
    fireEvent.click(screen.getByText('Sign In'));

    await waitFor(() => {
      expect(authService.login).toHaveBeenCalledWith({
        username: 'testuser',
        password: 'password123',
      });
      expect(mockNavigate).toHaveBeenCalledWith('/');
      expect(mockToast).toHaveBeenCalledWith(expect.objectContaining({
        status: 'success',
        title: 'Login successful',
      }));
    });
  });

  it('handles login failure', async () => {
    (authService.login as jest.Mock).mockRejectedValueOnce(new Error('Login failed'));

    render(<Login />);

    fireEvent.change(screen.getByLabelText(/username/i), {
      target: { value: 'testuser' },
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'wrongpassword' },
    });
    fireEvent.click(screen.getByText('Sign In'));

    await waitFor(() => {
      expect(mockToast).toHaveBeenCalledWith(expect.objectContaining({
        status: 'error',
        title: 'Login failed',
      }));
    });
  });
});
