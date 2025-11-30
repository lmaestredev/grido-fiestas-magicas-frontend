"use client";

import Image from "next/image";
import { useLenis } from "lenis/react";
import { motion, useScroll, useTransform, useSpring } from "motion/react";
import { useRef } from "react";

// Hero image dimensions from Figma
const HERO_DESKTOP_WIDTH = 1280;
const HERO_DESKTOP_HEIGHT = 831;
const HERO_MOBILE_WIDTH = 321;
const HERO_MOBILE_HEIGHT = 385;

export default function HeroSection() {
  const lenis = useLenis();
  const desktopHeroRef = useRef<HTMLDivElement>(null);

  const { scrollYProgress } = useScroll({
    target: desktopHeroRef,
    offset: ["start end", "end start"],
  });

  // Parallax solo para los elementos - se mueven hacia arriba al hacer scroll (movimiento muy notorio)
  const elementsY = useTransform(scrollYProgress, [0, 1], [180, -250]);
  const elementsYSpring = useSpring(elementsY, { stiffness: 120, damping: 25 });

  const scrollToForm = () => {
    const formElement = document.getElementById("formulario");
    if (formElement && lenis) {
      lenis.scrollTo(formElement, {
        offset: 0,
        duration: 1.5,
      });
    }
  };

  return (
    <section className="relative w-full overflow-hidden">
      {/* Desktop Hero */}
      <div
        ref={desktopHeroRef}
        className="relative w-full hidden md:block"
        style={{ aspectRatio: `${HERO_DESKTOP_WIDTH}/${HERO_DESKTOP_HEIGHT}` }}
      >
        {/* Background Image - bg_desktop.png estático */}
        <div className="absolute inset-0">
          <Image
            src="/images/hero/bg_desktop.png"
            alt="Fiestas Mágicas - Grido Background"
            fill
            className="object-contain object-center scale-[1.003] -translate-x-[2px] -translate-y-[2px]"
            priority
            quality={100}
            sizes="100vw"
          />
        </div>

        {/* Elements Image - NoBg.png con parallax más pronunciado */}
        <motion.div
          style={{ y: elementsYSpring }}
          className="absolute inset-0 z-2"
        >
          <Image
            src="/images/hero/NoBg.png"
            alt="Fiestas Mágicas - Grido Elements"
            fill
            className="object-contain object-center scale-[1.003] -translate-x-[2px] -translate-y-[2px]"
            priority
            quality={100}
            sizes="100vw"
          />
        </motion.div>

        {/* CTA Button Desktop - 68px height */}
        <button
          type="button"
          onClick={scrollToForm}
          className="absolute left-1/2 -translate-x-1/2 bottom-[10%] flex items-center justify-center gap-3 h-[68px] px-10 border border-white rounded-full text-white font-bold text-2xl hover:bg-white/10 transition-all duration-300 z-10 cursor-pointer"
        >
          Enviá tu saludo
          <motion.div
            animate={{
              y: [0, 8, 0],
            }}
            transition={{
              duration: 1.5,
              repeat: Infinity,
              ease: "easeInOut",
            }}
          >
            <Image
              src="/icons/arrow-down.svg"
              alt=""
              width={18}
              height={28}
              className="object-contain"
            />
          </motion.div>
        </button>
      </div>

      {/* Mobile Hero */}
      <div
        className="relative w-full md:hidden"
        style={{ aspectRatio: `${HERO_MOBILE_WIDTH}/${HERO_MOBILE_HEIGHT}` }}
      >
        <Image
          src="/images/hero-background-mobile.png"
          alt="Fiestas Mágicas - Grido"
          fill
          className="object-contain object-center"
          priority
          quality={100}
          sizes="100vw"
        />

        {/* CTA Button Mobile - smaller */}
        <button
          type="button"
          onClick={scrollToForm}
          className="absolute left-1/2 -translate-x-1/2 bottom-[8%] flex items-center justify-center gap-2 h-[42px] px-6 border border-white rounded-full text-white font-medium text-base hover:bg-white/10 transition-all duration-300 z-10 cursor-pointer min-w-max"
        >
          Enviá tu saludo
          <motion.div
            animate={{
              y: [0, 6, 0],
            }}
            transition={{
              duration: 1.5,
              repeat: Infinity,
              ease: "easeInOut",
            }}
          >
            <Image
              src="/icons/arrow-down.svg"
              alt=""
              width={10}
              height={12}
              className="object-contain"
            />
          </motion.div>
        </button>
      </div>
    </section>
  );
}
