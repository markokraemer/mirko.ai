import { Box, VStack, Heading, Button, Text, useColorModeValue, Center } from '@chakra-ui/react';
import { BrandLogo } from '@components/BrandLogo';

const LandingPage = () => {
  const bgColor = useColorModeValue('orange.100', 'orange.800');
  const textColor = useColorModeValue('gray.800', 'whiteAlpha.900');

  return (
    <Center bg={bgColor} color={textColor} minH="100vh" py="12" px={{ base: '4', lg: '8' }}>
      <VStack spacing="8">
        <BrandLogo />
        <Heading as="h1" size="xl" textAlign="center">
          Welcome to ConstroCo! Your Construction Partner
        </Heading>
        <Text textAlign="center">
          Specializing in commercial, residential, and infrastructural projects, we ensure unparalleled service and quality. Let us build your dream project together.
        </Text>
        <Button colorScheme="orange" size="lg">
          Discover More
        </Button>
      </VStack>
    </Center>
  );
};

export default LandingPage;