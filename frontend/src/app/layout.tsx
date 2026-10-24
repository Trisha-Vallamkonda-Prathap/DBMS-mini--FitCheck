import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "FitCheck — Cross-Brand Apparel Fit Intelligence",
  description:
    "Cross-brand women's apparel sizing intelligence combining structured dimensional matching with semantic vector search for fit complaints.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
