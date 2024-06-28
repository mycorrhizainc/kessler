import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { dark, neobrutalism } from '@clerk/themes';
import { ClerkProvider } from "@clerk/nextjs";
import { SaasProvider } from "@saas-ui/react";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Kessler Search",
  description: "the kessler search engine",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ClerkProvider
      appearance={{
        baseTheme: dark
      }}
    >
      <html lang="en">
        <body>
          <SaasProvider>{children}</SaasProvider>
        </body>
      </html>
    </ClerkProvider>
  );
}
