import { Box, VStack, Heading, Button, Text, useColorModeValue, Center } from '@chakra-ui/react';
import { BrandLogo } from '@components/BrandLogo';

const MirkoLandingPage = () => {
  const bgColor = useColorModeValue('blue.100', 'blue.800');
  const textColor = useColorModeValue('gray.800', 'whiteAlpha.900');

  return (
    <Center bg={bgColor} color={textColor} minH="100vh" py="12" px={{ base: '4', lg: '8' }}>
      <VStack spacing="8">
        <BrandLogo />
        <Heading as="h1" size="xl" textAlign="center">
          Meet Mirko - The AI Software Engineer
        </Heading>
        <Text textAlign="center">
          Advancing technology with innovation and precision. Specializing in AI software solutions, Mirko is your go-to expert for creating dynamic, intelligent systems that drive success.
        </Text>
        <Button colorScheme="blue" size="lg">
          Learn More
        </Button>
      </VStack>
    </Center>
  );
};

export default MirkoLandingPage;