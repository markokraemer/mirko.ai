import React from "react";
import { Flex, Input, Text, IconButton } from "@chakra-ui/react";
import { MdOutlineSend } from "react-icons/md";


export const Timeline = ({ collapse }) => {

  return (
        <Flex
            as="main"
            w="full"
            h="full"
            bg="white"
            alignItems="center"
            justifyContent="center"
            flexDirection="column"
            position="relative"
            borderRadius="2xl"
        >
            <Flex
                as="main"
                w="full"
                h="full"
                bg="white"
                alignItems="center"
                justifyContent="center"
                flexDirection="column"
                position="relative"
                borderRadius="2xl"
                >
                <Text fontSize={100} color="gray.300">
                    Timeline
                </Text>
            </Flex> 
            <Flex
                as="main"
                w="full"
                height={24}
                bg="white"
                alignItems="center"
                justifyContent="center"
                flexDirection="row"
                position="relative"
                borderRadius="2xl"
                paddingLeft={4}
                paddingRight={4}
            >
                <Input placeholder='Basic usage' marginRight={2} />
                <IconButton aria-label='Search database' icon={<MdOutlineSend />} />
            </Flex> 
        </Flex> 
  );
};