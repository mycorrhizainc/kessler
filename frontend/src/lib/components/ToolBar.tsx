import useGraphStore, { GraphState } from "../utils/GraphUtilities";
import { Node, Edge } from "reactflow";
import axios from "axios";
import { useState, useEffect } from "react";
import { shallow } from "zustand/shallow";
import * as React from "react";

import { usePathname, useRouter } from "next/navigation";

// mui elements
import Box from "@mui/joy/Box";
import ListItemDecorator from "@mui/joy/ListItemDecorator";
import Tabs from "@mui/joy/Tabs";
import TabList from "@mui/joy/TabList";
import Tab, { tabClasses } from "@mui/joy/Tab";
import Tooltip from "@mui/joy/Tooltip";
import BottomNavigation from "@mui/material/BottomNavigation";
import BottomNavigationAction from "@mui/material/BottomNavigationAction";
// icons
import HomeRoundedIcon from "@mui/icons-material/HomeRounded";
import FavoriteBorder from "@mui/icons-material/FavoriteBorder";
import Search from "@mui/icons-material/Search";
import Person from "@mui/icons-material/Person";
import SettingsIcon from "@mui/icons-material/Settings";
import { Bookmark, Home, SatelliteAlt } from "@mui/icons-material";
import CollectionsBookmarkIcon from "@mui/icons-material/CollectionsBookmark";

const ToolBar = () => {
  const pathname = usePathname();
  const [index, setIndex] = React.useState(-1);
  const color = "success";
  const router = useRouter();

  const pathval: { [key: string]: number } = {
    realms: 1,
    search: 2,
    browse: 3,
    settings: 4,
  };
  const handleNav = (event: any, value: any) => {
    setIndex(value as number);

    if (value == 0) {
      router.push("/");
    }
    let path = Object.keys(pathval).find((key) => pathval[key] === value);
    if (path === undefined) path = ""
    router.push(`/${path}`);
  };
  useEffect(() => {
    let path = pathname.substring(pathname.lastIndexOf("/") + 1);

    console.log("PATH:", path);

    if (path == "") {
      setIndex(0);
      return;
    }
    if (pathval[path]) setIndex(pathval[path]);
  }, []);
  return (
    <div className="absolute justify-center mb-7 place-content-center inset-x-0 bottom-2 z-10">
      <Tabs
        size="lg"
        aria-label="Bottom Navigation"
        value={index}
        onChange={handleNav}
        sx={(theme) => ({
          p: 1,
          borderRadius: 16,
          maxWidth: 400,
          mx: "auto",
          boxShadow: theme.shadow.sm,
          [`& .${tabClasses.root}`]: {
            py: 1,
            flex: 1,
            transition: "0.3s",
            fontWeight: "md",
            fontSize: "md",
            [`&:not(.${tabClasses.selected}):not(:hover)`]: {
              opacity: 0.7,
            },
          },
        })}
      >
        <TabList
          variant="plain"
          size="sm"
          disableUnderline
          sx={{ borderRadius: "lg", p: 0 }}
        >
          <Tooltip title="Home">
            <Tab
              disableIndicator
              orientation="vertical"
              indicatorPlacement="bottom"
              {...(index === 0 && { color: color })}
            >
              <ListItemDecorator>
                <HomeRoundedIcon />
              </ListItemDecorator>
            </Tab>
          </Tooltip>
          <Tooltip title="Realms">
            <Tab
              disableIndicator
              orientation="vertical"
              indicatorPlacement="bottom"
              {...(index === 1 && { color: color })}
            >
              <ListItemDecorator>
                <SatelliteAlt />
              </ListItemDecorator>
            </Tab>
          </Tooltip>
          <Tooltip title="Search">
            <Tab
              disableIndicator
              orientation="vertical"
              indicatorPlacement="bottom"
              {...(index === 2 && { color: color })}
            >
              <ListItemDecorator>
                <Search />
              </ListItemDecorator>
            </Tab>
          </Tooltip>
          <Tooltip title="Browse">
            <Tab
              disableIndicator
              orientation="vertical"
              indicatorPlacement="bottom"
              {...(index === 3 && { color: color })}
            >
              <ListItemDecorator>
                <CollectionsBookmarkIcon />
              </ListItemDecorator>
            </Tab>
          </Tooltip>
          <Tooltip title="Settings">
            <Tab
              disableIndicator
              orientation="vertical"
              indicatorPlacement="bottom"
              {...(index === 4 && { color: color })}
            >
              <ListItemDecorator>
                <SettingsIcon />
              </ListItemDecorator>
            </Tab>
          </Tooltip>
        </TabList>
      </Tabs>
    </div>
  );
};

export default ToolBar;
