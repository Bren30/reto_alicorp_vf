from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from datetime import datetime
from typing import List
import os
from pydantic import BaseModel

# Importar configuración de base de datos
from config.database import get_supabase_client, check_database_connection
from services.groq_service import generate_brand_manual
from models.brand_manual import (
    BrandManualCreate, 
    BrandManualResponse,
    BrandManualGenerateRequest,
    BrandManualGenerateResponse
)
from services.embeddings_service import (
    process_manual_for_rag,
    search_similar_content
)
from models.embeddings import SearchQuery, SearchResult
from services.groq_service import generate_content_with_rag
from fastapi import UploadFile, File,Form
from services.gemini_service import audit_image_against_brand_manual, test_gemini_connection
from models.governance import ApprovalRequest, AuditResult

# Cargar variables de entorno
load_dotenv()

# Crear instancia de FastAPI
app = FastAPI(
    title="Content Suite - Alicorp",
    description="API para generación de contenido con IA",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cliente de Supabase
supabase = get_supabase_client()


# ============================================
# NUEVOS ENDPOINTS DE FASE 2 (Base de Datos)
# ============================================

@app.get("/database/status")
async def database_status():
    """
    Verifica el estado de la conexión a la base de datos
    """
    status = await check_database_connection()
    return status

@app.post("/brand-manuals", response_model=BrandManualResponse, status_code=201)
async def create_brand_manual(manual: BrandManualCreate):
    """
    Crea un nuevo manual de marca en la base de datos
    """
    try:
        # Preparar datos para insertar
        manual_data = {
            "name": manual.name,
            "description": manual.description,
            "product_type": manual.product_type,
            "tone": manual.tone,
            "target_audience": manual.target_audience,
            "full_manual": None,  # Se llenará en Fase 3 con IA
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Insertar en Supabase
        result = supabase.table("brand_manuals").insert(manual_data).execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Error al crear el manual")
        
        return result.data[0]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/brand-manuals", response_model=list[BrandManualResponse])
async def get_all_brand_manuals():
    """
    Obtiene todos los manuales de marca
    """
    try:
        result = supabase.table("brand_manuals").select("*").order("created_at", desc=True).execute()
        return result.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/brand-manuals/{manual_id}", response_model=BrandManualResponse)
async def get_brand_manual(manual_id: str):
    """
    Obtiene un manual de marca específico por ID
    """
    try:
        result = supabase.table("brand_manuals").select("*").eq("id", manual_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Manual no encontrado")
        
        return result.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.delete("/brand-manuals/{manual_id}")
async def delete_brand_manual(manual_id: str):
    """
    Elimina un manual de marca
    """
    try:
        result = supabase.table("brand_manuals").delete().eq("id", manual_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Manual no encontrado")
        
        return {"message": "Manual eliminado correctamente", "id": manual_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    



@app.post("/brand-manuals/generate", response_model=BrandManualGenerateResponse, status_code=201)
async def generate_brand_manual_with_ai(request: BrandManualGenerateRequest):
    """
    Genera un manual de marca completo usando IA (Groq + Llama 3)
    y lo guarda en la base de datos
    
    Este es el MÓDULO I: Brand DNA Architect
    """
    try:
        # 1. Generar el manual con IA
        full_manual = await generate_brand_manual(
            name=request.name,
            description=request.description,
            product_type=request.product_type,
            tone=request.tone,
            target_audience=request.target_audience
        )
        
        # 2. Preparar datos para guardar en DB
        manual_data = {
            "name": request.name,
            "description": request.description,
            "product_type": request.product_type,
            "tone": request.tone,
            "target_audience": request.target_audience,
            "full_manual": full_manual,  # ← El JSON generado por IA
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # 3. Guardar en Supabase
        result = supabase.table("brand_manuals").insert(manual_data).execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Error al guardar el manual generado")
        
        # 4. Preparar respuesta
        saved_manual = result.data[0]
        
        return {
            **saved_manual,
            "message": "Manual de marca generado exitosamente con IA"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error al generar manual: {str(e)}"
        )


@app.post("/brand-manuals/{manual_id}/generate-embeddings")
async def generate_embeddings_for_manual(manual_id: str):
    """
    Genera embeddings para un manual de marca existente
    y los guarda en la base de datos vectorial
    
    Este paso es CRÍTICO para habilitar RAG
    """
    try:
        # 1. Obtener el manual de la base de datos
        result = supabase.table("brand_manuals").select("*").eq("id", manual_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Manual no encontrado")
        
        manual = result.data[0]
        
        # Verificar que tenga el manual completo generado
        if not manual.get("full_manual"):
            raise HTTPException(
                status_code=400,
                detail="Este manual no tiene contenido generado. Usa /brand-manuals/generate primero."
            )
        
        # 2. Procesar el manual y generar embeddings
        embeddings_data = await process_manual_for_rag(
            manual_id=manual_id,
            manual_data=manual["full_manual"]
        )
        
        # 3. Primero eliminar embeddings existentes (si hay)
        supabase.table("brand_manual_embeddings").delete().eq("manual_id", manual_id).execute()
        
        # 4. Guardar los nuevos embeddings en la base de datos
        result = supabase.table("brand_manual_embeddings").insert(embeddings_data).execute()
        
        return {
            "message": "Embeddings generados exitosamente",
            "manual_id": manual_id,
            "chunks_created": len(embeddings_data),
            "sections": [chunk["section"] for chunk in embeddings_data]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/brand-manuals/search", response_model=List[SearchResult])
async def search_brand_manual(search: SearchQuery):
    """
    Búsqueda semántica en un manual de marca
    
    Permite hacer preguntas en lenguaje natural sobre el manual
    y obtiene las secciones más relevantes
    
    Ejemplos de queries:
    - "¿Qué palabras están prohibidas?"
    - "¿Cuál es el tono de comunicación?"
    - "¿Puedo usar tecnicismos?"
    - "¿Qué colores debo usar?"
    """
    try:
        # Realizar búsqueda semántica
        results = await search_similar_content(
            query=search.query,
            manual_id=search.manual_id,
            supabase_client=supabase,
            top_k=search.top_k
        )
        
        if not results:
            return []
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en búsqueda: {str(e)}")

@app.get("/brand-manuals/{manual_id}/embeddings/status")
async def check_embeddings_status(manual_id: str):
    """
    Verifica si un manual tiene embeddings generados
    """
    try:
        result = supabase.table("brand_manual_embeddings")\
            .select("id, section")\
            .eq("manual_id", manual_id)\
            .execute()
        
        has_embeddings = len(result.data) > 0
        
        return {
            "manual_id": manual_id,
            "has_embeddings": has_embeddings,
            "chunks_count": len(result.data),
            "sections": [item["section"] for item in result.data] if has_embeddings else []
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    




class ContentGenerateRequest(BaseModel):
    manual_id: str
    content_type: str  # "product_description", "video_script", "image_prompt"
    additional_context: str = ""  # Opcional: contexto adicional del usuario


@app.post("/content/generate")
async def generate_content(request: ContentGenerateRequest):
    """Módulo II: Creative Engine"""
    try:
        # 1. Validar tipo
        valid_types = ["product_description", "video_script", "image_prompt"]
        if request.content_type not in valid_types:
            raise HTTPException(status_code=400, detail=f"Tipo inválido. Use: {valid_types}")
        
        # 2. Obtener manual
        manual_result = supabase.table("brand_manuals")\
            .select("*")\
            .eq("id", request.manual_id)\
            .execute()
        
        if not manual_result.data:
            raise HTTPException(status_code=404, detail="Manual no encontrado")
        
        manual = manual_result.data[0]
        
        # 3. Verificar que tenga full_manual generado
        if not manual.get("full_manual"):
            raise HTTPException(
                status_code=400,
                detail="Este manual no tiene contenido generado por IA"
            )
        
        # 4. Verificar embeddings
        embeddings_check = supabase.table("brand_manual_embeddings")\
            .select("id")\
            .eq("manual_id", request.manual_id)\
            .execute()
        
        if not embeddings_check.data:
            raise HTTPException(
                status_code=400,
                detail=f"Este manual no tiene embeddings. Ejecuta: POST /brand-manuals/{request.manual_id}/generate-embeddings"
            )
        
        # 5. Consultar RAG - Preguntas naturales para encontrar reglas del manual
        # El modelo de embeddings entiende mejor lenguaje natural que keywords
        rag_queries = {
            "product_description": "¿Cuál es el tono de comunicación para descripciones? ¿Hay palabras prohibidas? ¿Puedo usar tecnicismos? ¿Qué estilo de redacción debo usar?",
            "video_script": "¿Qué tono usar en videos? ¿Cuáles son los mensajes clave? ¿Quién es el público objetivo? ¿Cómo estructurar el contenido?",
            "image_prompt": "¿Qué colores principales y secundarios usar exactamente? ¿Cuál es el estilo fotográfico detallado? ¿Qué elementos son obligatorios y cuáles prohibidos? ¿Cómo usar el logo: tamaño mínimo, espaciado, posición? ¿Qué fondos están permitidos y prohibidos? ¿Hay reglas de composición visual? ¿Qué tipografía usar?"
        }
        
        rag_results = await search_similar_content(
            query=rag_queries[request.content_type],
            manual_id=request.manual_id,
            supabase_client=supabase,
            top_k=5  # Aumentado de 3 a 5 para más contexto en image_prompt
        )
        
        if not rag_results:
            raise HTTPException(
                status_code=500,
                detail="No se pudo recuperar contexto del manual"
            )
        
        # 6. Formatear contexto
        rag_context = "\n\n".join([
            f"[SECCIÓN: {r['section']}]\n{r['content']}"
            for r in rag_results
        ])
        
        # 7. Generar contenido automáticamente basado en el tipo seleccionado
        generated = await generate_content_with_rag(
            content_type=request.content_type,
            user_prompt=request.additional_context if request.additional_context else "",
            rag_context=rag_context,
            brand_name=manual["name"]
        )
        
        # 8. Guardar
        content_data = {
            "manual_id": request.manual_id,
            "content_type": request.content_type,
            "user_prompt": request.additional_context if request.additional_context else f"Generación automática de {request.content_type}",
            "generated_text": generated,
            "status": "pending"
        }
        
        result = supabase.table("generated_content").insert(content_data).execute()
        
        return {
            "id": result.data[0]["id"],
            "content_type": request.content_type,
            "generated_text": generated,
            "rag_context_used": rag_results,
            "status": "pending",
            "message": "Contenido generado basado en el manual de IA"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")






# Endpoint auxiliar para listar contenido (útil para frontend)
@app.get("/content/list")
async def list_content(manual_id: str = None):
    """Lista contenido generado (opcionalmente filtrado por manual)"""
    try:
        query = supabase.table("generated_content").select("*")
        if manual_id:
            query = query.eq("manual_id", manual_id)
        
        result = query.order("created_at", desc=True).execute()
        return result.data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")



@app.post("/content/{content_id}/approve")
async def approve_content(content_id: str):
    """
    Aprueba un contenido (cambia status a 'approved')
    """
    try:
        # Verificar que existe
        check = supabase.table("generated_content")\
            .select("id, status")\
            .eq("id", content_id)\
            .execute()
        
        if not check.data:
            raise HTTPException(status_code=404, detail="Contenido no encontrado")
        
        # Actualizar status
        result = supabase.table("generated_content")\
            .update({"status": "approved"})\
            .eq("id", content_id)\
            .execute()
        
        return {
            "id": content_id,
            "status": "approved",
            "message": "Contenido aprobado exitosamente"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.post("/content/{content_id}/reject")
async def reject_content(content_id: str):
    """
    Rechaza un contenido (cambia status a 'rejected')
    """
    try:
        # Verificar que existe
        check = supabase.table("generated_content")\
            .select("id, status")\
            .eq("id", content_id)\
            .execute()
        
        if not check.data:
            raise HTTPException(status_code=404, detail="Contenido no encontrado")
        
        # Actualizar status
        result = supabase.table("generated_content")\
            .update({"status": "rejected"})\
            .eq("id", content_id)\
            .execute()
        
        return {
            "id": content_id,
            "status": "rejected",
            "message": "Contenido rechazado"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# --- PARTE B: AUDITORÍA MULTIMODAL (CORREGIDO) ---

@app.get("/gemini/status")
async def gemini_status():
    """Verifica conexión con Google Gemini"""
    status = await test_gemini_connection()
    return status


@app.post("/audit/image", response_model=AuditResult)
async def audit_image_against_manual(
    manual_id: str = Form(...),
    image: UploadFile = File(...)
):
    """
    MÓDULO III - Parte B: Auditoría Multimodal
    
    El Aprobador B sube una imagen y el sistema la audita 
    contra el manual de marca (Módulo I).
    
    Args:
        manual_id: UUID del manual de marca a usar como referencia
        image: Archivo de imagen a auditar
    
    Returns:
        - compliant: true/false si cumple con el manual
        - score: 0-100 puntuación de cumplimiento
        - issues: Lista de problemas encontrados
        - recommendations: Recomendaciones para mejorar
        - analysis: Análisis detallado de la imagen
    """
    try:
        # 1. Obtener el manual de marca
        manual_result = supabase.table("brand_manuals")\
            .select("*")\
            .eq("id", manual_id)\
            .execute()
        
        if not manual_result.data:
            raise HTTPException(status_code=404, detail="Manual no encontrado")
        
        manual = manual_result.data[0]
        
        # 2. Verificar que tenga full_manual generado
        if not manual.get("full_manual"):
            raise HTTPException(
                status_code=400,
                detail="Este manual no tiene contenido generado por IA. Ejecuta POST /brand-manuals/generate primero"
            )
        
        # 3. Validar que sea imagen
        if not image.content_type or not image.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail=f"El archivo debe ser una imagen. Tipo recibido: {image.content_type}"
            )
        
        # 4. Leer imagen
        image_bytes = await image.read()
        
        # 5. Auditar imagen VS manual de marca con Gemini Vision
        audit_result = await audit_image_against_brand_manual(
            image_bytes=image_bytes,
            manual_content=manual["full_manual"],
            brand_name=manual["name"]
        )
        
        # 6. Retornar resultado
        return {
            "content_id": None,  # No está vinculado a contenido generado
            "manual_id": manual_id,
            "manual_name": manual["name"],
            **audit_result,
            "message": "✅ Auditoría completada" if audit_result["compliant"] else "❌ La imagen no cumple con el manual"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en auditoría: {str(e)}")


# Ejecutar con: uvicorn main:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)