import React from 'react';
import { VStack, Text } from '@chakra-ui/react';
import { Button, Card, CardBody, Fieldset, FieldsetContent, FieldsetLegend } from "@praxis-ui";
import { useOidc } from '../../../../oidc';

const SecurityTab: React.FC = () => {
  const { backFromAuthServer, goToAuthServer } = useOidc();

  const handleChangePassword = () => {
    goToAuthServer({
      extraQueryParams: { kc_action: "UPDATE_PASSWORD" }
    });
  };

  return (
    <Card>
      <CardBody>
        <Fieldset defaultOpen>
          <FieldsetLegend>Security Settings</FieldsetLegend>
          <FieldsetContent>
            <VStack gap={4}>
              <Button
                width="full"
                visual="solid"
                onClick={() => handleChangePassword()}
              >
                Change Password
              </Button>
              {backFromAuthServer?.extraQueryParams.kc_action === "UPDATE_PASSWORD" && (
                <Text color={backFromAuthServer.result.kc_action_status === "success" ? "green.500" : "gray.500"}>
                  {backFromAuthServer.result.kc_action_status === "success"
                    ? "Password successfully updated"
                    : "Password unchanged"}
                </Text>
              )}
            </VStack>
          </FieldsetContent>
        </Fieldset>
      </CardBody>
    </Card>
  );
};

export default SecurityTab;