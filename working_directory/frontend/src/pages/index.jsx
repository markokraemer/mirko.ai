import { Box, VStack, Heading, Button, Text, useColorModeValue, Center } from '@chakra-ui/react';
import { BrandLogo } from '@components/BrandLogo';

const Home = () => {
  const bgColor = useColorModeValue('gray.50', 'gray.800');
  const textColor = useColorModeValue('gray.800', 'whiteAlpha.900');

  return (
    <Center bg={bgColor} color={textColor} minH="100vh" py="12" px={{ base: '4', lg: '8' }}>
      <VStack spacing="8">
        <BrandLogo />
        <Heading as="h1" size="xl" textAlign="center">
          Welcome to your App!
        </Heading>
        <Text textAlign="center">
          Create tasks with instructions to edit your app and customize it.
        </Text>
        <Button colorScheme="pink" size="lg">
          Start
        </Button>
      </VStack>
    </Center>
  );
};

export default Home;
