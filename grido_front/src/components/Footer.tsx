"use client";

import Image from "next/image";
import { motion } from "motion/react";

export default function Footer() {
  return (
    <footer className="bg-grido-primary w-full">
      <div className="max-w-7xl mx-auto px-6 lg:px-[141px] py-[55px]">
        <div className="flex flex-col md:flex-row items-center justify-between gap-8">
          {/* Logo */}
          <div className="shrink-0">
            <Image
              src="/images/grido-logo.png"
              alt="Grido"
              width={100}
              height={71}
              quality={100}
              className="object-contain"
            />
          </div>

          {/* Text */}
          <p className="text-white text-center md:text-left max-w-[500px]">
          Copyright 2016. Todos los derechos reservados - Helacor - Córdoba - Argentina
          </p>

          {/* Social Links */}
          <div className="flex items-center gap-4 shrink-0">
            <motion.a
              href="https://www.tiktok.com/@gridohelado"
              target="_blank"
              rel="noopener noreferrer"
              aria-label="Seguinos en TikTok"
              whileHover={{ scale: 1.15, rotate: 5 }}
              whileTap={{ scale: 0.95 }}
              transition={{ type: "spring", stiffness: 400, damping: 17 }}
              className="block"
            >
              <svg
                width="26"
                height="26"
                viewBox="0 0 24 24"
                fill="currentColor"
                className="text-white"
              >
                <path d="M19.59 6.69a4.83 4.83 0 0 1-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 0 1-5.2 1.74 2.89 2.89 0 0 1 2.31-4.64 2.93 2.93 0 0 1 .88.13V9.4a6.84 6.84 0 0 0-1-.05A6.33 6.33 0 0 0 5 20.1a6.34 6.34 0 0 0 10.86-4.43v-7a8.16 8.16 0 0 0 4.77 1.52v-3.4a4.85 4.85 0 0 1-1-.1z" />
              </svg>
            </motion.a>
            <motion.a
              href="https://x.com/gridohelados"
              target="_blank"
              rel="noopener noreferrer"
              aria-label="Seguinos en X"
              whileHover={{ scale: 1.15, rotate: -5 }}
              whileTap={{ scale: 0.95 }}
              transition={{ type: "spring", stiffness: 400, damping: 17 }}
              className="block"
            >
              <svg
                width="26"
                height="26"
                viewBox="0 0 24 24"
                fill="currentColor"
                className="text-white"
              >
                <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
              </svg>
            </motion.a>
            <motion.a
              href="https://web.facebook.com/GridoHelados/"
              target="_blank"
              rel="noopener noreferrer"
              aria-label="Seguinos en Facebook"
              whileHover={{ scale: 1.15, rotate: 5 }}
              whileTap={{ scale: 0.95 }}
              transition={{ type: "spring", stiffness: 400, damping: 17 }}
              className="block"
            >
              <svg
                width="26"
                height="26"
                viewBox="0 0 24 24"
                fill="currentColor"
                className="text-white"
              >
                <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z" />
              </svg>
            </motion.a>
            <motion.a
              href="https://www.instagram.com/gridohelados/"
              target="_blank"
              rel="noopener noreferrer"
              aria-label="Seguinos en Instagram"
              whileHover={{ scale: 1.15, rotate: -5 }}
              whileTap={{ scale: 0.95 }}
              transition={{ type: "spring", stiffness: 400, damping: 17 }}
              className="block"
            >
              <Image
                src="/images/instagram-icon.png"
                alt="Instagram"
                width={26}
                height={26}
                quality={100}
                className="object-contain invert brightness-0 filter"
              />
            </motion.a>
          </div>
        </div>
      </div>
    </footer>
  );
}
