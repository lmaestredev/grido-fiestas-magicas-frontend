// Lista de palabras prohibidas en español argentino
// Incluye variaciones comunes, argentinismos y lunfardo vulgar
export const PROHIBITED_WORDS = [
  // Palabras ofensivas básicas
  "puto", "puta", "putos", "putas",
  "boludo", "boluda", "boludos", "boludas",
  "pelotudo", "pelotuda", "pelotudos", "pelotudas",
  "hijo de puta", "hdp",
  "forro", "forra", "forros", "forras",
  "garca", "garcas",
  "choto", "chota", "chotos", "chotas",
  "cagón", "cagona", "cagones", "cagonas",
  "maricón", "maricona", "maricones", "mariconas",
  "trolo", "trola", "trolos", "trolas",
  "mogólico", "mogólica", "mogólicos", "mogólicas",
  "retrasado", "retrasada", "retrasados", "retrasadas",
  
  // Insultos y groserías
  "mierda", "mierdas",
  "cagar", "cagaste", "cagó", "cagamos",
  "concha", "conchas",
  "pija", "pijas",
  "chupar", "chupame", "chupala",
  "coger", "cogiste", "cogió",
  "cojer", "cojiste", "cojio",
  "follar", "follaste", "folló",
  
  // Argentinismos vulgares
  "chanta", "chantas",
  "trucho", "trucha", "truchos", "truchas",
  "chorear", "choreo", "choreaste",
  "afanar", "afano", "afanaste",
  
  // Contenido sexual explícito
  "sexo", "sexual", "sexuales",
  "porno", "pornografía", "pornografico",
  "masturbar", "masturbación",
  "orgasmo", "orgasmos",
  "pene", "penes",
  "vagina", "vaginas",
  "coito", "coitos",
  
  // Palabras con variaciones (sin acentos, con números)
  "put0", "put@", "p_u_t_o",
  "bolud0", "b0ludo", "b0lud@",
  "pelotud0", "p3l0tud0",
  "mierd@", "mierd4", "m1erd4",
  
  // Frases comunes ofensivas
  "andá a cagar",
  "andate a la mierda",
  "que te den",
  "que se vaya a la mierda",
  "la puta madre",
  "la concha de tu madre",
  "la concha de la lora",
] as const;

// Función para normalizar texto (quitar acentos, convertir a minúsculas, etc.)
export function normalizeText(text: string): string {
  return text
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "") // Quitar acentos
    .replace(/[^a-z0-9\s]/g, " ") // Reemplazar caracteres especiales por espacios
    .replace(/\s+/g, " ") // Múltiples espacios por uno solo
    .trim();
}

// Función para verificar si el texto contiene palabras prohibidas
export function containsProhibitedWords(text: string): boolean {
  const normalized = normalizeText(text);
  const words = normalized.split(/\s+/);
  
  // Verificar palabras individuales
  for (const word of words) {
    if (PROHIBITED_WORDS.includes(word as typeof PROHIBITED_WORDS[number])) {
      return true;
    }
  }
  
  // Verificar frases completas
  for (const phrase of PROHIBITED_WORDS) {
    if (phrase.includes(" ") && normalized.includes(phrase)) {
      return true;
    }
  }
  
  return false;
}

