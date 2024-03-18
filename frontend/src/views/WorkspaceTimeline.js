import React from "react";

import { Flex, HStack, IconButton } from "@chakra-ui/react";
import { MdMenu } from "react-icons/md";
import { Timeline } from '../components/Timeline'
import { Workspace } from '../components/Workspace'

export const WorkspaceTimeline = ({ collapse, setCollapse }) => {

  return (
    // <Flex padding={0}>
        <HStack w="full" h="100vh" bg="white" padding={1}>
          <Flex
            as="aside"
            w="full"
            h="full"
            bg="gray.100"
            alignItems="center"
            padding={4}
            flexDirection="column"
            justifyContent="center"
            transition="ease-in-out .2s"
            borderRadius="2xl"
          >

            <Flex
                w="full"
                h={12}
                bg="white"
                alignItems="start"
                justifyContent="start"
                flexDirection="column"
                // position="relative"
                borderRadius="2xl"
                marginBottom={4}
                padding={2}
            >
                <IconButton
                    aria-label="Menu Colapse"
                    icon={<MdMenu />}
                    color="black"
                    bg="gray.100"
                    onClick={() => setCollapse(!collapse)}
                />
            </Flex>
            <Timeline />
          </Flex>
          <Flex
            as="aside"
            w="full"
            h="full"
            bg="gray.100"
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
    // </Flex>
  );
};