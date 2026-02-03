import numpy as np
from typing import List, Dict, Any
import json
from langfuse import observe

# Lazy loading del modelo para evitar problemas de carga lenta en Windows
# En producción (Linux/EC2) esto cargará normalmente
_embeddings_model = None

def _get_embeddings_model():
    """
    Carga el modelo de embeddings de forma lazy (solo cuando se necesita)
    """
    global _embeddings_model
    if _embeddings_model is None:
        from sentence_transformers import SentenceTransformer
        # Usamos 'all-MiniLM-L6-v2': ligero, rápido y efectivo
        # Genera vectores de 384 dimensiones
        _embeddings_model = SentenceTransformer('all-MiniLM-L6-v2')
    return _embeddings_model

def get_embedding_dimension() -> int:
    """
    Retorna la dimensión de los embeddings del modelo
    """
    return 384  # Dimensión de all-MiniLM-L6-v2

async def generate_embedding(text: str) -> List[float]:
    """
    Genera un embedding (vector) para un texto dado
    
    Args:
        text: Texto a convertir en embedding
    
    Returns:
        List[float]: Vector de 384 dimensiones
    """
    try:
        # Obtener modelo (carga lazy)
        model = _get_embeddings_model()
        # Generar embedding
        embedding = model.encode(text, convert_to_numpy=True)
        
        # Convertir numpy array a lista de floats
        return embedding.tolist()
        
    except Exception as e:
        raise Exception(f"Error al generar embedding: {str(e)}")

