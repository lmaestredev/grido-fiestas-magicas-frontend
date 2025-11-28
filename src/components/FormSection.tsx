"use client";

import { useActionState, useRef } from "react";
import Image from "next/image";
import { motion, useScroll, useTransform } from "motion/react";
import { sendGreeting, type GreetingFormState } from "~/app/actions/sendGreeting";
import { PROVINCIAS_ARGENTINA, EMAIL_DOMAINS } from "~/lib/constants";

const initialState: GreetingFormState = {
  success: false,
  message: "",
};

// Floating gift component with animation and parallax
interface FloatingGiftProps {
  src: string;
  alt: string;
  width: number;
  height: number;
  className: string;
  floatDuration?: number;
  floatDelay?: number;
  rotateRange?: number;
  parallaxSpeed?: number;
  scrollYProgress: ReturnType<typeof useScroll>["scrollYProgress"];
}

function FloatingGift({
  src,
  alt,
  width,
  height,
  className,
  floatDuration = 4,
  floatDelay = 0,
  rotateRange = 3,
  parallaxSpeed = 0.1,
  scrollYProgress,
}: FloatingGiftProps) {
  // Parallax based on scroll
  const y = useTransform(scrollYProgress, [0, 1], [0, -100 * parallaxSpeed]);

  return (
    <motion.div
      className={className}
      style={{ y }}
      animate={{
        y: [0, -15, 0],
        rotate: [-rotateRange, rotateRange, -rotateRange],
      }}
      transition={{
        y: {
          duration: floatDuration,
          repeat: Infinity,
          ease: "easeInOut",
          delay: floatDelay,
        },
        rotate: {
          duration: floatDuration * 1.2,
          repeat: Infinity,
          ease: "easeInOut",
          delay: floatDelay,
        },
      }}
    >
      <Image
        src={src}
        alt={alt}
        width={width}
        height={height}
        quality={100}
        className="object-contain"
      />
    </motion.div>
  );
}

