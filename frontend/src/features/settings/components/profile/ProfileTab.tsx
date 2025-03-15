import React from 'react';
import { VStack, HStack, Text } from '@chakra-ui/react';
import { Avatar, Button, Card, CardBody, Fieldset, FieldsetContent, FieldsetLegend } from "@praxis-ui";
import { useOidc } from '../../../../oidc';
import { selectUserProfile } from '../../../users/store/userSlice';

const ProfileTab: React.FC = () => {
  const { decodedIdToken, goToAuthServer } = useOidc();
  const userProfile = selectUserProfile(decodedIdToken);

  return (
    <Card>
      <CardBody>
        <Fieldset defaultOpen>
          <FieldsetLegend>Profile Management</FieldsetLegend>
          <FieldsetContent>
            <VStack align="start" gap={4}>
              <HStack gap={4} width="full">
                <Avatar
                  size="xl"
                  name={userProfile.username}
                  src={userProfile.picture}
                />
                <VStack align="start" gap={2}>
                  <Button
                    visual="outline"
                    onClick={() => goToAuthServer({
                      extraQueryParams: { kc_action: "UPDATE_PROFILE" }
                    })}
                  >
                    Edit Profile
                  </Button>
                  <Text fontSize="sm" color="gray.600">
                    Edit your profile information on Keycloak
                  </Text>
                </VStack>
              </HStack>
            </VStack>
          </FieldsetContent>
        </Fieldset>
      </CardBody>
    </Card>
  );
};

export default ProfileTab;