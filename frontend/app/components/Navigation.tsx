import { List, ListItem } from "@chakra-ui/react";
import {
  MdOutlineSpaceDashboard,
  MdHistory,
} from "react-icons/md";
import { NavItem } from "./NavItem";
import { IconType } from "react-icons";

interface NavigationProps {
  collapse: boolean;
}

interface NavItemType {
  type: "link" | "header";
  label: string;
  icon?: IconType;
  path?: string;
  notifications?: number;
}

const items: NavItemType[] = [
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

export const Navigation: React.FC<NavigationProps> = ({ collapse }) => (
  <List w="full" my={8} color="white">
    {items.map((item, index) => (
      <ListItem key={index} color="white">
        <NavItem item={item} isActive={index === 0} collapse={collapse} />
      </ListItem>
    ))}
  </List>
);