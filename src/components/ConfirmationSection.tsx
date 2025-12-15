"use client";

import Image from "next/image";
import { motion } from "motion/react";

interface ConfirmationSectionProps {
  parentesco?: string;
  nombre?: string;
}

const HEADER_DESKTOP_WIDTH = 1280;
const HEADER_DESKTOP_HEIGHT = 831;
const HEADER_MOBILE_WIDTH = 321;
const HEADER_MOBILE_HEIGHT = 385;

export default function ConfirmationSection({
  parentesco = "[parentesco]",
  nombre = "[nombre]",
}: ConfirmationSectionProps) {
  return (
    <main className="min-h-screen bg-white">
      {/* Top Section - Header Image */}
      <section className="relative w-full overflow-hidden">
        {/* Desktop Header */}
        <div 
          className="relative w-full hidden md:block"
          style={{ 
            aspectRatio: `${HEADER_DESKTOP_WIDTH}/${HEADER_DESKTOP_HEIGHT}`
          }}
        >
          <Image
            src="/images/HEADER-feedback-formulario-desktop.png"
            alt="¡Papá Noel recibió tu solicitud!"
            fill
            className="object-contain object-center"
            priority
            quality={100}
            sizes="100vw"
          />
        </div>

        {/* Mobile Header */}
        <div 
          className="relative w-full md:hidden"
          style={{ 
            aspectRatio: `${HEADER_MOBILE_WIDTH}/${HEADER_MOBILE_HEIGHT}`
          }}
        >
          <Image
            src="/images/HEADER-feedback-formulario-mobile.png"
            alt="¡Papá Noel recibió tu solicitud!"
            fill
            className="object-contain object-center"
            priority
            quality={100}
            sizes="100vw"
          />
        </div>
      </section>

      {/* Middle Section - White with Confirmation Message */}
      <section className="relative w-full bg-white py-12 md:py-16">
        <div className="max-w-4xl mx-auto px-4 md:px-8 text-center">
          <motion.h2
            className="text-grido-primary-dark font-bold text-3xl md:text-4xl lg:text-5xl mb-6 md:mb-8"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            ¡Tu saludo mágico fue enviado!
          </motion.h2>
          <motion.p
            className="text-grido-primary-dark text-xl md:text-2xl lg:text-3xl font-medium"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            Tu {parentesco} {nombre}
            <br />
            estará recibiendo tu saludo pronto.
          </motion.p>
        </div>
      </section>

      {/* Bottom Section - Dark Blue Footer */}
      <footer className="bg-grido-primary-dark w-full">
        <div className="max-w-7xl mx-auto px-6 lg:px-[141px] py-[55px]">
          <div className="flex flex-col md:flex-row items-center justify-between gap-8">
            {/* Grido Logo */}
            <div className="shrink-0">
              <Image
                src="/images/grido-logo.png"
                alt="Grido"
                width={100}
                height={71}
                quality={100}
                className="object-contain brightness-0 invert"
              />
            </div>

            {/* Copyright Text */}
            <p className="text-white text-center md:text-left max-w-[500px] text-sm md:text-base">
              Copyright 2016. Todos los derechos reservados - Helacor - Córdoba
              - Argentina
            </p>

            {/* Instagram Icon */}
            <div className="shrink-0">
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
                  className="object-contain brightness-0 invert"
                />
              </motion.a>
            </div>
          </div>
        </div>
      </footer>
    </main>
  );
}

