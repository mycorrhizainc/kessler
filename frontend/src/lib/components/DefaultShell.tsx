"use client";
import {
  SignInButton,
  SignedIn,
  SignedOut,
  UserButton,
} from "@clerk/nextjs";
import {
  Box,
  IconButton,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalBody,
} from "@chakra-ui/react";
import {
  AppShell,
  Sidebar,
  SidebarOverlay,
  SidebarSection,
  NavItem,
  NavGroup,
  SearchInput,
} from "@saas-ui/react";
import React, { useState } from "react";
import { Node } from "reactflow";
import {
  FiChevronsLeft,
  FiChevronsRight,
  FiMessageCircle,
  FiFeather,
} from "react-icons/fi";

import { usePathname } from "next/navigation";
import ColorModeToggle from "./ColorModeToggle";

// import SearchDialog from "./SearchDialog";

export default function Page({ children }: { children: React.ReactNode }) {
  const [isOpen, toggleOpen] = useState(true);
  const [searchModal, changeSearchModal] = useState(false);

  const toggleSearchModal = () => {
    changeSearchModal(!searchModal);
  };

  const pathname = usePathname();

  function pathIs(name: string) {
    let leafName = pathname.split("/")[-1];
    if (leafName == name) {
      return true;
    }
    return false;
  }
  return (
    <AppShell
      variant="static"
      minH="100vh"
      sidebar={
        <Sidebar
          toggleBreakpoint={false}
          variant={isOpen ? "default" : "compact"}
          transition="width"
          transitionDuration="normal"
          width={isOpen ? "280px" : "16"}
          minWidth="auto"
        >
          <SidebarSection>
            <NavItem
              padding="3px"
              display="flex"
              alignItems="center"
              justifyContent="center"
            >
              <SignedOut>
                <SignInButton />
              </SignedOut>
              <SignedIn>
                <UserButton />
              </SignedIn>
            </NavItem>
          </SidebarSection>
          <SidebarSection direction={isOpen ? "row" : "column"}>
            <IconButton
              onClick={() => {
                toggleOpen(!isOpen);
              }}
              variant="ghost"
              size="sm"
              icon={isOpen ? <FiChevronsLeft /> : <FiChevronsRight />}
              aria-label="Toggle Sidebar"
            />
          </SidebarSection>

          <SidebarSection flex="1" overflowY="auto" overflowX="hidden">
            <NavGroup>
              <NavItem
                href="/"
                icon={<FiMessageCircle />}
                isActive={pathIs("")}
              >
                Chat with Documents
              </NavItem>
              <NavItem
                href="/documents"
                icon={<FiFeather />}
                isActive={pathIs("documents")}
              >
                Modify Document Database
              </NavItem>
              <NavItem
                href="/basic-chat"
                icon={<FiMessageCircle />}
                isActive={pathIs("basic-chat")}
              >
                Basic LLM Chat
              </NavItem>
              {
                // <NavItem icon={<FiBookmark />} isActive={pathIs("saved")}>
                //   Saved Documents (BROKEN)
                // </NavItem>
              }
              {/* <SearchDialog /> */}
            </NavGroup>
          </SidebarSection>
          <SidebarOverlay zIndex="1" />
          <ColorModeToggle />
        </Sidebar>
      }
    >
      <Box as="main" flex="1" py="2" px="4">
        {children}
      </Box>
      <Modal isOpen={searchModal} onClose={toggleSearchModal}>
        <ModalOverlay />
        <ModalContent maxH="1500px" maxW="1500px" overflow="scroll">
          <ModalBody>
            <SearchInput placeholder="Search" />
          </ModalBody>
        </ModalContent>
      </Modal>
    </AppShell>
  );
}
