import { Avatar, Flex, IconButton, Text } from "@chakra-ui/react";
import { MdOutlineMoreHoriz } from "react-icons/md";

interface AvatarBoxProps {
  collapse: boolean;
}

export const AvatarBox: React.FC<AvatarBoxProps>  = ({ collapse }) => (
  <Flex
    w="full"
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
        color="white"
      >
        <Text fontSize="sm" fontWeight="bold" pb="0" lineHeight={0}>
            John Doe
        </Text>
        <Text as="small" color="gray.300" fontSize={12} lineHeight={0}>
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