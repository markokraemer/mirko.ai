import React from "react";
import { Flex, Tabs, Tab, TabList, Divider } from "@chakra-ui/react";
import { TerminalWorkspace } from "./TerminalWorkspace";
import { PlannerWorkspace } from "./PlannerWorkspace";
import { EditorWorkspace } from "./EditorWorkspace";
import { BrowserWorkspace } from "./BrowserWorkspace";

export const Workspace = () => {

    const [activeWorkspace, setShowActiveWorkspace] = React.useState('terminal');

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
        padding={4}
    >
        <Flex
            as="main"
            w="full"
            bg="white"
            alignItems="start"
            justifyContent="start"
            flexDirection="column"
            position="relative"
            borderRadius="2xl"
        >
            <Tabs isFitted variant='enclosed'>
                <TabList>
                    <Tab onClick={() => setShowActiveWorkspace('terminal')}>Terminal</Tab>
                    <Tab onClick={() => setShowActiveWorkspace('browser')}>Browser</Tab>
                    <Tab onClick={() => setShowActiveWorkspace('editor')}>Editor</Tab>
                    <Tab onClick={() => setShowActiveWorkspace('planner')}>Planner</Tab>
                </TabList>
            </Tabs>
            <Divider  marginTop={2} marginBottom={2} />
        </Flex>
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
            margin
        >
            {activeWorkspace === 'terminal' && (<TerminalWorkspace/>)}
            {activeWorkspace === 'browser' && (<BrowserWorkspace/>)}
            {activeWorkspace === 'editor' && (<EditorWorkspace/>)}
            {activeWorkspace === 'planner' && (<PlannerWorkspace/>)}
        </Flex>
    </Flex> 
  );
};