export default function FormSection() {
  const [state, formAction, isPending] = useActionState(sendGreeting, initialState);
  const sectionRef = useRef<HTMLElement>(null);

  // Scroll progress for parallax
  const { scrollYProgress } = useScroll({
    target: sectionRef,
    offset: ["start end", "end start"],
  });

  return (
    <section
      ref={sectionRef}
      id="formulario"
      className="relative w-full bg-white py-16 overflow-hidden"
    >
      {/* Decorative floating gifts with parallax */}
      {/* Gift box - top left */}
      <FloatingGift
        src="/images/regalo-rojo.png"
        alt="Regalo decorativo"
        width={134}
        height={134}
        className="absolute left-[8%] top-[8%] hidden lg:block"
        floatDuration={4}
        floatDelay={0}
        rotateRange={4}
        parallaxSpeed={0.15}
        scrollYProgress={scrollYProgress}
      />

      {/* Gift box - top right */}
      <FloatingGift
        src="/images/regalo-rojo.png"
        alt="Regalo rojo"
        width={180}
        height={180}
        className="absolute right-[5%] top-[8%] hidden lg:block"
        floatDuration={5}
        floatDelay={0.5}
        rotateRange={3}
        parallaxSpeed={0.1}
        scrollYProgress={scrollYProgress}
      />

      {/* Gift box - bottom right */}
      <FloatingGift
        src="/images/regalo-rojo.png"
        alt="Regalo rojo grande"
        width={320}
        height={360}
        className="absolute right-[3%] bottom-[20%] hidden lg:block"
        floatDuration={4.5}
        floatDelay={1}
        rotateRange={2}
        parallaxSpeed={0.2}
        scrollYProgress={scrollYProgress}
      />

      {/* Green gift box - bottom left */}
      <FloatingGift
        src="/images/regalo-lazo.png"
        alt="Regalo con lazo"
        width={280}
        height={280}
        className="absolute left-[5%] bottom-[25%] hidden lg:block"
        floatDuration={4.2}
        floatDelay={1.5}
        rotateRange={5}
        parallaxSpeed={0.18}
        scrollYProgress={scrollYProgress}
      />

      {/* Form Content */}
      <div className="relative z-10 max-w-[662px] mx-auto px-4">
        <h2 className="text-grido-primary-dark font-bold text-3xl md:text-4xl text-center mb-4">
          ¡Creemos un saludo mágico!
        </h2>
        <p className="text-center text-black mb-10">
          Llená el siguiente formulario para crear un Saludo Mágico de la mano
          <br className="hidden sm:block" />
          de Papá Noel y Grido!
        </p>

        {/* Success Message */}
        {state.success && (
          <div className="mb-6 p-4 bg-green-100 border border-green-400 text-green-700 rounded-lg text-center">
            {state.message}
          </div>
        )}

        {/* Error Message */}
        {!state.success && state.message && (
          <div className="mb-6 p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg text-center">
            {state.message}
          </div>
        )}

        <form action={formAction} className="space-y-6">
          {/* Tu información */}
          <div className="space-y-4">
            <h3 className="text-grido-primary-dark font-bold text-xl md:text-2xl text-center">
              Tu información
            </h3>

            <div>
              <input
                type="text"
                name="nombre"
                placeholder="Tu nombre"
                className="w-full h-[47px] px-4 border border-grido-primary-dark rounded-[10px] text-lg placeholder:text-grido-placeholder focus:ring-2 focus:ring-grido-primary/20"
              />
              {state.errors?.nombre && (
                <p className="text-red-500 text-sm mt-1">{state.errors.nombre}</p>
              )}
            </div>

            <div>
              <input
                type="text"
                name="parentesco"
                placeholder="Tu parentesco"
                className="w-full h-[47px] px-4 border border-grido-primary-dark rounded-[10px] text-lg placeholder:text-grido-placeholder"
              />
              {state.errors?.parentesco && (
                <p className="text-red-500 text-sm mt-1">{state.errors.parentesco}</p>
              )}
            </div>

            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1">
                <input
                  type="text"
                  name="email"
                  placeholder="Tu email"
                  className="w-full h-[47px] px-4 border border-grido-primary-dark rounded-[10px] text-lg placeholder:text-grido-placeholder"
                />
                {state.errors?.email && (
                  <p className="text-red-500 text-sm mt-1">{state.errors.email}</p>
                )}
              </div>
              <div className="sm:w-[180px]">
                <div className="relative">
                  <select
                    name="emailDomain"
                    defaultValue="@gmail.com"
                    className="w-full h-[47px] px-4 pr-10 border border-grido-primary-dark rounded-[10px] text-lg text-grido-placeholder appearance-none bg-white cursor-pointer"
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
                    className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none"
                  />
                </div>
                {state.errors?.emailDomain && (
                  <p className="text-red-500 text-sm mt-1">{state.errors.emailDomain}</p>
                )}
              </div>
            </div>
          </div>

          {/* Información del destinatario */}
          <div className="space-y-4 pt-4">
            <h3 className="text-grido-primary-dark font-bold text-xl md:text-2xl text-center">
              Información del destinatario
            </h3>

            <div className="relative">
              <select
                name="provincia"
                defaultValue=""
                className="w-full h-[47px] px-4 pr-10 border border-grido-primary-dark rounded-[10px] text-lg text-grido-placeholder appearance-none bg-white cursor-pointer"
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
                <p className="text-red-500 text-sm mt-1">{state.errors.provincia}</p>
              )}
            </div>

            <div>
              <textarea
                name="queHizo"
                placeholder="Contame que hizo en el año!"
                rows={3}
                className="w-full px-4 py-4 border border-grido-primary-dark rounded-[10px] text-lg placeholder:text-grido-placeholder resize-none"
              />
              {state.errors?.queHizo && (
                <p className="text-red-500 text-sm mt-1">{state.errors.queHizo}</p>
              )}
            </div>

            <div>
              <textarea
                name="recuerdoEspecial"
                placeholder="¿Un recuerdo especial para mencionarle?"
                rows={3}
                className="w-full px-4 py-4 border border-grido-primary-dark rounded-[10px] text-lg placeholder:text-grido-placeholder resize-none"
              />
              {state.errors?.recuerdoEspecial && (
                <p className="text-red-500 text-sm mt-1">{state.errors.recuerdoEspecial}</p>
              )}
            </div>

            <div>
              <textarea
                name="pedidoNocheMagica"
                placeholder="¿Cuál es su pedido de Noche Mágica?"
                rows={3}
                className="w-full px-4 py-4 border border-grido-primary-dark rounded-[10px] text-lg placeholder:text-grido-placeholder resize-none"
              />
              {state.errors?.pedidoNocheMagica && (
                <p className="text-red-500 text-sm mt-1">{state.errors.pedidoNocheMagica}</p>
              )}
            </div>
          </div>

          {/* Submit Button */}
          <div className="flex justify-center pt-4">
            <button
              type="submit"
              disabled={isPending}
              className="bg-grido-primary hover:bg-grido-primary-dark text-white font-medium text-lg px-9 py-3 rounded-full transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isPending ? "Enviando..." : "Enviá tu saludo"}
            </button>
          </div>
        </form>
      </div>
    </section>
  );
}
