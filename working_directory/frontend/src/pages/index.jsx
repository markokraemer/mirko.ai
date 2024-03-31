import { Box, VStack, Heading, Button, Text, useColorModeValue, Center } from '@chakra-ui/react';
import { BrandLogo } from '@components/BrandLogo';

const Home = () => {
  const bgColor = useColorModeValue('orange.100', 'orange.800');
  const textColor = useColorModeValue('gray.800', 'whiteAlpha.900');

  return (
    <Center bg={bgColor} color={textColor} minH="100vh" py="12" px={{ base: '4', lg: '8' }}>
      <VStack spacing="8">
        <BrandLogo />
        <Heading as="h1" size="xl" textAlign="center">
          Welcome to ConstroCo!
        </Heading>
        <Text textAlign="center">
          Your premier partner in civil and construction projects. With a commitment to excellence and innovation, we bring your visions to life.
        </Text>
        <Button colorScheme="yellow" size="lg">
          Contact Us
        </Button>
      </VStack>
    </Center>
  );
};

export default Home;