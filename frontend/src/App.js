
import { Flex, HStack } from "@chakra-ui/react";
import React from "react";
import { Sidebar } from "./components/Sidebar";
import { WorkspaceTimeline } from "./views/WorkspaceTimeline";
import './App.css';

function App() {

  const [collapse, setCollapse] = React.useState(false);

  return (
    <div className="App">
      <HStack w="full" h="100vh" bg="white" padding={4}>
      <Flex
        as="aside"
        w="full"
        h="full"
        maxW={collapse ? 350 : 100}
        bg="gray.100"
        alignItems="start"
        padding={6}
        flexDirection="column"
        justifyContent="space-between"
        transition="ease-in-out .2s"
        borderRadius="2xl"
      >
        <Sidebar collapse={collapse} />
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
      >
          <WorkspaceTimeline collapse={collapse} setCollapse={setCollapse} />
      </Flex>
    </HStack>
    </div>
  );
}

export default App;
