import React from "react";
import { Flex, Text } from "@chakra-ui/react";

interface TerminalWorkspaceProps {}

export const TerminalWorkspace: React.FC<TerminalWorkspaceProps> = () => {

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
                Terminal Workspace
            </Text>
        </Flex> 
  );
};