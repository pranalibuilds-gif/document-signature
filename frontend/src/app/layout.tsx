import type { Metadata } from "next";
import { Inter, Dancing_Script, Great_Vibes, Pinyon_Script, Cormorant_Garamond } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });
const dancingScript = Dancing_Script({ subsets: ["latin"], variable: "--font-dancing" });
const greatVibes = Great_Vibes({ subsets: ["latin"], weight: "400", variable: "--font-vibes" });
const pinyonScript = Pinyon_Script({ subsets: ["latin"], weight: "400", variable: "--font-pinyon" });
const cormorant = Cormorant_Garamond({ subsets: ["latin"], weight: "400", variable: "--font-cormorant", style: "italic" });

export const metadata: Metadata = {
  title: "DocuSign Mini | Secure Document Signing",
  description: "A professional-grade document signature platform built with FastAPI and Next.js.",
  icons: {
    icon: "/favicon.svg",
  },
  openGraph: {
    title: "DocuSign Mini",
    description: "Professional document signing workflows.",
    type: "website",
    siteName: "DocuSign Mini",
  }
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${inter.variable} ${dancingScript.variable} ${greatVibes.variable} ${pinyonScript.variable} ${cormorant.variable}`}>
      <body className="font-sans">
        <main className="min-h-screen">
          {children}
        </main>
      </body>
    </html>
  );
}
