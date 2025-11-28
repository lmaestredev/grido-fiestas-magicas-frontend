"use client";

import Image from "next/image";
import { useLenis } from "lenis/react";

// Hero image dimensions from Figma: 1280x831
const HERO_WIDTH = 1280;
const HERO_HEIGHT = 831;

export default function HeroSection() {
  const lenis = useLenis();

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
      {/* Container that maintains aspect ratio */}
      <div
        className="relative w-full"
        style={{ aspectRatio: `${HERO_WIDTH}/${HERO_HEIGHT}` }}
      >
        {/* Background Image - fills container with contain, scaled slightly to hide 2px transparent border */}
        <Image
          src="/images/hero-background.png"
          alt="Fiestas Mágicas - Grido"
          fill
          className="object-contain object-center scale-[1.003] -translate-x-[2px] -translate-y-[2px]"
          priority
          quality={100}
          sizes="100vw"
        />

        {/* CTA Button - 68px height on desktop */}
        <button
          type="button"
          onClick={scrollToForm}
          className="absolute left-1/2 -translate-x-1/2 bottom-[16%] flex items-center justify-center gap-3 h-[68px] px-10 border border-white rounded-full text-white font-bold text-2xl hover:bg-white/10 transition-all duration-300 z-10 cursor-pointer"
        >
          Enviá tu saludo
          <Image
            src="/icons/arrow-down.svg"
            alt=""
            width={18}
            height={28}
            className="object-contain"
          />
        </button>
      </div>
    </section>
  );
}
