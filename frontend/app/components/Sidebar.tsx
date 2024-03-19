import React from "react";
import { Box, IconButton, Flex } from "@chakra-ui/react";
import { AvatarBox } from "./AvatarBox";
import { MdMenu } from "react-icons/md";
import { Logo } from "./Logo";
import { Navigation } from "./Navigation";

interface SidebarProps {
  collapse: boolean;
  setCollapse: (collapse: boolean) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ collapse, setCollapse }) => (
  <React.Fragment>
    <Box w="full">
      <Logo collapse={collapse} />
      <Navigation collapse={collapse} />
    </Box>
    <Flex
      alignItems="center"
      justifyContent={collapse ? "space-between" : "center"}
      flexDirection={collapse ? "row-reverse" : "column"}
      position="relative"
      w="full"
    >
      <IconButton
        aria-label="Menu Colapse"
        icon={<MdMenu />}
        color="black"
        bg="gray.300"
        onClick={() => setCollapse(!collapse)}
      />
      <AvatarBox collapse={collapse} />
    </Flex>
  </React.Fragment>
);
