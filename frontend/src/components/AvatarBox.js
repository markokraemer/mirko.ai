import { Avatar, Flex, IconButton, Text } from "@chakra-ui/react";
import { MdOutlineMoreHoriz } from "react-icons/md";

export const AvatarBox = ({ collapse }) => (
  <Flex
    borderWidth={collapse ? 1 : 0}
    borderColor="gray.100"
    borderRadius="full"
    w="full"
    p={2}
    alignItems="center"
    justifyContent="space-between"
    gap={2}
    flexDirection={collapse ? "row" : "column-reverse"}
  >
    <Avatar name="John Doe" bg="teal.300" />
    {collapse && (
      <Flex
        w="full"
        flexDirection="column"
        gap={4}
        justifyContent="center"
        alignItems="flex-start"
      >
        <Text fontSize="sm" fontWeight="bold" pb="0" lineHeight={0}>
            John Doe
        </Text>
        <Text as="small" color="gray.500" fontSize={12} lineHeight={0}>
            john@doe.com
        </Text>
      </Flex>
    )}

    <IconButton
      aria-label="Settings"
      icon={<MdOutlineMoreHoriz />}
      borderRadius="full"
      color="gray.400"
      variant="ghost"
      fontSize={20}
    />
  </Flex>
);