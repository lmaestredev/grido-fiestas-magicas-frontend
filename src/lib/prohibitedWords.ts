export const PROHIBITED_WORDS = [
  // Insultos y palabras ofensivas
  "puto", "puta", "putos", "putas",
  "boludo", "boluda", "boludos", "boludas",
  "pelotudo", "pelotuda", "pelotudos", "pelotudas",
  "hijo de puta", "hdp", "hija de puta",
  "forro", "forra", "forros", "forras",
  "garca", "garcas",
  "choto", "chota", "chotos", "chotas",
  "cagón", "cagona", "cagones", "cagonas",
  "maricón", "maricona", "maricones", "mariconas",
  "trolo", "trola", "trolos", "trolas",
  "mogólico", "mogólica", "mogólicos", "mogólicas",
  "retrasado", "retrasada", "retrasados", "retrasadas",
  "idiota", "idiotas", "imbécil", "imbéciles",
  "estúpido", "estúpida", "estúpidos", "estúpidas",
  "tarado", "tarada", "tarados", "taradas",
  "gil", "giles", "gilada",
  "salame", "salames",
  "cretino", "cretina", "cretinos", "cretinas",

  // Palabrotas y vulgaridades
  "mierda", "mierdas",
  "cagar", "cagaste", "cagó", "cagamos", "cagada", "cagadas",
  "concha", "conchas",
  "pija", "pijas", "verga", "vergas",
  "pito", "pitos",
  "culo", "culos", "orto", "ortos",
  "chupar", "chupame", "chupala", "chupamela",
  "coger", "cogiste", "cogió", "cogeme", "cogete",
  "cojer", "cojiste", "cojio",
  "follar", "follaste", "folló",
  "garchar", "garchaste", "garchó",
  "culeado", "culeada", "culear",
  "chingar", "chingaste", "chingó",
  "joder", "jodete", "joderse",
  "carajo", "carajos",
  "chingada", "chingado",

  // Contenido sexual explícito
  "sexo", "sexual", "sexuales",
  "porno", "pornografía", "pornografico", "pornográfico",
  "masturbar", "masturbación", "masturbarse",
  "orgasmo", "orgasmos",
  "pene", "penes",
  "vagina", "vaginas",
  "coito", "coitos",
  "tetas", "teta", "pechos",
  "eyacular", "eyaculación",
  "erección", "erecto",
  "desnudo", "desnuda", "desnudos", "desnudas",

  // Términos discriminatorios
  "negro de mierda", "negros",
  "judío de mierda",
  "indio de mierda",
  "puto marica",
  "travesti", "travestis",
  "machona", "machonas",
  "tortillera", "tortilleras",

  // Delincuencia
  "chanta", "chantas",
  "trucho", "trucha", "truchos", "truchas",
  "chorear", "choreo", "choreaste", "chorro", "chorros",
  "afanar", "afano", "afanaste", "afanó",
  "robar", "robaste", "robó",
  "matar", "mataste", "mató", "asesinar",
  "violar", "violador", "violación",
  "drogas", "droga", "merca", "faso", "porro",
  "cocaína", "marihuana", "éxtasis",

  // Variaciones con caracteres especiales
  "put0", "put@", "p_u_t_o", "p.u.t.o",
  "bolud0", "b0ludo", "b0lud@", "b.o.l.u.d.o",
  "pelotud0", "p3l0tud0", "p.e.l.o.t.u.d.o",
  "mierd@", "mierd4", "m1erd4", "m.i.e.r.d.a",
  "c0ger", "c0j3r",

  // Frases ofensivas
  "andá a cagar", "andate a cagar",
  "andate a la mierda", "vete a la mierda",
  "que te den", "que te jodan",
  "que se vaya a la mierda",
  "la puta madre",
  "la concha de tu madre",
  "la concha de la lora",
  "la puta que te parió",
  "me cago en",
  "chupame la pija",
  "metete lo en el orto",

  // Contenido político
  "político", "política", "políticos", "políticas",
  "partido político", "partidos políticos",
  "gobierno", "gobiernos",
  "presidente", "presidenta", "presidentes",
  "diputado", "diputada", "diputados",
  "senador", "senadora", "senadores",
  "elección", "elecciones", "electoral",
  "voto", "votar", "votación",
  "campaña electoral", "campaña política",
  "candidato", "candidatos", "candidata", "candidatas",
  "izquierda", "derecha", "centro",
  "kirchnerismo", "kirchnerista", "kirchneristas",
  "macrismo", "macrista", "macristas",
  "peronismo", "peronista", "peronistas",
  "radicalismo", "radical", "radicales",
  "libertario", "libertarios", "libertad avanza",
  "milei", "javier milei",
  "cristina", "cristina kirchner", "cfk",
  "macri", "mauricio macri",
  "alberto", "alberto fernández",
  "massa", "sergio massa",
  "larreta", "rodríguez larreta",
  "bullrich", "patricia bullrich",
  "kicillof", "axel kicillof",
  "congreso", "legislatura",
  "dictadura", "golpe de estado",
  "corrupción", "corrupto", "corruptos",

  // Contenido religioso
  "religión", "religiosa", "religioso", "religiosos",
  "iglesia", "iglesias", "catedral", "catedrales",
  "templo", "templos", "mezquita", "sinagoga",
  "biblia", "corán", "torá", "evangelio",
  "dios", "jesús", "jesucristo", "cristo",
  "alá", "buda", "mahoma",
  "virgen maría", "virgen", "santa",
  "cristiano", "cristianos", "cristianismo",
  "católico", "católicos", "catolicismo",
  "musulmán", "musulmanes", "islam", "islámico",
  "judío", "judíos", "judaísmo",
  "protestante", "evangélico", "evangélicos",
  "ateo", "ateos", "ateísmo",
  "pastor", "pastores",
  "sacerdote", "cura", "obispo",
  "rabino", "rabinos",
  "imán", "imanes",
  "monja", "monjas", "hermana",
  "fe religiosa", "creyente", "creyentes",
  "culto religioso", "misa", "rezo", "rezar", "oración",
  "pecado", "pecados", "infierno", "cielo", "paraíso",
  "bendición", "bendecir", "santificar",
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

