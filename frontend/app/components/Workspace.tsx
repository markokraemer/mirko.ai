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
        bg="gray.900"
        alignItems="center"
        justifyContent="center"
        flexDirection="column"
        position="relative"
        borderRadius="2xl"
    >
        <Flex
            as="main"
            w="full"
            bg="gray.700"
            alignItems="start"
            justifyContent="start"
            flexDirection="column"
            position="relative"
            borderTopRadius="2xl"
        >
            <Tabs variant='soft-rounded' margin={2}>
                <TabList>
                    <Tab color="white" bg={activeWorkspace === 'terminal' ? "gray.300" : "gray.900"} marginRight={2} onClick={() => setShowActiveWorkspace('terminal')}>Terminal</Tab>
                    <Tab color="white" bg={activeWorkspace === 'browser' ? "gray.300" : "gray.900"} marginRight={2} onClick={() => setShowActiveWorkspace('browser')}>Browser</Tab>
                    <Tab color="white" bg={activeWorkspace === 'editor' ? "gray.300" : "gray.900"} marginRight={2} onClick={() => setShowActiveWorkspace('editor')}>Editor</Tab>
                    <Tab color="white" bg={activeWorkspace === 'planner' ? "gray.300" : "gray.900"} marginRight={2} onClick={() => setShowActiveWorkspace('planner')}>Planner</Tab>
                </TabList>
            </Tabs>

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
            borderBottomRadius="2xl"
        >
            {activeWorkspace === 'terminal' && (<TerminalWorkspace/>)}
            {activeWorkspace === 'browser' && (<BrowserWorkspace/>)}
            {activeWorkspace === 'editor' && (<EditorWorkspace/>)}
            {activeWorkspace === 'planner' && (<PlannerWorkspace/>)}
        </Flex>
    </Flex> 
  );
};