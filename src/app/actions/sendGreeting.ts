"use server";

import { redirect } from "next/navigation";
import { Redis } from "@upstash/redis";
import { nanoid } from "nanoid";
import { PROVINCIAS_ARGENTINA, EMAIL_DOMAINS } from "~/lib/constants";
import { validateFormContent } from "~/lib/contentModeration";

const redis = new Redis({
  url: process.env.UPSTASH_REDIS_REST_URL!,
  token: process.env.UPSTASH_REDIS_REST_TOKEN!,
});

export interface GreetingFormData {
  nombre: string;
  parentesco: string;
  email: string;
  emailDomain: string;
  provincia: string;
  nombreNino: string;
  queHizo: string;
}

export interface GreetingFormState {
  success: boolean;
  message: string;
  errors?: Partial<Record<keyof GreetingFormData, string>>;
  videoId?: string;
  formData?: GreetingFormData;
}

export async function sendGreeting(
  prevState: GreetingFormState | null,
  formData: FormData
): Promise<GreetingFormState> {
  const data: GreetingFormData = {
    nombre: formData.get("nombre") as string,
    parentesco: formData.get("parentesco") as string,
    email: formData.get("email") as string,
    emailDomain: formData.get("emailDomain") as string,
    provincia: formData.get("provincia") as string,
    nombreNino: formData.get("nombreNino") as string,
    queHizo: formData.get("queHizo") as string
  };

  const errors: Partial<Record<keyof GreetingFormData, string>> = {};

  if (!data.nombre || data.nombre.trim().length < 2) {
    errors.nombre = "El nombre es requerido (mínimo 2 caracteres)";
  } else if (!/^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+$/.test(data.nombre)) {
    errors.nombre = "El nombre solo puede contener letras y espacios";
  }

  if (!data.parentesco || data.parentesco.trim().length < 2) {
    errors.parentesco = "El parentesco es requerido";
  } else if (!/^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+$/.test(data.parentesco)) {
    errors.parentesco = "El parentesco solo puede contener letras y espacios";
  }

  if (!data.email || !/^[^\s@]+$/.test(data.email)) {
    errors.email = "Ingresá un email válido";
  }

  if (!data.emailDomain || !EMAIL_DOMAINS.includes(data.emailDomain as typeof EMAIL_DOMAINS[number])) {
    errors.emailDomain = "Seleccioná un dominio de email";
  }

  if (!data.provincia || !PROVINCIAS_ARGENTINA.includes(data.provincia as typeof PROVINCIAS_ARGENTINA[number])) {
    errors.provincia = "Seleccioná una provincia válida";
  }

  if (!data.nombreNino || data.nombreNino.trim().length < 2) {
    errors.nombreNino = "El nombre del niño es requerido (mínimo 2 caracteres)";
  } else if (!/^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+$/.test(data.nombreNino)) {
    errors.nombreNino = "El nombre del niño solo puede contener letras y espacios";
  }

  if (!data.queHizo || data.queHizo.trim().length < 10) {
    errors.queHizo = "Contanos qué hizo en el año (mínimo 10 caracteres)";
  } else if (data.queHizo.trim().length > 80) {
    errors.queHizo = "El texto es muy largo (máximo 80 caracteres)";
  }

  if (Object.keys(errors).length > 0) {
    return {
      success: false,
      message: "Por favor, corregí los errores en el formulario",
      errors,
      formData: data,
    };
  }

  const contentValidation = await validateFormContent({
    queHizo: data.queHizo,
    nombre: data.nombre,
    parentesco: data.parentesco,
    nombreNino: data.nombreNino,
  });

  if (!contentValidation.isValid) {
    return {
      success: false,
      message: "Por favor, corregí los errores en el formulario",
      errors: contentValidation.errors as Partial<Record<keyof GreetingFormData, string>>,
      formData: data,
    };
  }

  try {
    // Generar ID único para el video
    const videoId = nanoid(12);

    // Crear el job para Redis
    const job = {
      videoId,
      status: "pending",
      data: {
        nombre: data.nombre,
        parentesco: data.parentesco,
        email: `${data.email}${data.emailDomain}`,
        provincia: data.provincia,
        nombreNino: data.nombreNino,
        queHizo: data.queHizo
      },
      createdAt: new Date().toISOString(),
    };

    // Escribir directamente en Redis
    await redis.set(`job:${videoId}`, JSON.stringify(job));
    // RPUSH agrega al final de la cola (FIFO: mantiene orden de llegada)
    await redis.rpush("video:queue", videoId);

    // Opcional: Notificar al worker si hay webhook configurado
    if (process.env.WORKER_WEBHOOK_URL) {
      fetch(process.env.WORKER_WEBHOOK_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ videoId }),
      }).catch(console.error);
    }
  } catch (error) {
    // Si es un redirect de Next.js, re-lanzarlo
    if (error && typeof error === "object" && "digest" in error && typeof error.digest === "string" && error.digest.startsWith("NEXT_REDIRECT")) {
      throw error;
    }
    console.error("Error writing to Redis:", error);
    return {
      success: false,
      message: "Hubo un error al procesar tu solicitud. Por favor intentá de nuevo.",
      formData: data,
    };
  }

  // Redirigir a la página de confirmación con los parámetros (fuera del try-catch)
  const params = new URLSearchParams({
    parentesco: data.parentesco,
    nombre: data.nombreNino,
  });
  redirect(`/confirmacion?${params.toString()}`);
}
