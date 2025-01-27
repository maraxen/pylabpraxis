import React from 'react';
import axios from 'axios';
import { Button } from '../ui/button';

const CreateAccountButton: React.FC = () => {
  const handleCreateAccount = async () => {
    try {
      const response = await axios.get('/api/v1/auth/register-uri');
      window.location.href = response.data.uri; // Redirect to Keycloak
    } catch (error) {
      console.error('Error creating account:', error);
      // Handle error, display message to the user
    }
  };

  return (
    <Button onClick={handleCreateAccount}>Create Account</Button>
  );
};

export default CreateAccountButton;
