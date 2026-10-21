"""
Orquestador híbrido: clasificación local → Groq IA como fallback.

Primero intenta clasificar con reglas locales (classifier.py).
Solo si el texto es ambiguo o no hay match, llama a la IA.
Esto minimiza latencia y costo en los casos más comunes.
"""
import json
import os

from groq import Groq

# from app.core.classifier import clasificar
# from app.modules.ai_parser.schemas import TransaccionExtraida


MODELOS_GROQ = [
    "qwen/qwen3.8-27b",
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "allam-2-7b",
]


def _procesar_con_ia(texto_usuario: str):
    """Llama a Groq con estrategia de fallback entre modelos."""
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    prompt = (
        f"Analiza el siguiente texto de un gasto o ingreso: '{texto_usuario}'. "
        "Devuelve ÚNICAMENTE un objeto JSON válido con este formato exacto: "
        '{"monto": float, "tipo": "ingreso" o "egreso", '
        '"pilar": "necesidades_basicas" o "estilo_vida" o "ahorro_inversion" o "ingreso", '
        '"categoria_sugerida": "string", "descripcion": "string"}'
    )

    errores = []
    for modelo in MODELOS_GROQ:
        try:
            response = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "Sos un asistente financiero estructurado. Solo respondes en formato JSON estricto.",
                    },
                    {"role": "user", "content": prompt},
                ],
                model=modelo,
                response_format={"type": "json_object"},
            )
            data = json.loads(response.choices[0].message.content)
            return data  # TransaccionExtraida(**data) en el código real
        except Exception as e:
            errores.append(f"Falló '{modelo}': {e}")

    raise RuntimeError(f"Todos los modelos Groq fallaron: {' | '.join(errores)}")


def procesar_mensaje_con_groq(texto_usuario: str):
    """
    Orquestador híbrido:
    1. Intenta clasificar con reglas locales (classifier.py).
    2. Si el texto es ambiguo o no matchea, delega a Groq IA.
    """
    resultado = clasificar(texto_usuario)  # del classifier local
    if resultado:
        # Match local: respuesta inmediata, sin llamada a la API
        return {
            "monto": resultado.monto,
            "tipo": resultado.tipo,
            "pilar": resultado.pilar,
            "categoria_sugerida": resultado.categoria,
            "descripcion": resultado.descripcion,
        }

    # Texto complejo o ambiguo → delegar a la IA
    return _procesar_con_ia(texto_usuario)
