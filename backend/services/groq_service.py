from groq import Groq
from dotenv import load_dotenv
import os
import json
from langfuse import observe

load_dotenv()

# Inicializar cliente de Groq
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Configuración del modelo
MODEL_NAME = "llama-3.3-70b-versatile"  # Modelo más potente de Groq

@observe(name="generate_brand_manual")
async def generate_brand_manual(
    name: str,
    description: str,
    product_type: str,
    tone: str,
    target_audience: str
) -> dict:
    """
    Genera un manual de marca estructurado usando Groq (Llama 3)
    
    Args:
        name: Nombre del producto/marca
        description: Descripción breve del producto
        product_type: Tipo de producto (snack, bebida, etc.)
        tone: Tono de comunicación deseado
        target_audience: Público objetivo
    
    Returns:
        dict: Manual de marca estructurado en formato JSON
    """
    
    # Prompt engineering para generar un manual completo
    system_prompt = """Eres un experto en branding y marketing estratégico. 
Tu tarea es crear manuales de marca profesionales, detallados y coherentes.
Debes generar un manual en formato JSON con la estructura exacta que se te solicita.
Sé creativo, específico y profesional."""

    user_prompt = f"""
Crea un manual de marca completo y profesional para el siguiente producto:

**INFORMACIÓN DEL PRODUCTO:**
- Nombre: {name}
- Descripción: {description}
- Tipo de producto: {product_type}
- Tono de comunicación: {tone}
- Público objetivo: {target_audience}

**ESTRUCTURA REQUERIDA (Responde SOLO con JSON válido):**

{{
  "identidad_marca": {{
    "proposito": "string (el propósito y misión del producto)",
    "valores": ["valor1", "valor2", "valor3"],
    "personalidad": "string (descripción de la personalidad de la marca)",
    "diferenciador": "string (qué hace único a este producto)"
  }},
  "tono_comunicacion": {{
    "descripcion_general": "string",
    "palabras_permitidas": ["palabra1", "palabra2", "palabra3"],
    "palabras_prohibidas": ["palabra1", "palabra2", "palabra3"],
    "estilo_redaccion": "string (formal, casual, técnico, creativo, etc.)",
    "uso_tecnicismos": "boolean (true si se permiten, false si no)",
    "ejemplos_buenos": ["ejemplo1", "ejemplo2"],
    "ejemplos_malos": ["ejemplo1", "ejemplo2"]
  }},
  "elementos_visuales": {{
    "colores_principales": ["#HEX1", "#HEX2"],
    "colores_secundarios": ["#HEX3", "#HEX4"],
    "tipografia_principal": "string (nombre de fuente)",
    "tipografia_secundaria": "string (nombre de fuente)",
    "uso_logo": {{
      "tamano_minimo": "string (ej: '10% del ancho de la imagen' o '50px mínimo')",
      "espaciado_minimo": "string (ej: '5% del ancho del logo alrededor' o 'espacio blanco equivalente a la altura del logo')",
      "posicion_permitida": ["posición1", "posición2"],
      "fondos_permitidos": ["fondo1", "fondo2"],
      "fondos_prohibidos": ["fondo1", "fondo2"],
      "elementos_adicionales": "string (ej: 'puede aparecer con tagline', 'siempre acompañado de...')"
    }},
    "estilo_fotografico": "string (descripción DETALLADA: iluminación, composición, tipo de tomas, mood, filtros si aplica)",
    "iconografia": "string (tipo de iconos: planos, con sombras, estilo específico)",
    "composicion_visual": "string (ej: 'fondo minimalista con producto centrado', 'ingredientes visibles', 'contraste alto/bajo')",
    "elementos_obligatorios": ["elemento1", "elemento2"],
    "elementos_prohibidos": ["elemento1", "elemento2"]
  }},
  "publico_objetivo": {{
    "demografia": {{
      "edad": "string (rango de edad)",
      "genero": "string",
      "ubicacion": "string",
      "nivel_socioeconomico": "string"
    }},
    "psicografia": {{
      "intereses": ["interés1", "interés2"],
      "valores": ["valor1", "valor2"],
      "estilo_vida": "string"
    }},
    "pain_points": ["problema1", "problema2"],
    "aspiraciones": ["aspiración1", "aspiración2"]
  }},
  "directrices_contenido": {{
    "tipos_contenido": {{
      "redes_sociales": {{
        "longitud_ideal": "string",
        "hashtags": ["#tag1", "#tag2"],
        "frecuencia": "string"
      }},
      "blog_articulos": {{
        "longitud_ideal": "string",
        "estructura": "string",
        "temas_principales": ["tema1", "tema2"]
      }},
      "email_marketing": {{
        "subject_line_style": "string",
        "longitud_ideal": "string",
        "call_to_action": ["CTA1", "CTA2"]
      }}
    }},
    "palabras_clave_seo": ["keyword1", "keyword2", "keyword3"],
    "mensajes_clave": ["mensaje1", "mensaje2", "mensaje3"]
  }},
  "ejemplos_aplicacion": {{
    "descripcion_producto_buena": "string (ejemplo de descripción que sigue el manual)",
    "descripcion_producto_mala": "string (ejemplo de lo que NO hacer)",
    "post_redes_bueno": "string",
    "post_redes_malo": "string"
  }}
}}

IMPORTANTE: 
- Responde ÚNICAMENTE con el JSON, sin texto adicional antes o después
- Asegúrate de que el JSON sea válido y esté completo
- Sé específico y creativo según el producto descrito
- Todos los campos deben tener contenido relevante y detallado
"""

    try:
        # Llamada a Groq API
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            model=MODEL_NAME,
            temperature=0.7,  # Balance entre creatividad y coherencia
            max_tokens=4000,  # Suficiente para un manual completo
            top_p=0.9,
            stream=False
        )
        
        # Extraer respuesta
        response_content = chat_completion.choices[0].message.content
        
        # Limpiar la respuesta (por si viene con markdown)
        response_content = response_content.strip()
        if response_content.startswith("```json"):
            response_content = response_content[7:]
        if response_content.startswith("```"):
            response_content = response_content[3:]
        if response_content.endswith("```"):
            response_content = response_content[:-3]
        response_content = response_content.strip()
        
        # Parsear JSON
        manual_json = json.loads(response_content)
        
        return manual_json
        
    except json.JSONDecodeError as e:
        raise Exception(f"Error al parsear JSON de Groq: {str(e)}")
    except Exception as e:
        raise Exception(f"Error al generar manual con Groq: {str(e)}")




