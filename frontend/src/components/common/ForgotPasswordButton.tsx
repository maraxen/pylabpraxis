import React from 'react';
import axios from 'axios';
import { Button } from '../ui/button';

const ForgotPasswordButton: React.FC = () => {
  const handleForgotPassword = async () => {
    try {
      const response = await axios.get('/api/v1/auth/forgot-password-uri');
      window.location.href = response.data.uri; // Redirect to Keycloak
    } catch (error) {
      console.error('Error sending forgot password request:', error);
      // Handle error, display message to the user
    }
  };

  return (
    <Button onClick={handleForgotPassword}>Forgot Password</Button>
  );
};

export default ForgotPasswordButton;