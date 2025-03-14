import React from 'react';
import { VStack } from '@chakra-ui/react';
import { Card, CardBody } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { LuPlay } from 'react-icons/lu';

interface ProtocolReviewTemplateProps {
  isLoading: boolean;
  onStartProtocol: (e: React.FormEvent) => void;
}

export const ProtocolReviewTemplate: React.FC<ProtocolReviewTemplateProps> = ({
  isLoading,
  onStartProtocol
}) => {
  return (
    <Card>
      <CardBody>
        <VStack gap={4}>
          <Button
            type="submit"
            visual="solid"
            loading={isLoading}
            width="full"
            onClick={onStartProtocol}
          >
            <LuPlay />Start Protocol
          </Button>
        </VStack>
      </CardBody>
    </Card>
  );
};