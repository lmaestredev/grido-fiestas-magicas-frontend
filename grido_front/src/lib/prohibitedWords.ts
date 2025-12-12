export const PROHIBITED_WORDS = [
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
  "mierda", "mierdas",
  "cagar", "cagaste", "cagó", "cagamos",
  "concha", "conchas",
  "pija", "pijas",
  "chupar", "chupame", "chupala",
  "coger", "cogiste", "cogió",
  "cojer", "cojiste", "cojio",
  "follar", "follaste", "folló",
  "chanta", "chantas",
  "trucho", "trucha", "truchos", "truchas",
  "chorear", "choreo", "choreaste",
  "afanar", "afano", "afanaste",
  "sexo", "sexual", "sexuales",
  "porno", "pornografía", "pornografico",
  "masturbar", "masturbación",
  "orgasmo", "orgasmos",
  "pene", "penes",
  "vagina", "vaginas",
  "coito", "coitos",
  "put0", "put@", "p_u_t_o",
  "bolud0", "b0ludo", "b0lud@",
  "pelotud0", "p3l0tud0",
  "mierd@", "mierd4", "m1erd4",
  "andá a cagar",
  "andate a la mierda",
  "que te den",
  "que se vaya a la mierda",
  "la puta madre",
  "la concha de tu madre",
  "la concha de la lora",
] as const;

export function normalizeText(text: string): string {
  return text
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-z0-9\s]/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

export function containsProhibitedWords(text: string): boolean {
  const normalized = normalizeText(text);
  const words = normalized.split(/\s+/);
  
  for (const word of words) {
    if (PROHIBITED_WORDS.includes(word as typeof PROHIBITED_WORDS[number])) {
      return true;
    }
  }
  
  for (const phrase of PROHIBITED_WORDS) {
    if (phrase.includes(" ") && normalized.includes(phrase)) {
      return true;
    }
  }
  
  return false;
}