async def chunk_manual_content(manual: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Divide el manual de marca en chunks (fragmentos) semánticos
    
    Estrategia: Cada sección importante del manual es un chunk separado
    Esto permite búsquedas más precisas por contexto
    
    Args:
        manual: El JSON completo del manual de marca
    
    Returns:
        List[Dict]: Lista de chunks con su contenido y metadata
    """
    chunks = []
    
    try:
        # Chunk 1: Identidad de Marca (completa)
        if "identidad_marca" in manual:
            identidad = manual["identidad_marca"]
            content = f"""
IDENTIDAD DE MARCA:
Propósito: {identidad.get('proposito', '')}
Valores: {', '.join(identidad.get('valores', []))}
Personalidad: {identidad.get('personalidad', '')}
Diferenciador: {identidad.get('diferenciador', '')}
"""
            chunks.append({
                "section": "identidad_marca",
                "content": content.strip()
            })
        
        # Chunk 2: Tono de Comunicación (completo)
        if "tono_comunicacion" in manual:
            tono = manual["tono_comunicacion"]
            content = f"""
TONO DE COMUNICACIÓN:
Descripción: {tono.get('descripcion_general', '')}
Estilo: {tono.get('estilo_redaccion', '')}
Uso de tecnicismos: {'Permitido' if tono.get('uso_tecnicismos') else 'Prohibido'}

Palabras permitidas: {', '.join(tono.get('palabras_permitidas', []))}
Palabras prohibidas: {', '.join(tono.get('palabras_prohibidas', []))}

Ejemplos buenos:
{chr(10).join('- ' + ej for ej in tono.get('ejemplos_buenos', []))}

Ejemplos malos:
{chr(10).join('- ' + ej for ej in tono.get('ejemplos_malos', []))}
"""
            chunks.append({
                "section": "tono_comunicacion",
                "content": content.strip()
            })
        
        # Chunk 3: Elementos Visuales
        if "elementos_visuales" in manual:
            visuales = manual["elementos_visuales"]
            content = f"""
ELEMENTOS VISUALES:
Colores principales: {', '.join(visuales.get('colores_principales', []))}
Colores secundarios: {', '.join(visuales.get('colores_secundarios', []))}
Tipografía principal: {visuales.get('tipografia_principal', '')}
Tipografía secundaria: {visuales.get('tipografia_secundaria', '')}
Estilo fotográfico: {visuales.get('estilo_fotografico', '')}
Iconografía: {visuales.get('iconografia', '')}

Uso del logo:
- Tamaño mínimo: {visuales.get('uso_logo', {}).get('tamano_minimo', '')}
- Espaciado: {visuales.get('uso_logo', {}).get('espaciado', '')}
- Fondos permitidos: {', '.join(visuales.get('uso_logo', {}).get('fondos_permitidos', []))}
- Fondos prohibidos: {', '.join(visuales.get('uso_logo', {}).get('fondos_prohibidos', []))}
"""
            chunks.append({
                "section": "elementos_visuales",
                "content": content.strip()
            })
        
        # Chunk 4: Público Objetivo
        if "publico_objetivo" in manual:
            publico = manual["publico_objetivo"]
            demo = publico.get('demografia', {})
            psico = publico.get('psicografia', {})
            
            content = f"""
PÚBLICO OBJETIVO:

Demografía:
- Edad: {demo.get('edad', '')}
- Género: {demo.get('genero', '')}
- Ubicación: {demo.get('ubicacion', '')}
- Nivel socioeconómico: {demo.get('nivel_socioeconomico', '')}

Psicografía:
- Intereses: {', '.join(psico.get('intereses', []))}
- Valores: {', '.join(psico.get('valores', []))}
- Estilo de vida: {psico.get('estilo_vida', '')}

Pain Points: {', '.join(publico.get('pain_points', []))}
Aspiraciones: {', '.join(publico.get('aspiraciones', []))}
"""
            chunks.append({
                "section": "publico_objetivo",
                "content": content.strip()
            })
        
        # Chunk 5: Directrices de Contenido
        if "directrices_contenido" in manual:
            directrices = manual["directrices_contenido"]
            content = f"""
DIRECTRICES DE CONTENIDO:

Palabras clave SEO: {', '.join(directrices.get('palabras_clave_seo', []))}
Mensajes clave: {', '.join(directrices.get('mensajes_clave', []))}

Tipos de contenido:
{json.dumps(directrices.get('tipos_contenido', {}), indent=2, ensure_ascii=False)}
"""
            chunks.append({
                "section": "directrices_contenido",
                "content": content.strip()
            })
        
        # Chunk 6: Ejemplos de Aplicación
        if "ejemplos_aplicacion" in manual:
            ejemplos = manual["ejemplos_aplicacion"]
            content = f"""
EJEMPLOS DE APLICACIÓN:

✅ Descripción de producto BUENA:
{ejemplos.get('descripcion_producto_buena', '')}

❌ Descripción de producto MALA:
{ejemplos.get('descripcion_producto_mala', '')}

✅ Post en redes sociales BUENO:
{ejemplos.get('post_redes_bueno', '')}

❌ Post en redes sociales MALO:
{ejemplos.get('post_redes_malo', '')}
"""
            chunks.append({
                "section": "ejemplos_aplicacion",
                "content": content.strip()
            })
        
        return chunks
        
    except Exception as e:
        raise Exception(f"Error al crear chunks del manual: {str(e)}")

@observe(name="process_manual_for_rag")
async def process_manual_for_rag(manual_id: str, manual_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Procesa un manual completo para RAG:
    1. Divide en chunks
    2. Genera embeddings para cada chunk
    3. Prepara para insertar en la base de datos
    
    Args:
        manual_id: UUID del manual en la base de datos
        manual_data: Contenido del manual (el JSON full_manual)
    
    Returns:
        List[Dict]: Lista de embeddings listos para guardar
    """
    try:
        # 1. Dividir en chunks
        chunks = await chunk_manual_content(manual_data)
        
        # 2. Generar embeddings para cada chunk
        embeddings_to_save = []
        
        for chunk in chunks:
            # Generar embedding para el contenido del chunk
            embedding_vector = await generate_embedding(chunk["content"])
            
            # Preparar para guardar en DB
            embeddings_to_save.append({
                "manual_id": manual_id,
                "content": chunk["content"],
                "section": chunk["section"],
                "embedding": embedding_vector
            })
        
        return embeddings_to_save
        
    except Exception as e:
        raise Exception(f"Error al procesar manual para RAG: {str(e)}")

@observe(name="rag_search")
async def search_similar_content(
    query: str,
    manual_id: str,
    supabase_client,
    top_k: int = 3
) -> List[Dict[str, Any]]:
    """
    Búsqueda semántica en el manual de marca
    
    Args:
        query: Pregunta o consulta del usuario
        manual_id: UUID del manual a consultar
        supabase_client: Cliente de Supabase
        top_k: Número de resultados más relevantes a retornar
    
    Returns:
        List[Dict]: Chunks más relevantes del manual
    """
    try:
        # 1. Generar embedding de la consulta
        query_embedding = await generate_embedding(query)
        
        # 2. Buscar en la base de datos usando similitud coseno
        # Nota: Supabase con pgvector usa el operador <=> para distancia coseno
        result = supabase_client.rpc(
            'match_brand_manual_embeddings',
            {
                'query_embedding': query_embedding,
                'match_manual_id': manual_id,
                'match_count': top_k
            }
        ).execute()
        
        if not result.data:
            return []
        
        return result.data
        
    except Exception as e:
        raise Exception(f"Error en búsqueda semántica: {str(e)}")