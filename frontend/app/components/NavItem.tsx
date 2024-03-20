import Link from "next/link";
import {
  ListIcon,
  Link as LinkChakra,
  Heading,
  Box,
  Badge,
  Text,
} from "@chakra-ui/react";
import React from "react";

import { IconType } from "react-icons";

interface NavItemProps {
  item: {
    type: string;
    label: string;
    icon?: IconType;
    notifications?: number;
    messages?: number;
  };
  isActive: boolean;
  collapse: boolean;
}


export const NavItem: React.FC<NavItemProps> = ({ item, isActive, collapse }) => {
  const { label } = item;

  if (item.type === "link") {
    const { icon, notifications, messages } = item;
    return (
      <Box display="flex" alignItems="center" my={6} justifyContent="center">
        <LinkChakra
          href=""
          as={Link}
          gap={1}
          display="flex"
          alignItems="center"
          _hover={{ textDecoration: "none", color: "black" }}
          fontWeight="medium"
          color={isActive ? "white" : "gray.400"}
          w="full"
          justifyContent={!collapse ? "center" : ""}
        >
          <ListIcon as={icon} fontSize={22} m="0" />
          {collapse && <Text>{label}</Text>}
        </LinkChakra>
        {collapse && (
          <React.Fragment>
            {notifications && (
              <Badge
                borderRadius="full"
                colorScheme="yellow"
                w={6}
                textAlign="center"
              >
                {notifications}
              </Badge>
            )}
            {messages && (
              <Badge
                borderRadius="full"
                colorScheme="green"
                w={6}
                textAlign="center"
              >
                {messages}
              </Badge>
            )}
          </React.Fragment>
        )}
      </Box>
    );
  }
  return (
    <Heading
      color="gray.400"
      fontWeight="medium"
      textTransform="uppercase"
      fontSize="sm"
      borderTopWidth={1}
      borderColor="gray.100"
      pt={collapse ? 8 : 0}
      my={6}
    >
      <Text display={collapse ? "flex" : "none"}>{label}</Text>
    </Heading>
  );
};