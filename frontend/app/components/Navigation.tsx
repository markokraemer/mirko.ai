import { List, ListItem } from "@chakra-ui/react";
import {
  MdOutlineSpaceDashboard,
  MdHistory,
} from "react-icons/md";
import { NavItem } from "./NavItem";

const items = [
  {
    type: "link",
    label: "Workspace",
    icon: MdOutlineSpaceDashboard,
    path: "/",
  },
  {
    type: "header",
    label: "Account",
  },
  {
    type: "link",
    label: "Threads",
    icon: MdHistory,
    path: "/",
    notifications: 1,
  }
];

export const Navigation = ({ collapse }) => (
  <List w="full" my={8}>
    {items.map((item, index) => (
      <ListItem key={index}>
        <NavItem item={item} isActive={index === 0} collapse={collapse} />
      </ListItem>
    ))}
  </List>
);