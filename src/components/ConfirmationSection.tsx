"use client";

import Image from "next/image";
import { motion } from "motion/react";
import Footer from "./Footer";

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
      <section className="w-full">
        {/* Desktop Header */}
        <div className="relative w-full hidden md:block">
          <Image
            src="/images/HEADER-feedback-formulario-desktop.png"
            alt="¡Papá Noel recibió tu solicitud!"
            width={HEADER_DESKTOP_WIDTH}
            height={HEADER_DESKTOP_HEIGHT}
            className="w-full h-auto"
            priority
            quality={100}
            sizes="100vw"
          />
        </div>

        {/* Mobile Header */}
        <div className="relative w-full md:hidden">
          <Image
            src="/images/HEADER-feedback-formulario-mobile.png"
            alt="¡Papá Noel recibió tu solicitud!"
            width={HEADER_MOBILE_WIDTH}
            height={HEADER_MOBILE_HEIGHT}
            className="w-full h-auto"
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
            {nombre}
            <br />
            , recibirás tu saludo por correo electrónico pronto.
          </motion.p>
        </div>
      </section>

      {/* Bottom Section - Footer */}
      <Footer />
    </main>
  );
}

