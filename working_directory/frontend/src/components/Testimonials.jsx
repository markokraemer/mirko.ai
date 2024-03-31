import React from 'react';
import { Box, Heading, Text, VStack } from '@chakra-ui/react';

export const Testimonials = () => (
  <VStack spacing="4" align="stretch">
    <Heading as="h3" size="lg" textAlign="center">Testimonials</Heading>
    <Box p="5" shadow="md" borderWidth="1px">
      <Text mt="4">ConstroCo handled our project professionally from start to finish. The attention to detail was incredible, and we couldn't be happier with the result. - Client A</Text>
    </Box>
    <Box p="5" shadow="md" borderWidth="1px">
      <Text mt="4">I was amazed at the speed and quality of construction. ConstroCo's team was friendly and highly skilled. Highly recommend! - Client B</Text>
    </Box>
  </VStack>
);