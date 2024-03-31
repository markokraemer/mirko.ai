import React from 'react';
import { SimpleGrid, Image, Box, Heading } from '@chakra-ui/react';

export const Portfolio = () => (
  <Box py="8">
    <Heading as="h3" size="lg" textAlign="center">Our Projects</Heading>
    <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing="8" pt="4">
      <Image src="/project1.jpg" alt="Project 1" boxSize="100%" objectFit="cover" />
      <Image src="/project2.jpg" alt="Project 2" boxSize="100%" objectFit="cover" />
      <Image src="/project3.jpg" alt="Project 3" boxSize="100%" objectFit="cover" />
    </SimpleGrid>
  </Box>
);