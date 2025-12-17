import type { Metadata } from "next";
import localFont from "next/font/local";
import "./globals.css";
import SmoothScroll from "~/components/SmoothScroll";

const gothamRounded = localFont({
  src: [
    {
      path: "../../public/fonts/gothamrnd_book.otf",
      weight: "400",
      style: "normal",
    },
    {
      path: "../../public/fonts/gothamrnd_medium.otf",
      weight: "500",
      style: "normal",
    },
    {
      path: "../../public/fonts/gothamrnd_bold.otf",
      weight: "700",
      style: "normal",
    },
  ],
  variable: "--font-gotham-rounded",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Grido Fiestas Mágicas - Enviá tu saludo navideño",
  description:
    "Creá un saludo mágico de la mano de Papá Noel y Grido para estas fiestas",
  icons: {
    icon: [
      {
        url: "/images/FAVICON 16X16PX.jpg",
        sizes: "16x16",
        type: "image/jpeg",
      },
      {
        url: "/images/FAVICON 32X32PX.jpg",
        sizes: "32x32",
        type: "image/jpeg",
      },
    ],
  },
  openGraph: {
    title: "Grido Fiestas Mágicas - Enviá tu saludo navideño",
    description:
      "Creá un saludo mágico de la mano de Papá Noel y Grido para estas fiestas",
    images: [
      {
        url: "/images/hero-background.png",
        width: 1280,
        height: 831,
        alt: "Grido Fiestas Mágicas",
      },
    ],
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Grido Fiestas Mágicas - Enviá tu saludo navideño",
    description:
      "Creá un saludo mágico de la mano de Papá Noel y Grido para estas fiestas",
    images: ["/images/hero-background.png"],
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es">
      <body className={`${gothamRounded.variable} antialiased`}>
        <SmoothScroll>{children}</SmoothScroll>
      </body>
    </html>
  );
}
