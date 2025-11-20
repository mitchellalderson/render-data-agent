import "./globals.css";
import type { ReactNode } from "react";

export const metadata = {
  title: "Data Analyst Agent",
  description: "Chat with your signup and ICP data"
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
