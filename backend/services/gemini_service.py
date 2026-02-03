import google.generativeai as genai
from dotenv import load_dotenv
import os
from PIL import Image
import io
import json
from langfuse import observe
import base64

load_dotenv()

# Configurar Gemini
genai.configure(api_key=os.getenv("GOOGLE_AI_KEY"))

# MODELO CORRECTO - De tu lista disponible
VISION_MODEL = "gemini-2.0-flash"  

@observe(name="multimodal_audit")
async def audit_image_against_brand_manual(
    image_bytes: bytes,
    manual_content: dict,
    brand_name: str
) -> dict:
    """
    Audita una imagen contra el manual de marca usando Gemini Vision
    """
    
    try:
        # Cargar imagen con PIL
        image = Image.open(io.BytesIO(image_bytes))
        
        # Construir el manual como texto COMPLETO Y DETALLADO
        elementos_visuales = manual_content.get('elementos_visuales', {})
        tono = manual_content.get('tono_comunicacion', {})
        uso_logo = elementos_visuales.get('uso_logo', {})
        identidad = manual_content.get('identidad_marca', {})
        
        manual_text = f"""
MANUAL DE MARCA - {brand_name}

=== IDENTIDAD DE MARCA ===
Propósito: {identidad.get('proposito', 'No especificado')}
Valores: {identidad.get('valores', 'No especificado')}
Personalidad: {identidad.get('personalidad', 'No especificado')}

=== ELEMENTOS VISUALES OBLIGATORIOS ===
• Colores PRINCIPALES (DEBEN aparecer): {elementos_visuales.get('colores_principales', 'No especificado')}
• Colores SECUNDARIOS (pueden aparecer): {elementos_visuales.get('colores_secundarios', 'No especificado')}
• Estilo fotográfico REQUERIDO: {elementos_visuales.get('estilo_fotografico', 'No especificado')}
• Composición visual: {elementos_visuales.get('composicion_visual', 'No especificado')}
• Iconografía: {elementos_visuales.get('iconografia', 'No especificado')}
• Tipografía principal: {elementos_visuales.get('tipografia_principal', 'No especificado')}
• Tipografía secundaria: {elementos_visuales.get('tipografia_secundaria', 'No especificado')}

=== ELEMENTOS OBLIGATORIOS ===
{elementos_visuales.get('elementos_obligatorios', 'No especificado')}

=== ELEMENTOS PROHIBIDOS (SI APARECEN = FALLO AUTOMÁTICO) ===
{elementos_visuales.get('elementos_prohibidos', 'No especificado')}

=== REGLAS DE USO DEL LOGO (CRÍTICAS) ===
• Tamaño mínimo: {uso_logo.get('tamano_minimo', 'No especificado')}
• Espaciado mínimo alrededor: {uso_logo.get('espaciado_minimo', 'No especificado')}
• Posiciones permitidas: {uso_logo.get('posicion_permitida', 'No especificado')}
• Fondos PERMITIDOS: {uso_logo.get('fondos_permitidos', 'No especificado')}
• Fondos PROHIBIDOS: {uso_logo.get('fondos_prohibidos', 'No especificado')}
• Elementos adicionales: {uso_logo.get('elementos_adicionales', 'No especificado')}

=== TONO Y ESTILO ===
{tono.get('descripcion_general', 'No especificado')}
Palabras permitidas: {tono.get('palabras_permitidas', 'No especificado')}
Palabras prohibidas: {tono.get('palabras_prohibidas', 'No especificado')}
"""
        
        # Prompt para Gemini Vision - AUDITORÍA ESTRICTA EN ESPAÑOL
        prompt = f"""Eres un auditor PROFESIONAL de identidad de marca. Tu trabajo es analizar esta imagen y determinar si cumple con el manual de marca.

{manual_text}

=== METODOLOGÍA DE AUDITORÍA ===

**PASO 1 - DESCRIPCIÓN VISUAL**: Describe con precisión lo que ves en la imagen:
- ¿Qué producto/elemento principal aparece?
- ¿Qué colores dominantes hay? (identifica tonos aproximados)
- ¿Hay logo visible? ¿Dónde está? ¿Qué tamaño aparente tiene?
- ¿Qué tipo de fondo hay?
- ¿Hay texto? ¿Qué tipografía parece tener?
- ¿Qué elementos adicionales hay? (ingredientes, iconos, etc.)

**PASO 2 - EVALUACIÓN POR CATEGORÍAS** (asigna puntos por categoría):

1. **COLORES (peso 25%)** - CRITERIO: Aproximaciones visuales son aceptables
   - ¿Los colores PRINCIPALES del manual están presentes en la imagen? ✓/✗
   - ¿Los tonos son VISUALMENTE SIMILARES a los especificados? (no necesitan ser HEX exacto) ✓/✗
   - ¿Hay colores COMPLETAMENTE AJENOS a la paleta? ✗ (penaliza -10 puntos)
   - Ejemplo: Si el manual dice "#34C759" (verde) y la imagen tiene un verde similar/cercano = ✓
   - Puntos: 0-25

2. **LOGO Y BRANDING (peso 30%)** - CRITERIO ESTRICTO:
   - ¿El logo está presente y visible? ✓/✗ (si NO = -10 puntos)
   - ¿Cumple tamaño mínimo aproximado especificado? ✓/✗
   - ¿Tiene espaciado visual adecuado? ✓/✗
   - ¿Está en una de las posiciones permitidas? ✓/✗ (si NO = -10 puntos)
   - ¿El fondo del logo es de los permitidos? ✓/✗
   - Puntos: 0-30

3. **ESTILO FOTOGRÁFICO Y COMPOSICIÓN (peso 20%)**:
   - ¿La iluminación coincide con el manual? (natural, cálida, etc.) ✓/✗
   - ¿La composición general es la especificada? (minimalista, centrado, etc.) ✓/✗
   - ¿El mood/atmósfera es correcto? (alegre, fresco, profesional, etc.) ✓/✗
   - Puntos: 0-20

4. **ELEMENTOS OBLIGATORIOS/PROHIBIDOS (peso 15%)** - CRITERIO ESTRICTO:
   - ¿Están TODOS los elementos obligatorios presentes? ✓/✗ (si falta uno = -8 puntos)
   - ¿NO aparece NINGÚN elemento de los prohibidos? ✓/✗ (si aparece uno = -15 puntos)
   - Puntos: 0-15

5. **TIPOGRAFÍA Y TEXTO (peso 10%)**:
   - Si hay texto, ¿el estilo es similar a la tipografía del manual? ✓/✗
   - ¿El tono del texto es apropiado? ✓/✗
   - Puntos: 0-10

**PASO 3 - CÁLCULO FINAL**:
- Score total: suma de puntos (0-100)
- Compliant: true si score >= 72, false si < 72
- Issues: lista de incumplimientos en ESPAÑOL
- Recommendations: soluciones concretas en ESPAÑOL

**IMPORTANTE - RESPONDE EN ESPAÑOL**:
- Todos los textos deben estar en español
- Usa términos técnicos en español cuando sea apropiado
- Sé claro y profesional

RESPONDE EN FORMATO JSON EXACTO (sin markdown, sin código, TODO EN ESPAÑOL):
{{
  "compliant": boolean,
  "score": number,
  "issues": ["string en español"],
  "recommendations": ["string en español"],
  "analysis": "string en español - descripción detallada",
  "category_scores": {{
    "colors": number,
    "branding": number,
    "photography_style": number,
    "elements": number,
    "typography": number
  }}
}}

⚠️ CRITERIOS DE EVALUACIÓN:
- COLORES: Acepta tonos visualmente similares (no necesitan HEX exacto)
- LOGO: Estricto en posición y visibilidad
- COMPOSICIÓN: Evalúa el estilo general, no detalles mínimos
- ELEMENTOS: Estricto en obligatorios/prohibidos
- El objetivo es evaluar si la imagen COMUNICA la marca correctamente, no si es pixel-perfect
"""
        
        # Llamar a Gemini Vision usando la API correcta
        model = genai.GenerativeModel(VISION_MODEL)
        
        response = model.generate_content([
            prompt,
            image
        ])
        
        # Parsear respuesta
        response_text = response.text.strip()
        
        # Limpiar markdown si existe
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        # Intentar parsear JSON
        try:
            result = json.loads(response_text)
        except json.JSONDecodeError:
            # Si falla, crear estructura básica con el análisis en texto
            result = {
                "compliant": False,
                "score": 50,
                "issues": ["No se pudo parsear respuesta estructurada"],
                "recommendations": ["Verificar formato de imagen"],
                "analysis": response_text
            }
        
        # Validar y completar estructura
        if "compliant" not in result:
            result["compliant"] = False
        if "score" not in result:
            result["score"] = 0
        if "issues" not in result or not isinstance(result["issues"], list):
            result["issues"] = []
        if "recommendations" not in result or not isinstance(result["recommendations"], list):
            result["recommendations"] = []
        if "analysis" not in result:
            result["analysis"] = "Análisis no disponible"
        
        return result
        
    except Exception as e:
        raise Exception(f"Error en auditoría con Gemini: {str(e)}")


async def test_gemini_connection() -> dict:
    """
    Prueba la conexión con Google Gemini
    """
    try:
        model = genai.GenerativeModel(VISION_MODEL)
        response = model.generate_content("Responde solo con la palabra: OK")
        
        return {
            "status": "connected",
            "model": VISION_MODEL,
            "response": response.text.strip()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }