"""
Configuración de Papá Noel: Voz, Diálogos y Contexto.

Este módulo define:
- La voz de Papá Noel (voice ID para TTS)
- Diálogos base y marcos de diálogo
- Contexto y personalidad para generar mensajes personalizados
"""

import os
from typing import Dict, Any, Optional

# ============================================================================
# CONFIGURACIÓN DE VOZ
# ============================================================================

# Voice ID de Papá Noel (ElevenLabs)
# Puedes cambiar esto en el .env con PAPA_NOEL_VOICE_ID
PAPA_NOEL_VOICE_ID = os.getenv("PAPA_NOEL_VOICE_ID", "bkVwoLpm00fYfz45ZQAb")  # Voice ID de Papá Noel

# Avatar ID para HeyGen (si se usa)
PAPA_NOEL_AVATAR_ID = os.getenv("PAPA_NOEL_AVATAR_ID", "default")


# ============================================================================
# PERSONALIDAD Y CONTEXTO DE PAPÁ NOEL
# ============================================================================

PAPA_NOEL_PERSONALITY = """
Eres Papá Noel (Santa Claus), un personaje cálido, alegre y paternal. 
Tus características principales:
- Hablás con un tono cálido y afectuoso
- Usás expresiones argentinas naturales (vos, mirá, contáme, etc.)
- Sos entusiasta y positivo
- Mostrás orgullo y alegría por los logros de los niños
- Recordás detalles especiales con cariño
- Prometés hacer lo posible por cumplir los deseos
- Mencionás a Grido y los helados de forma natural
- Terminás con un mensaje de Fiestas Mágicas
"""

PAPA_NOEL_CONTEXT = """
Contexto de la situación:
- Es la Noche Mágica (Nochebuena/Navidad)
- Estás en Argentina
- Grido es el patrocinador de esta iniciativa
- Los padres/familiares envían mensajes personalizados para sus hijos
- Querés hacer que cada niño se sienta especial y querido
"""


# ============================================================================
# DIÁLOGOS BASE Y PLANTILLAS
# ============================================================================

# Frase de introducción (Frame 2)
FRAME2_PHRASE = "¡Ho, ho, ho! Mirá lo que tengo para vos..."

# Plantilla principal del mensaje (Frame 3)
FRAME3_TEMPLATE = """
¡Hola {nombre}! Soy Papá Noel y vengo desde el Polo Norte para saludarte en esta Noche Mágica.

Tu {parentesco} me contó que este año {queHizo}. ¡Qué orgullo me da saber eso!

{recuerdoEspecial}

Y me dijeron que tu pedido especial para esta Noche Mágica es: {pedidoNocheMagica}. 
Voy a hacer todo lo posible para que se cumpla.

Desde Grido y desde el Polo Norte, te deseamos unas Fiestas Mágicas llenas de alegría. 
Y recordá, la magia está en compartir... ¡y en un rico helado de Grido!

¡Ho, ho, ho! ¡Feliz Noche Mágica!
"""


# ============================================================================
# FRASES Y EXPRESIONES TÍPICAS DE PAPÁ NOEL
# ============================================================================

PAPA_NOEL_PHRASES = {
    "greetings": [
        "¡Ho, ho, ho!",
        "¡Hola {nombre}!",
        "¡Qué alegría verte!",
        "¡Feliz Noche Mágica!",
    ],
    "acknowledgments": [
        "¡Qué orgullo me da saber eso!",
        "¡Eso es increíble!",
        "¡Qué bien que hiciste eso!",
        "¡Me encanta escuchar eso!",
    ],
    "memories": [
        "Ese recuerdo es muy especial",
        "Ese momento quedará para siempre",
        "Qué lindo que compartan esos momentos",
        "Eso es lo que hace que la magia sea real",
    ],
    "promises": [
        "Voy a hacer todo lo posible para que se cumpla",
        "Voy a ver qué puedo hacer",
        "Voy a intentar cumplir tu deseo",
        "Haré mi mejor esfuerzo",
    ],
    "closings": [
        "¡Feliz Noche Mágica desde {provincia}!",
        "¡Que tengas unas Fiestas Mágicas increíbles!",
        "¡Que la magia te acompañe siempre!",
        "¡Un abrazo grande desde el Polo Norte!",
    ],
}


# ============================================================================
# FUNCIONES PARA GENERAR MENSAJES
# ============================================================================

def get_papa_noel_voice_id() -> str:
    """Obtiene el Voice ID de Papá Noel."""
    return PAPA_NOEL_VOICE_ID


def get_papa_noel_avatar_id() -> str:
    """Obtiene el Avatar ID de Papá Noel (para HeyGen)."""
    return PAPA_NOEL_AVATAR_ID


def generate_frame2_script() -> str:
    """Genera el script para el Frame 2 (introducción)."""
    return FRAME2_PHRASE


def generate_frame3_script(form_data: Dict[str, Any]) -> str:
    """
    Genera el script para el Frame 3 (mensaje principal).
    
    Args:
        form_data: Datos del formulario con:
            - nombre: Nombre del niño
            - parentesco: Parentesco (papá, mamá, etc.)
            - queHizo: Qué hizo el niño en el año
            - recuerdoEspecial: Recuerdo especial
            - pedidoNocheMagica: Pedido para la Noche Mágica
            - provincia: Provincia de Argentina
    
    Returns:
        Script completo para el Frame 3
    """
    return FRAME3_TEMPLATE.format(**form_data)


def get_papa_noel_system_prompt() -> str:
    """
    Obtiene el prompt del sistema para Papá Noel.
    Útil si se usa un LLM para generar diálogos más personalizados.
    """
    return f"{PAPA_NOEL_PERSONALITY}\n\n{PAPA_NOEL_CONTEXT}"


def get_papa_noel_context_for_tts() -> str:
    """
    Obtiene el contexto completo para TTS.
    Puede usarse como contexto adicional al generar el audio.
    """
    return f"""
    {PAPA_NOEL_PERSONALITY}
    
    {PAPA_NOEL_CONTEXT}
    
    Instrucciones para la voz:
    - Tono cálido y paternal
    - Entonación alegre y positiva
    - Ritmo pausado pero entusiasta
    - Acento argentino natural
    """


# ============================================================================
# CONFIGURACIÓN AVANZADA (OPCIONAL)
# ============================================================================

# Si quieres usar un LLM para generar diálogos más personalizados
USE_LLM_FOR_DIALOGS = os.getenv("USE_LLM_FOR_DIALOGS", "false").lower() == "true"

# Si está habilitado, se puede usar OpenAI/Anthropic para generar diálogos
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")  # openai, anthropic, etc.
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4")  # gpt-4, claude-3, etc.


def generate_custom_dialog_with_llm(form_data: Dict[str, Any]) -> Optional[str]:
    """
    Genera un diálogo personalizado usando un LLM (si está configurado).
    
    Args:
        form_data: Datos del formulario
    
    Returns:
        Diálogo generado o None si no está configurado
    """
    if not USE_LLM_FOR_DIALOGS:
        return None
    
    # TODO: Implementar generación con LLM
    # Por ahora, usar la plantilla estándar
    return generate_frame3_script(form_data)

