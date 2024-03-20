import React from "react";
import { Flex, Input, Text, IconButton } from "@chakra-ui/react";
import { MdOutlineSend } from "react-icons/md";

interface TimelineProps {}

export const Timeline: React.FC<TimelineProps> = () => {

  return (
        <Flex
            as="main"
            w="full"
            h="full"
            bg="gray.700"
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
                bg="gray.900"
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
                bg="gray.900"
                alignItems="center"
                justifyContent="center"
                flexDirection="row"
                position="relative"
                borderRadius="2xl"
                paddingLeft={4}
                paddingRight={4}
                marginTop={2}
            >
                <Input placeholder='Ask MirkoAI' marginRight={2} />
                <IconButton bg="gray.300" aria-label='Search database' icon={<MdOutlineSend />} />
            </Flex> 
        </Flex> 
  );
};