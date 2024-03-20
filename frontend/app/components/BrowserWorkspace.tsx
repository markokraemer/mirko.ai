import React from "react";
import { Flex, Text } from "@chakra-ui/react";

interface BrowserWorkspaceProps {}

export const BrowserWorkspace: React.FC<BrowserWorkspaceProps> = () => {

  return (
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
            <Text fontSize={50} color="gray.300">
                Browser Workspace
            </Text>
        </Flex> 
  );
};