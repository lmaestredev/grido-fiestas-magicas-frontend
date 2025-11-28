"use client";

import { useActionState, useRef } from "react";
import Image from "next/image";
import { motion, useScroll, useTransform, useSpring } from "motion/react";
import {
  sendGreeting,
  type GreetingFormState,
} from "~/app/actions/sendGreeting";
import { PROVINCIAS_ARGENTINA, EMAIL_DOMAINS } from "~/lib/constants";

const initialState: GreetingFormState = {
  success: false,
  message: "",
};

// Floating gift component with animation and parallax
interface FloatingGiftProps {
  src: string;
  alt: string;
  size: string;
  className: string;
  floatDuration?: number;
  floatDelay?: number;
  floatAmount?: number;
  rotateRange?: number;
  parallaxRange?: [number, number];
  scrollYProgress: ReturnType<typeof useScroll>["scrollYProgress"];
}

function FloatingGift({
  src,
  alt,
  size,
  className,
  floatDuration = 4,
  floatDelay = 0,
  floatAmount = 15,
  rotateRange = 3,
  parallaxRange = [30, -30],
  scrollYProgress,
}: FloatingGiftProps) {
  const rawY = useTransform(scrollYProgress, [0, 1], parallaxRange);
  const y = useSpring(rawY, { stiffness: 100, damping: 30 });

  return (
    <motion.div
      className={className}
      style={{ y, width: size, height: size }}
      animate={{
        translateY: [0, -floatAmount, 0],
        rotate: [-rotateRange, rotateRange, -rotateRange],
      }}
      transition={{
        translateY: {
          duration: floatDuration,
          repeat: Infinity,
          ease: "easeInOut",
          delay: floatDelay,
        },
        rotate: {
          duration: floatDuration * 1.3,
          repeat: Infinity,
          ease: "easeInOut",
          delay: floatDelay + 0.2,
        },
      }}
    >
      <Image
        src={src}
        alt={alt}
        fill
        quality={100}
        className="object-contain"
      />
    </motion.div>
  );
}

// Simple floating gift for mobile (no parallax)
interface MobileGiftProps {
  src: string;
  alt: string;
  className: string;
  floatDuration?: number;
  floatDelay?: number;
  floatAmount?: number;
  rotateRange?: number;
  initialRotate?: number;
}

function MobileGift({
  src,
  alt,
  className,
  floatDuration = 4,
  floatDelay = 0,
  floatAmount = 8,
  rotateRange = 3,
  initialRotate = 0,
}: MobileGiftProps) {
  return (
    <motion.div
      className={className}
      initial={{ rotate: initialRotate }}
      animate={{
        translateY: [0, -floatAmount, 0],
        rotate: [
          initialRotate - rotateRange,
          initialRotate + rotateRange,
          initialRotate - rotateRange,
        ],
      }}
      transition={{
        translateY: {
          duration: floatDuration,
          repeat: Infinity,
          ease: "easeInOut",
          delay: floatDelay,
        },
        rotate: {
          duration: floatDuration * 1.3,
          repeat: Infinity,
          ease: "easeInOut",
          delay: floatDelay + 0.2,
        },
      }}
    >
      <Image
        src={src}
        alt={alt}
        fill
        quality={100}
        className="object-contain"
      />
    </motion.div>
  );
}

