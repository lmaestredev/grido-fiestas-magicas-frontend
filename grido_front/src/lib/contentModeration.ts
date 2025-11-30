import { containsProhibitedWords } from "./prohibitedWords";

const PERSPECTIVE_API_KEY = process.env.PERSPECTIVE_API_KEY || "";
const PERSPECTIVE_API_URL = "https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze";

interface PerspectiveResponse {
  attributeScores?: {
    TOXICITY?: { summaryScore?: { value?: number } };
    SEVERE_TOXICITY?: { summaryScore?: { value?: number } };
    IDENTITY_ATTACK?: { summaryScore?: { value?: number } };
    INSULT?: { summaryScore?: { value?: number } };
    PROFANITY?: { summaryScore?: { value?: number } };
    THREAT?: { summaryScore?: { value?: number } };
  };
}

export interface ContentModerationResult {
  isValid: boolean;
  reason?: string;
  scores?: {
    toxicity?: number;
    severeToxicity?: number;
    insult?: number;
    profanity?: number;
  };
}

/**
 * Valida contenido usando lista de palabras prohibidas y Perspective API
 */
export async function validateContent(
  text: string,
  fieldName: string
): Promise<ContentModerationResult> {
  // Primera validación: lista de palabras prohibidas (rápida y local)
  if (containsProhibitedWords(text)) {
    return {
      isValid: false,
      reason: `El contenido contiene palabras o frases inapropiadas. Por favor, usá un lenguaje respetuoso.`,
    };
  }

  // Segunda validación: Perspective API (para casos más complejos)
  if (!PERSPECTIVE_API_KEY) {
    console.warn("PERSPECTIVE_API_KEY no configurada, solo validando con lista de palabras");
    // Si no hay API key, confiamos en la lista de palabras
    return { isValid: true };
  }

  try {
    const response = await fetch(
      `${PERSPECTIVE_API_URL}?key=${PERSPECTIVE_API_KEY}`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          comment: {
            text: text,
          },
          requestedAttributes: {
            TOXICITY: {},
            SEVERE_TOXICITY: {},
            IDENTITY_ATTACK: {},
            INSULT: {},
            PROFANITY: {},
            THREAT: {},
          },
          languages: ["es"],
        }),
      }
    );

    if (!response.ok) {
      console.error("Error en Perspective API:", await response.text());
      // Si falla la API, permitimos el contenido (fail-open)
      return { isValid: true };
    }

    const data: PerspectiveResponse = await response.json();
    const scores = data.attributeScores || {};

    const toxicity = scores.TOXICITY?.summaryScore?.value || 0;
    const severeToxicity = scores.SEVERE_TOXICITY?.summaryScore?.value || 0;
    const insult = scores.INSULT?.summaryScore?.value || 0;
    const profanity = scores.PROFANITY?.summaryScore?.value || 0;

    // Umbrales de tolerancia (ajustables)
    const TOXICITY_THRESHOLD = 0.7;
    const SEVERE_TOXICITY_THRESHOLD = 0.5;
    const INSULT_THRESHOLD = 0.7;
    const PROFANITY_THRESHOLD = 0.7;

    const isToxic = toxicity > TOXICITY_THRESHOLD;
    const isSeverelyToxic = severeToxicity > SEVERE_TOXICITY_THRESHOLD;
    const isInsulting = insult > INSULT_THRESHOLD;
    const isProfane = profanity > PROFANITY_THRESHOLD;

    if (isToxic || isSeverelyToxic || isInsulting || isProfane) {
      return {
        isValid: false,
        reason: `El contenido no es apropiado. Por favor, usá un lenguaje respetuoso y positivo.`,
        scores: {
          toxicity,
          severeToxicity,
          insult,
          profanity,
        },
      };
    }

    return {
      isValid: true,
      scores: {
        toxicity,
        severeToxicity,
        insult,
        profanity,
      },
    };
  } catch (error) {
    console.error("Error validando contenido con Perspective API:", error);
    // Si hay error, permitimos el contenido (fail-open para no bloquear usuarios legítimos)
    return { isValid: true };
  }
}

/**
 * Valida múltiples campos de texto
 */
export async function validateFormContent(
  fields: Record<string, string>
): Promise<{ isValid: boolean; errors: Record<string, string> }> {
  const errors: Record<string, string> = {};

  // Validar cada campo de texto
  for (const [fieldName, text] of Object.entries(fields)) {
    if (!text || text.trim().length === 0) {
      continue; // Los campos vacíos se validan en otro lugar
    }

    const result = await validateContent(text, fieldName);
    if (!result.isValid && result.reason) {
      errors[fieldName] = result.reason;
    }
  }

  return {
    isValid: Object.keys(errors).length === 0,
    errors,
  };
}

