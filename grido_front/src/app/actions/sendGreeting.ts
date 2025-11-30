"use server";

import { PROVINCIAS_ARGENTINA, EMAIL_DOMAINS } from "~/lib/constants";
import { validateFormContent } from "~/lib/contentModeration";

export interface GreetingFormData {
  nombre: string;
  parentesco: string;
  email: string;
  emailDomain: string;
  provincia: string;
  queHizo: string;
  recuerdoEspecial: string;
  pedidoNocheMagica: string;
}

export interface GreetingFormState {
  success: boolean;
  message: string;
  errors?: Partial<Record<keyof GreetingFormData, string>>;
  videoId?: string;
}

export async function sendGreeting(
  prevState: GreetingFormState | null,
  formData: FormData
): Promise<GreetingFormState> {
  // Extract form data
  const data: GreetingFormData = {
    nombre: formData.get("nombre") as string,
    parentesco: formData.get("parentesco") as string,
    email: formData.get("email") as string,
    emailDomain: formData.get("emailDomain") as string,
    provincia: formData.get("provincia") as string,
    queHizo: formData.get("queHizo") as string,
    recuerdoEspecial: formData.get("recuerdoEspecial") as string,
    pedidoNocheMagica: formData.get("pedidoNocheMagica") as string,
  };

  // Validation
  const errors: Partial<Record<keyof GreetingFormData, string>> = {};

  if (!data.nombre || data.nombre.trim().length < 2) {
    errors.nombre = "El nombre es requerido (mínimo 2 caracteres)";
  }

  if (!data.parentesco || data.parentesco.trim().length < 2) {
    errors.parentesco = "El parentesco es requerido";
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

  if (!data.queHizo || data.queHizo.trim().length < 10) {
    errors.queHizo = "Contanos qué hizo en el año (mínimo 10 caracteres)";
  }

  if (!data.recuerdoEspecial || data.recuerdoEspecial.trim().length < 5) {
    errors.recuerdoEspecial = "Compartí un recuerdo especial";
  }

  if (!data.pedidoNocheMagica || data.pedidoNocheMagica.trim().length < 5) {
    errors.pedidoNocheMagica = "Contanos su pedido para la Noche Mágica";
  }

  if (Object.keys(errors).length > 0) {
    return {
      success: false,
      message: "Por favor, corregí los errores en el formulario",
      errors,
    };
  }

  // Validación de contenido inapropiado
  const contentValidation = await validateFormContent({
    queHizo: data.queHizo,
    recuerdoEspecial: data.recuerdoEspecial,
    pedidoNocheMagica: data.pedidoNocheMagica,
  });

  if (!contentValidation.isValid) {
    return {
      success: false,
      message: "Por favor, corregí los errores en el formulario",
      errors: contentValidation.errors as Partial<Record<keyof GreetingFormData, string>>,
    };
  }

  try {
    // Call the video generation API
    const apiUrl = process.env.VIDEO_API_URL || "/api/generate-video";
    
    const response = await fetch(apiUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${process.env.VIDEO_API_SECRET || ""}`,
      },
      body: JSON.stringify({
        nombre: data.nombre,
        parentesco: data.parentesco,
        email: `${data.email}${data.emailDomain}`,
        provincia: data.provincia,
        queHizo: data.queHizo,
        recuerdoEspecial: data.recuerdoEspecial,
        pedidoNocheMagica: data.pedidoNocheMagica,
      }),
    });

    if (!response.ok) {
      throw new Error("Error al procesar el video");
    }

    const result = await response.json();

    return {
      success: true,
      message: "¡Tu saludo mágico se está generando! Te llegará por email en unos minutos. 🎄✨",
      videoId: result.videoId,
    };
  } catch (error) {
    console.error("Error calling video API:", error);
    return {
      success: false,
      message: "Hubo un error al procesar tu solicitud. Por favor intentá de nuevo.",
    };
  }
}
