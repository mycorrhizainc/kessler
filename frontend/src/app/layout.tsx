import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Kessler Search",
  description: "the kessler search engine",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
<<<<<<< HEAD
      <body className={"container"+inter.className}>{children}</body>
=======
      <body className={"container h-lvh aspect-auto"+inter.className}>{children}</body>
>>>>>>> d57a0f4 (working frontend link add !)
    </html>
  );
}
