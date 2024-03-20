import React from "react";
import { Flex, Text } from "@chakra-ui/react";
import Editor from "@monaco-editor/react";

interface EditorWorkspaceProps {}

export const EditorWorkspace: React.FC<EditorWorkspaceProps> = () => {
  const handleEditorChange = (value: string | undefined) => {};

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
      <Editor
        height="100%"
        defaultLanguage="javascript"
        defaultValue="// Welcome to MirkoAI!"
        theme="vs-dark"
        onChange={handleEditorChange}
      />
    </Flex>
  );
};
