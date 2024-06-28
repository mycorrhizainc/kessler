"use client";
import { Center } from "@chakra-ui/react";  
import { SignIn } from "@clerk/nextjs";

export default function Page() {
  return (
    <Center justifyContent="center">
      <SignIn path="/sign-in" signUpUrl="/sign-up" />
    </Center>
  );
}
