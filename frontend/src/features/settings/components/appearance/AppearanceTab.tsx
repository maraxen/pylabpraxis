import React from 'react';
import { Text } from '@chakra-ui/react';
import { Card, CardBody, Fieldset, FieldsetContent, FieldsetLegend } from "@praxis-ui";

const AppearanceTab: React.FC = () => (
  <Card>
    <CardBody>
      <Fieldset>
        <FieldsetLegend>Appearance Settings</FieldsetLegend>
        <FieldsetContent>
          <Text>Additional appearance settings will be available in future updates.</Text>
        </FieldsetContent>
      </Fieldset>
    </CardBody>
  </Card>
);

export default AppearanceTab;