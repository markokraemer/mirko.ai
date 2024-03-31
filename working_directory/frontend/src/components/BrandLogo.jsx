import { Text, HStack } from '@chakra-ui/react';
import { GiBrickWall } from "react-icons/gi";

export const BrandLogo = () => (
  <HStack spacing={2} alignItems="center">
    <GiBrickWall size="32px" />
    <Text fontSize="xl" fontWeight="bold">
      ConstroCo
    </Text>
  </HStack>
);