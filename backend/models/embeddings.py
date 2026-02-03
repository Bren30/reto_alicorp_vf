from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID

class EmbeddingCreate(BaseModel):
    """
    Modelo para crear un embedding
    """
    manual_id: UUID
    content: str
    section: str
    embedding: List[float]

class SearchQuery(BaseModel):
    """
    Modelo para búsqueda semántica
    """
    query: str = Field(..., description="Pregunta o consulta sobre el manual")
    manual_id: str = Field(..., description="ID del manual a consultar")
    top_k: int = Field(default=3, description="Número de resultados")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "¿Puedo usar tecnicismos en las descripciones?",
                "manual_id": "uuid-del-manual",
                "top_k": 3
            }
        }

class SearchResult(BaseModel):
    """
    Modelo de resultado de búsqueda
    """
    id: UUID
    manual_id: UUID
    content: str
    section: str
    similarity: float