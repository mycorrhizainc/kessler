"use client";
import { SignUp } from "@clerk/nextjs";
import { Center } from "@chakra-ui/react";

export default function Page() {
  return <Center justifyContent="center">
   <SignUp path="/sign-up" signInUrl="/sign-in" />
   </Center>
}
