import React from "react";

import { Flex, HStack, IconButton } from "@chakra-ui/react";
import { Timeline } from '../components/Timeline'
import { Workspace } from '../components/Workspace'

interface WorkspaceTimelineProps {}

export const WorkspaceTimeline: React.FC<WorkspaceTimelineProps> = () => {

  return (
        <HStack w="full" h="100vh" bg="gray.900" padding={1}>
          <Flex
            as="aside"
            w="full"
            h="full"
            bg="gray.700"
            alignItems="center"
            padding={4}
            flexDirection="column"
            justifyContent="center"
            transition="ease-in-out .2s"
            borderRadius="2xl"
          >
            <Timeline />
          </Flex>
          <Flex
            as="aside"
            w="full"
            h="full"
            bg="gray.700"
            alignItems="center"
            justifyContent="center"
            flexDirection="column"
            position="relative"
            borderRadius="2xl"
            padding={4}
          >
            <Workspace />
          </Flex>
        </HStack>
  );
};