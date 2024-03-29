import { Text, HStack } from '@chakra-ui/react';
import { GrStatusPlaceholderSmall } from "react-icons/gr";

export const BrandLogo = () => (
  <HStack spacing={2} alignItems="center">
    <GrStatusPlaceholderSmall size="32px" /> {/* TODO: Replace the Icon with an actual icon suitable to the brand */}
    <Text fontSize="xl" fontWeight="bold">
      YourApp.com {/* TODO: Replace the Logo Name with the actual brand app name */}
    </Text>
  </HStack>
);
