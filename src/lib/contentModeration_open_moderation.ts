import { containsProhibitedWords } from "./prohibitedWords";

const OPENAI_API_KEY = process.env.OPEN_AI_API_KEY || "";
const OPENAI_MODERATION_URL = "https://api.openai.com/v1/moderations";

// Umbrales de score para cada categoría (0-1, donde 1 es 100% de confianza)
const MODERATION_THRESHOLDS = {
  hate: 0.3,
  harassment: 0.4,
  violence: 0.4,
  sexual: 0.3,
  "self-harm": 0.3,
};

interface OpenAIModerationResponse {
  id: string;
  model: string;
  results: Array<{
    flagged: boolean;
    categories: {
      sexual: boolean;
      hate: boolean;
      harassment: boolean;
      "self-harm": boolean;
      "sexual/minors": boolean;
      "hate/threatening": boolean;
      "violence/graphic": boolean;
      "self-harm/intent": boolean;
      "self-harm/instructions": boolean;
      "harassment/threatening": boolean;
      violence: boolean;
    };
    category_scores: {
      sexual: number;
      hate: number;
      harassment: number;
      "self-harm": number;
      "sexual/minors": number;
      "hate/threatening": number;
      "violence/graphic": number;
      "self-harm/intent": number;
      "self-harm/instructions": number;
      "harassment/threatening": number;
      violence: number;
    };
  }>;
}

export interface ContentModerationResult {
  isValid: boolean;
  reason?: string;
  scores?: {
    hate?: number;
    harassment?: number;
    violence?: number;
    sexual?: number;
  };
  categories?: string[];
}

export async function validateContent(
  text: string,
  fieldName: string
): Promise<ContentModerationResult> {
  // Validar palabras prohibidas (incluye contenido ofensivo, político y religioso)
  if (containsProhibitedWords(text)) {
    return {
      isValid: false,
      reason: `El contenido contiene palabras o frases inapropiadas. Por favor, usá un lenguaje respetuoso y evitá temas políticos o religiosos.`,
    };
  }

  if (!OPENAI_API_KEY) {
    console.warn("OPENAI_API_KEY no configurada, solo validando con lista de palabras");
    return { isValid: true };
  }

  try {
    const response = await fetch(OPENAI_MODERATION_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${OPENAI_API_KEY}`,
      },
      body: JSON.stringify({
        input: text,
        model: "omni-moderation-latest",
      }),
    });

    if (!response.ok) {
      console.error("Error en OpenAI Moderation API:", await response.text());
      return { isValid: true };
    }

    const data: OpenAIModerationResponse = await response.json();
    const result = data.results[0];

    if (!result) {
      console.error("No se recibió resultado de OpenAI Moderation");
      return { isValid: true };
    }

    // Verificar scores contra los umbrales definidos
    const violatedCategories: string[] = [];
    let hasViolation = false;

    if (result.category_scores.hate > MODERATION_THRESHOLDS.hate) {
      violatedCategories.push("odio");
      hasViolation = true;
    }
    if (result.category_scores.harassment > MODERATION_THRESHOLDS.harassment) {
      violatedCategories.push("acoso");
      hasViolation = true;
    }
    if (result.category_scores.violence > MODERATION_THRESHOLDS.violence) {
      violatedCategories.push("violencia");
      hasViolation = true;
    }
    if (result.category_scores.sexual > MODERATION_THRESHOLDS.sexual) {
      violatedCategories.push("contenido sexual");
      hasViolation = true;
    }
    if (result.category_scores["self-harm"] > MODERATION_THRESHOLDS["self-harm"]) {
      violatedCategories.push("autolesión");
      hasViolation = true;
    }

    // También verificar las categorías marcadas como flagged por OpenAI
    if (result.flagged || hasViolation) {
      return {
        isValid: false,
        reason: `El contenido no es apropiado. Por favor, usá un lenguaje respetuoso y positivo.`,
        scores: {
          hate: result.category_scores.hate,
          harassment: result.category_scores.harassment,
          violence: result.category_scores.violence,
          sexual: result.category_scores.sexual,
        },
        categories: violatedCategories,
      };
    }

    return {
      isValid: true,
      scores: {
        hate: result.category_scores.hate,
        harassment: result.category_scores.harassment,
        violence: result.category_scores.violence,
        sexual: result.category_scores.sexual,
      },
    };
  } catch (error) {
    console.error("Error validando contenido con OpenAI Moderation API:", error);
    return { isValid: true };
  }
}

export async function validateFormContent(
  fields: Record<string, string>
): Promise<{ isValid: boolean; errors: Record<string, string> }> {
  const errors: Record<string, string> = {};

  for (const [fieldName, text] of Object.entries(fields)) {
    if (!text || text.trim().length === 0) {
      continue;
    }

    const result = await validateContent(text, fieldName);
    console.log(`Moderation result for field ${fieldName}:`, result);
    if (!result.isValid && result.reason) {
      errors[fieldName] = result.reason;
    }
  }

  return {
    isValid: Object.keys(errors).length === 0,
    errors,
  };
}

