import React from 'react';
import { Box, Link, useColorModeValue } from '@chakra-ui/react';

export const MadeWithSGBadge = () => {
  const bgColor = useColorModeValue('whiteAlpha.900', 'blackAlpha.900');
  const textColor = useColorModeValue('gray.800', 'whiteAlpha.900');
  const boxShadowColor = useColorModeValue('md', 'dark-lg');
  const hoverBgColor = useColorModeValue('gray.100', 'whiteAlpha.500');

  return (
    <Box position="fixed" bottom="0" right="0" zIndex="tooltip">
      <Link href="https://www.softgen.ai" isExternal>
        <Box
          background={bgColor}
          color={textColor}
          fontSize="xs"
          p="2"
          borderTopLeftRadius="lg"
          boxShadow={boxShadowColor}
          _hover={{ bg: hoverBgColor }}
          transition="background 0.3s ease"
        >
          Made with 🤖 by SoftGen.ai
        </Box>
      </Link>
    </Box>
  );
};