export default function FormSection() {
  const [state, formAction, isPending] = useActionState(
    sendGreeting,
    initialState,
  );
  const sectionRef = useRef<HTMLElement>(null);

  const { scrollYProgress } = useScroll({
    target: sectionRef,
    offset: ["start end", "end start"],
  });

  return (
    <section
      ref={sectionRef}
      id="formulario"
      className="relative w-full bg-white py-8 md:py-16 overflow-x-hidden"
    >
      {/* Mobile Gifts - positioned at top */}
      <div className="relative h-[120px] w-full mb-4 lg:hidden">
        {/* Large red gift - right side */}
        <MobileGift
          src="/images/regalo-rojo.png"
          alt="Regalo rojo"
          className="absolute right-[-20%] top-[-20%] w-[50vw] h-[50vw]"
          floatDuration={4.5}
          floatDelay={0}
          floatAmount={5}
          rotateRange={2}
        />
        {/* Small red gift - left top */}
        <MobileGift
          src="/images/regalo-rojo.png"
          alt="Regalo rojo pequeño"
          className="absolute left-[18%] top-[0%] w-[20vw] h-[20vw]"
          floatDuration={4}
          floatDelay={0.3}
          floatAmount={6}
          rotateRange={3}
        />
        {/* Orange gift - center */}
        <MobileGift
          src="/images/regalo-naranja.png"
          alt="Regalo naranja"
          className="absolute left-[30%] top-[60%] w-[40vw] h-[40vw]"
          floatDuration={5}
          floatDelay={0.5}
          floatAmount={5}
          rotateRange={2}
        />
        {/* Green gift - left bottom with rotation */}
        <MobileGift
          src="/images/regalo-lazo.png"
          alt="Regalo verde"
          className="absolute left-[-8%] top-[50%] w-[35vw] h-[35vw]"
          floatDuration={4.2}
          floatDelay={0.8}
          floatAmount={5}
          rotateRange={3}
          initialRotate={15}
        />
      </div>

      {/* Desktop floating gifts with parallax */}
      <FloatingGift
        src="/images/regalo-rojo.png"
        alt="Regalo decorativo"
        size="12vw"
        className="absolute left-[5%] top-[25%] hidden lg:block"
        floatDuration={4}
        floatDelay={0}
        floatAmount={12}
        rotateRange={5}
        parallaxRange={[60, -40]}
        scrollYProgress={scrollYProgress}
      />

      <FloatingGift
        src="/images/regalo-naranja.png"
        alt="Regalo naranja"
        size="15vw"
        className="absolute right-[4%] top-[25%] hidden lg:block"
        floatDuration={5}
        floatDelay={0.5}
        floatAmount={10}
        rotateRange={4}
        parallaxRange={[40, -50]}
        scrollYProgress={scrollYProgress}
      />

      <FloatingGift
        src="/images/regalo-rojo.png"
        alt="Regalo rojo grande"
        size="35vw"
        className="absolute right-[-12%] top-[40%] hidden lg:block"
        floatDuration={4.5}
        floatDelay={1}
        floatAmount={8}
        rotateRange={3}
        parallaxRange={[80, -60]}
        scrollYProgress={scrollYProgress}
      />

      <FloatingGift
        src="/images/regalo-lazo.png"
        alt="Regalo con lazo"
        size="30vw"
        className="absolute left-[-8%] top-[45%] hidden lg:block"
        floatDuration={4.2}
        floatDelay={1.5}
        floatAmount={10}
        rotateRange={6}
        parallaxRange={[70, -50]}
        scrollYProgress={scrollYProgress}
      />

      {/* Form Content */}
      <div className="relative z-10 max-w-[662px] mx-auto pt-[30vmin] px-3 md:px-4">
        <h2 className="text-grido-primary-dark font-bold text-[24px] md:text-4xl text-center mb-2 md:mb-4">
          ¡Creemos
          <br className="md:hidden" />
          <span className="md:hidden"> </span>
          un saludo mágico!
        </h2>
        <p className="text-center text-black text-[14px] md:text-base mb-6 md:mb-10">
          Llená el siguiente formulario para
          <br className="md:hidden" />
          <span className="hidden md:inline"> </span>
          crear un Saludo Mágico de la mano
          <br />
          de Papá Noel y Grido!
        </p>

        {/* Success Message */}
        {state.success && (
          <div className="mb-6 p-4 bg-green-100 border border-green-400 text-green-700 rounded-lg text-center text-sm md:text-base">
            {state.message}
          </div>
        )}

        {/* Error Message */}
        {!state.success && state.message && (
          <div className="mb-6 p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg text-center text-sm md:text-base">
            {state.message}
          </div>
        )}

        <form action={formAction} className="space-y-4 md:space-y-6">
          {/* Tu información */}
          <div className="space-y-3 md:space-y-4">
            <h3 className="text-grido-primary-dark font-bold text-[20px] md:text-2xl text-center">
              Tu información
            </h3>

            <div>
              <input
                type="text"
                name="nombre"
                placeholder="Tu nombre"
                className="w-full h-[47px] px-4 border border-grido-primary-dark rounded-[10px] text-[16px] md:text-lg placeholder:text-grido-placeholder focus:ring-2 focus:ring-grido-primary/20"
              />
              {state.errors?.nombre && (
                <p className="text-red-500 text-sm mt-1">
                  {state.errors.nombre}
                </p>
              )}
            </div>

            <div>
              <input
                type="text"
                name="parentesco"
                placeholder="Tu parentesco"
                className="w-full h-[47px] px-4 border border-grido-primary-dark rounded-[10px] text-[16px] md:text-lg placeholder:text-grido-placeholder"
              />
              {state.errors?.parentesco && (
                <p className="text-red-500 text-sm mt-1">
                  {state.errors.parentesco}
                </p>
              )}
            </div>

            <div className="flex flex-row gap-2 md:gap-4">
              <div className="flex-1">
                <input
                  type="text"
                  name="email"
                  placeholder="Tu email"
                  className="w-full h-[47px] px-4 border border-grido-primary-dark rounded-[10px] text-[16px] md:text-lg placeholder:text-grido-placeholder"
                />
                {state.errors?.email && (
                  <p className="text-red-500 text-sm mt-1">
                    {state.errors.email}
                  </p>
                )}
              </div>
              <div className="w-[130px] md:w-[180px]">
                <div className="relative">
                  <select
                    name="emailDomain"
                    defaultValue="@gmail.com"
                    className="w-full h-[47px] px-2 md:px-4 pr-8 md:pr-10 border border-grido-primary-dark rounded-[10px] text-[13px] md:text-lg text-grido-placeholder appearance-none bg-white cursor-pointer"
                  >
                    {EMAIL_DOMAINS.map((domain) => (
                      <option key={domain} value={domain}>
                        {domain}
                      </option>
                    ))}
                  </select>
                  <Image
                    src="/images/chevron-down.svg"
                    alt=""
                    width={16}
                    height={8}
                    quality={100}
                    className="absolute right-3 md:right-4 top-1/2 -translate-y-1/2 pointer-events-none"
                  />
                </div>
                {state.errors?.emailDomain && (
                  <p className="text-red-500 text-sm mt-1">
                    {state.errors.emailDomain}
                  </p>
                )}
              </div>
            </div>
          </div>

          {/* Información del destinatario */}
          <div className="space-y-3 md:space-y-4 pt-2 md:pt-4">
            <h3 className="text-grido-primary-dark font-bold text-[20px] md:text-2xl text-center">
              Información del destinatario
            </h3>

            <div className="relative">
              <select
                name="provincia"
                defaultValue=""
                className="w-full h-[47px] px-4 pr-10 border border-grido-primary-dark rounded-[10px] text-[16px] md:text-lg text-grido-placeholder appearance-none bg-white cursor-pointer"
              >
                <option value="" disabled>
                  Su provincia
                </option>
                {PROVINCIAS_ARGENTINA.map((provincia) => (
                  <option key={provincia} value={provincia}>
                    {provincia}
                  </option>
                ))}
              </select>
              <Image
                src="/images/chevron-down.svg"
                alt=""
                width={16}
                height={8}
                quality={100}
                className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none"
              />
              {state.errors?.provincia && (
                <p className="text-red-500 text-sm mt-1">
                  {state.errors.provincia}
                </p>
              )}
            </div>

            <div>
              <textarea
                name="queHizo"
                placeholder="Contame que hizo en el año!"
                rows={3}
                className="w-full px-4 py-4 border border-grido-primary-dark rounded-[10px] text-[16px] md:text-lg placeholder:text-grido-placeholder resize-none"
              />
              {state.errors?.queHizo && (
                <p className="text-red-500 text-sm mt-1">
                  {state.errors.queHizo}
                </p>
              )}
            </div>

            <div>
              <textarea
                name="recuerdoEspecial"
                placeholder="¿Un recuerdo especial para mencionarle?"
                rows={3}
                className="w-full px-4 py-4 border border-grido-primary-dark rounded-[10px] text-[16px] md:text-lg placeholder:text-grido-placeholder resize-none"
              />
              {state.errors?.recuerdoEspecial && (
                <p className="text-red-500 text-sm mt-1">
                  {state.errors.recuerdoEspecial}
                </p>
              )}
            </div>

            <div>
              <textarea
                name="pedidoNocheMagica"
                placeholder="¿Cuál es su pedido de Noche Mágica?"
                rows={3}
                className="w-full px-4 py-4 border border-grido-primary-dark rounded-[10px] text-[16px] md:text-lg placeholder:text-grido-placeholder resize-none"
              />
              {state.errors?.pedidoNocheMagica && (
                <p className="text-red-500 text-sm mt-1">
                  {state.errors.pedidoNocheMagica}
                </p>
              )}
            </div>
          </div>

          {/* Submit Button - smaller on mobile */}
          <div className="flex justify-center pt-2 md:pt-4">
            <button
              type="submit"
              disabled={isPending}
              className="bg-grido-primary hover:bg-grido-primary-dark text-white font-medium text-[16px] md:text-lg h-[42px] md:h-auto px-9 md:px-9 md:py-3 rounded-full transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isPending ? "Enviando..." : "Enviá tu saludo"}
            </button>
          </div>
        </form>
      </div>
    </section>
  );
}