@observe(name="generate_content_with_rag")
async def generate_content_with_rag(
    content_type: str,
    user_prompt: str,
    rag_context: str,
    brand_name: str
) -> str:
    """
    Genera contenido usando contexto RAG
    
    Args:
        content_type: product_description, video_script, image_prompt
        user_prompt: Solicitud del usuario
        rag_context: Contexto recuperado del manual vía RAG
        brand_name: Nombre de la marca
    
    Returns:
        str: Contenido generado
    """
    
    # Prompts específicos por tipo - Generación automática según el manual
    prompts_map = {
        "product_description": f"""Eres un copywriter experto especializado en {brand_name}.

Tu tarea es crear una DESCRIPCIÓN DE PRODUCTO persuasiva y profesional.

CONTEXTO DEL MANUAL DE MARCA:
{rag_context}

INSTRUCCIONES:
1. Analiza las reglas del manual (tono, palabras prohibidas, estilo)
2. Si el manual dice "prohibido usar tecnicismos", NO uses tecnicismos
3. Respeta las palabras permitidas y evita las prohibidas
4. Usa el tono especificado en el manual
5. Crea una descripción de 80-120 palabras
6. Destaca beneficios clave del producto

{"CONTEXTO ADICIONAL: " + user_prompt if user_prompt else ""}

GENERA LA DESCRIPCIÓN:""",

        "video_script": f"""Eres un guionista experto especializado en contenido de marca para {brand_name}.

Tu tarea es crear un GUION DE VIDEO de 30-45 segundos.

CONTEXTO DEL MANUAL DE MARCA:
{rag_context}

INSTRUCCIONES:
1. Analiza el tono de comunicación del manual
2. Identifica los mensajes clave y público objetivo
3. Crea un guion con estructura:
   - GANCHO (3-5 segundos): Captura atención
   - DESARROLLO (20-30 segundos): Presenta el producto/mensaje
   - CIERRE (5-8 segundos): Call to action
4. Respeta el tono y estilo del manual
5. Usa lenguaje apropiado para el público objetivo

{"CONTEXTO ADICIONAL: " + user_prompt if user_prompt else ""}

GENERA EL GUION:""",

        "image_prompt": f"""Eres un experto en prompts para IA generativa (DALL-E, Midjourney, Stable Diffusion, Imagen 3, Nano Banana).

Tu tarea es crear un PROMPT ULTRA DETALLADO Y ESPECÍFICO para generar una imagen promocional de {brand_name} que cumpla AL 100% con el manual de marca.

CONTEXTO DEL MANUAL DE MARCA:
{rag_context}

INSTRUCCIONES CRÍTICAS - CADA DETALLE ES OBLIGATORIO:

**1. COLORES (OBLIGATORIO - USA CÓDIGOS HEX SI ESTÁN DISPONIBLES)**:
   - Extrae los colores PRINCIPALES del manual
   - Extrae los colores SECUNDARIOS del manual
   - Especifica DÓNDE usar cada color en la composición
   - Formato: "usa el color principal [nombre] (código HEX si está disponible) para [elemento específico]"
   - Ejemplo: "usa el color principal verde vibrante #34C759 como fondo base de la imagen"

**2. LOGO (CRÍTICO - POSICIÓN Y TAMAÑO EXACTOS)**:
   - Identifica el TAMAÑO MÍNIMO especificado en el manual
   - Identifica las POSICIONES PERMITIDAS del logo
   - Identifica el ESPACIADO requerido
   - Especifica EN QUÉ POSICIÓN EXACTA debe ir
   - Formato: "coloca el logotipo de {brand_name} en la [posición específica del manual], con un tamaño de [porcentaje/medida] del ancho de la imagen, rodeado de un espaciado [porcentaje] para que resalte"
   - Ejemplo: "coloca el logotipo de Quinua Crunch en la esquina superior izquierda, con un tamaño del 10% del ancho de la imagen, con un espaciado blanco del 5% alrededor"

**3. COMPOSICIÓN VISUAL (USA TEXTUALMENTE LO DEL MANUAL)**:
   - Si el manual tiene "composicion_visual", cópiala TEXTUALMENTE
   - Si no, construye una basada en el estilo fotográfico
   - Especifica: qué va en el centro, qué va alrededor, qué va en el fondo
   - Ejemplo: "composición minimalista con el producto centrado, ingredientes visibles alrededor, fondo limpio y simple"

**4. ESTILO FOTOGRÁFICO (DETALLA CADA ASPECTO)**:
   - Iluminación: (natural/artificial, cálida/fría, suave/dura)
   - Ángulo: (cenital, frontal, lateral, 45°)
   - Distancia: (close-up, plano medio, plano general)
   - Mood/atmósfera: (alegre, profesional, fresco, dinámico)
   - Filtros/efectos: si el manual los menciona
   - Ejemplo: "usa iluminación natural cálida desde arriba, toma en plano cercano que muestre los detalles, atmósfera alegre y colorida"

**5. ELEMENTOS OBLIGATORIOS (MENCIONA CADA UNO EXPLÍCITAMENTE)**:
   - Lee la lista de "elementos_obligatorios" del manual
   - INCLUYE CADA UNO en el prompt
   - Ejemplo: "incluye el logo visible, el nombre del producto 'Quinua Crunch' legible, y los ingredientes principales (quinua, frutas) visibles en la imagen"

**6. ELEMENTOS PROHIBIDOS (NUNCA LOS MENCIONES)**:
   - Lee "elementos_prohibidos"
   - NO los menciones en el prompt
   - Si el usuario pide algo prohibido, ignóralo

**7. TIPOGRAFÍA (SI HAY TEXTO EN LA IMAGEN)**:
   - Identifica la tipografía principal del manual
   - Especifica qué estilo de texto usar
   - Ejemplo: "usa una tipografía sans-serif moderna similar a Open Sans para cualquier texto"

**8. FONDOS (ESPECIFICA EL FONDO PERMITIDO)**:
   - Identifica fondos permitidos
   - Identifica fondos prohibidos
   - Usa explícitamente uno permitido
   - Ejemplo: "usa un fondo blanco limpio o gris muy claro"

**CONTEXTO ADICIONAL**: {user_prompt if user_prompt else "Ninguno proporcionado"}

**FORMATO DEL PROMPT FINAL**:
- Debe ser una descripción FLUIDA y NARRATIVA (NO una lista de bullets)
- 250-350 palabras
- Estilo: "Crea una imagen [descripción fluida integrando todos los elementos]..."
- Menciona TODOS los puntos críticos integrados en la narrativa

**EJEMPLO DE PROMPT BIEN HECHO**:
❌ MALO (lista): "Logo arriba. Colores: verde #34C759. Fondo blanco. Producto centrado."

✅ BUENO (narrativa): "Crea una imagen publicitaria vibrante y saludable de Quinua Crunch. Usa un fondo blanco limpio que transmita pureza y salud. En el centro de la composición, coloca un bol de cerámica blanca lleno de Quinua Crunch, mostrando claramente los granos de quinua crujientes mezclados con frutas frescas como fresas y arándanos. El color principal de la marca, verde vibrante #34C759, debe estar presente en elementos como hojas decorativas o en el tono de algunos ingredientes. Los colores secundarios, un verde más suave #8BC34A y un amarillo cálido #FFC107, deben aparecer en las frutas y detalles visuales. Coloca el logotipo de Quinua Crunch en la esquina superior izquierda de la imagen, con un tamaño del 10% del ancho total, asegurando un espaciado blanco del 5% alrededor del logo para que destaque claramente. Incluye el nombre del producto 'Quinua Crunch' en una tipografía moderna sans-serif similar a Open Sans, colocada cerca del producto. Alrededor del bol, distribuye ingredientes principales como quinua orgánica, frutas frescas y nueces de forma natural y apetitosa. Usa iluminación natural cálida que venga desde la parte superior izquierda, creando un ambiente fresco y saludable. La composición debe ser minimalista pero atractiva, con alto contraste para que el producto sea el foco principal. El mood debe ser alegre, inspirador y transmitir energía positiva, conectando con el estilo de vida saludable del público objetivo Gen Z y Millennials."

AHORA GENERA EL PROMPT COMPLETO EN ESPAÑOL (250-350 palabras, narrativa fluida):"""
    }
    
    prompt = prompts_map.get(content_type, prompts_map["product_description"])
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=MODEL_NAME,
            temperature=0.7,
            max_tokens=1500
        )
        
        return chat_completion.choices[0].message.content.strip()
        
    except Exception as e:
        raise Exception(f"Error generando contenido: {str(e)}")