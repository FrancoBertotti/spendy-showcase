"""
Motor de clasificación pre-IA para transacciones.

Evalúa si el texto de entrada matchea con reglas locales
(regex + diccionarios de palabras clave) antes de delegar a la IA.
Toda la lógica de clasificación local vive aquí y SOLO aquí.

Nota: los diccionarios de palabras clave (CATEGORIAS_KEYWORDS y
CATEGORIA_A_PILAR) son parte de la lógica propietaria y no se
incluyen en este extracto.
"""
import re
from typing import Optional
from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Estructura de resultado
# ---------------------------------------------------------------------------

@dataclass
class ClasificacionLocal:
    monto: float
    tipo: str       # 'ingreso' | 'egreso'
    pilar: str      # 'necesidades_basicas' | 'estilo_vida' | 'ahorro_inversion' | 'ingreso'
    categoria: str  # nombre de la categoría sugerida
    descripcion: str


# ---------------------------------------------------------------------------
# Diccionarios de palabras clave
# (contenido propietario no incluido en este extracto)
# ---------------------------------------------------------------------------

# CATEGORIAS_KEYWORDS mapea cada categoría a una lista de palabras clave
# en español. Cubre supermercado, transporte, salud, servicios, ocio,
# inversiones, ingresos y más.
CATEGORIAS_KEYWORDS: dict[str, list[str]] = {
    # "Supermercado": [...],
    # "Transporte Obligatorio": [...],
    # "Comida / Restó": [...],
    # ... (15 categorías en total)
}

# CATEGORIA_A_PILAR mapea cada categoría a uno de los cuatro pilares
# del sistema 50/30/20: necesidades_basicas, estilo_vida,
# ahorro_inversion, ingreso.
CATEGORIA_A_PILAR: dict[str, str] = {
    # "Supermercado": "necesidades_basicas",
    # "Ocio y Salidas": "estilo_vida",
    # "Inversiones": "ahorro_inversion",
    # ...
}

# Palabras que indican que el texto describe un ingreso
PALABRAS_INGRESO = [
    # lista de términos en español para detectar ingresos
]

# Patrón para detectar montos numéricos en texto en español
# Soporta separador de miles con punto y decimales con coma
_PATRON_MONTO = re.compile(
    r'(?:\$|\b)(\d{1,3}(?:\.\d{3})+|\d+)(?:[,\.](\d{1,2}))?\b'
)


# ---------------------------------------------------------------------------
# Lógica de clasificación
# ---------------------------------------------------------------------------

def _extraer_monto(texto: str) -> Optional[float]:
    """Extrae el primer monto numérico encontrado en el texto."""
    m = _PATRON_MONTO.search(texto)
    if not m:
        return None
    entero = m.group(1).replace(".", "")
    decimal = m.group(2) if m.group(2) else "0"
    valor = float(f"{entero}.{decimal}")
    return valor if valor > 0 else None


def _detectar_tipo(texto: str) -> str:
    """Retorna 'ingreso' o 'egreso' según palabras clave."""
    return "ingreso" if any(p in texto for p in PALABRAS_INGRESO) else "egreso"


def _detectar_categoria(texto: str, tipo: str) -> Optional[str]:
    """
    Recorre CATEGORIAS_KEYWORDS y retorna la primera categoría que matchea.
    Si el tipo es ingreso y no matcheó nada, devuelve 'Otros Ingresos'.
    """
    for categoria, keywords in CATEGORIAS_KEYWORDS.items():
        if any(kw in texto for kw in keywords):
            return categoria
    if tipo == "ingreso":
        return "Otros Ingresos"
    return None


def clasificar(texto: str) -> Optional[ClasificacionLocal]:
    """
    Intenta clasificar el texto usando solo reglas locales.

    Retorna ClasificacionLocal si la clasificación es confiable,
    o None si el texto es ambiguo y debe delegarse a la IA.
    """
    texto_limpio = texto.lower().strip()

    monto = _extraer_monto(texto_limpio)
    if monto is None:
        return None  # Sin monto claro → delegar a IA

    tipo = _detectar_tipo(texto_limpio)
    categoria = _detectar_categoria(texto_limpio, tipo)

    # Si no matcheó categoría y el texto es elaborado → delegar a IA
    if categoria is None and len(texto_limpio.split()) > 3:
        return None

    categoria_final = categoria or "Varios"
    pilar = CATEGORIA_A_PILAR.get(categoria_final, "estilo_vida")

    return ClasificacionLocal(
        monto=monto,
        tipo=tipo,
        pilar=pilar,
        categoria=categoria_final,
        descripcion=texto.strip().capitalize(),
    )
