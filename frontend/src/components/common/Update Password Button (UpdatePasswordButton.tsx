import React from 'react';
import axios from 'axios';
import { Button } from '../ui/button';

interface UpdatePasswordButtonProps {
  token: string;
}

const UpdatePasswordButton: React.FC<UpdatePasswordButtonProps> = ({ token }) => {
  const handleUpdatePassword = async () => {
    try {
      const response = await axios.get('/api/v1/auth/update-password-uri', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      window.location.href = response.data.uri; // Redirect to Keycloak
    } catch (error) {
      console.error('Error sending update password request:', error);
      // Handle error, display message to the user
    }
  };

  return (
    <Button onClick={handleUpdatePassword}>Update Password</Button>
  );
};

export default UpdatePasswordButton;