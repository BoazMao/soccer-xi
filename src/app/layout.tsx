import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = { title: "World Cup XI", description: "Draft an all-time World Cup XI." };
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
