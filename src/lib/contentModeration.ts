import { containsProhibitedWords } from "./prohibitedWords";

const OPENAI_API_KEY = process.env.OPEN_AI_API_KEY || "";
const OPENAI_CHAT_URL = "https://api.openai.com/v1/chat/completions";

interface OpenAIChatResponse {
  id: string;
  object: string;
  created: number;
  model: string;
  choices: Array<{
    index: number;
    message: {
      role: string;
      content: string;
    };
    finish_reason: string;
  }>;
  usage: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
}

interface ModerationAnalysis {
  isValid: boolean;
  reason?: string;
  categories?: string[];
  scores?: {
    toxicity?: number;
    inappropriate?: number;
    offensive?: number;
  };
}

export interface ContentModerationResult {
  isValid: boolean;
  reason?: string;
  scores?: {
    toxicity?: number;
    inappropriate?: number;
    offensive?: number;
  };
  categories?: string[];
}

async function analyzeWithGPT(text: string): Promise<ModerationAnalysis> {
  const systemPrompt = `Eres un moderador de contenido experto. Tu tarea es analizar textos destinados a saludos navideños familiares para niños.

Debes rechazar contenido que contenga:
1. Lenguaje ofensivo, vulgar o inapropiado
2. Contenido sexual o sugerente
3. Violencia o amenazas
4. Discurso de odio o discriminación
5. Referencias políticas o religiosas (aunque sean positivas)
6. Drogas, alcohol o sustancias ilícitas
7. Temas sensibles o inapropiados para niños

Debes aprobar contenido que sea:
- Alegre, positivo y familiar
- Apropiado para todas las edades
- Relacionado con celebraciones, logros personales, recuerdos felices
- Sin mencionar política, religión o temas controvertidos

Responde ÚNICAMENTE con un objeto JSON válido con esta estructura:
{
  "isValid": true o false,
  "reason": "explicación breve en español argentino (solo si isValid es false)",
  "categories": ["categoría1", "categoría2"] (solo si isValid es false),
  "confidence": número entre 0 y 1
}`;

  const userPrompt = `Analiza el siguiente texto y determina si es apropiado para un saludo navideño familiar:

"${text}"

Responde solo con el objeto JSON.`;

  try {
    const response = await fetch(OPENAI_CHAT_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${OPENAI_API_KEY}`,
      },
      body: JSON.stringify({
        model: "gpt-5.2",
        messages: [
          { role: "system", content: systemPrompt },
          { role: "user", content: userPrompt },
        ],
        max_completion_tokens: 300,
        response_format: { type: "json_object" },
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error("Error en OpenAI Chat API:", errorText);
      return { isValid: true }; // Fallback: aprobar si hay error
    }

    const data: OpenAIChatResponse = await response.json();
    const content = data.choices[0]?.message?.content;

    if (!content) {
      console.error("No se recibió contenido de GPT");
      return { isValid: true };
    }

    const analysis = JSON.parse(content) as ModerationAnalysis;
    return analysis;
  } catch (error) {
    console.error("Error en análisis con GPT:", error);
    return { isValid: true }; // Fallback: aprobar si hay error
  }
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
    const gptAnalysis = await analyzeWithGPT(text);

    if (!gptAnalysis.isValid) {
      return {
        isValid: false,
        reason:
          gptAnalysis.reason ||
          "El contenido no es apropiado. Por favor, usá un lenguaje respetuoso y positivo.",
        categories: gptAnalysis.categories,
        scores: gptAnalysis.scores,
      };
    }

    return {
      isValid: true,
      scores: gptAnalysis.scores,
    };
  } catch (error) {
    console.error("Error validando contenido con GPT:", error);
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

