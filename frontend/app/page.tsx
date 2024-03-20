'use client'

import { useState } from 'react';

import { Flex, HStack } from "@chakra-ui/react";
import React from "react";
import { Sidebar } from "./components/Sidebar";
import { WorkspaceTimeline } from "./views/WorkspaceTimeline";

export default function Home() {
  const [collapse, setCollapse] = useState(false);

  return (
    <div className="App">
      <HStack w="full" h="100vh" bg="gray.900" padding={4}>
      <Flex
        as="aside"
        w="full"
        h="full"
        maxW={collapse ? 350 : 100}
        bg="gray.700"
        alignItems="start"
        padding={6}
        flexDirection="column"
        justifyContent="space-between"
        transition="ease-in-out .2s"
        borderRadius="2xl"
      >
        <Sidebar collapse={collapse} setCollapse={setCollapse} />
      </Flex>
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
        <WorkspaceTimeline />
      </Flex>
    </HStack>
    </div>
  );
}
