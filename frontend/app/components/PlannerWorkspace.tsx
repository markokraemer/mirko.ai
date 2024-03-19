import React from "react";
import { Flex, Text } from "@chakra-ui/react";

interface EditorWorkspaceProps {}

export const PlannerWorkspace: React.FC<EditorWorkspaceProps> = () => {

  return (
        <Flex
            as="main"
            w="full"
            h="full"
            bg="gray.100"
            alignItems="center"
            justifyContent="center"
            flexDirection="column"
            position="relative"
            borderRadius="2xl"
        >
            <Text fontSize={50} color="gray.300">
                Planner Workspace
            </Text>
        </Flex> 
  );
};