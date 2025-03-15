import React from 'react';
import { VStack } from '@chakra-ui/react';
import { Fieldset, FieldsetContent, FieldsetLegend, Button } from "@praxis-ui";
import { LuDatabase, LuActivity } from "react-icons/lu";

const SystemSettings: React.FC = () => (
  <Fieldset>
    <FieldsetLegend>System Settings</FieldsetLegend>
    <FieldsetContent>
      <VStack align="stretch" gap={4}>
        <Button visual="outline">
          <LuDatabase size={16} />
          Database Configuration
        </Button>
        <Button visual="outline">
          <LuActivity size={16} />
          View System Logs
        </Button>
      </VStack>
    </FieldsetContent>
  </Fieldset>
);

export default SystemSettings;