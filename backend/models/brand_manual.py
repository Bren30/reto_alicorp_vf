from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID

class BrandManualCreate(BaseModel):
    """
    Modelo para crear un manual de marca
    """
    name: str = Field(..., description="Nombre del producto/marca")
    description: Optional[str] = Field(None, description="Descripción breve")
    product_type: str = Field(..., description="Tipo de producto (ej: snack, bebida)")
    tone: str = Field(..., description="Tono de comunicación (ej: profesional, divertido)")
    target_audience: str = Field(..., description="Público objetivo (ej: Gen Z, millennials)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Quinua Crunch",
                "description": "Snack saludable de quinua",
                "product_type": "snack",
                "tone": "divertido pero profesional",
                "target_audience": "Gen Z"
            }
        }

class BrandManualResponse(BaseModel):
    """
    Modelo de respuesta de un manual de marca
    """
    id: UUID
    name: str
    description: Optional[str]
    product_type: str
    tone: str
    target_audience: str
    full_manual: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ===== NUEVOS MODELOS PARA GENERACIÓN CON IA =====

class BrandManualGenerateRequest(BaseModel):
    """
    Modelo para solicitar la generación de un manual con IA
    """
    name: str = Field(..., description="Nombre del producto/marca")
    description: str = Field(..., description="Descripción del producto")
    product_type: str = Field(..., description="Tipo de producto")
    tone: str = Field(..., description="Tono de comunicación deseado")
    target_audience: str = Field(..., description="Público objetivo")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Quinua Crunch",
                "description": "Snack saludable hecho con quinua orgánica peruana, alto en proteínas y fibra",
                "product_type": "snack saludable",
                "tone": "divertido, cercano pero profesional",
                "target_audience": "Gen Z y Millennials health-conscious"
            }
        }

class BrandManualGenerateResponse(BaseModel):
    """
    Modelo de respuesta después de generar un manual con IA
    """
    id: UUID
    name: str
    description: str
    product_type: str
    tone: str
    target_audience: str
    full_manual: Dict[str, Any]
    created_at: datetime
    message: str = "Manual de marca generado exitosamente"
    
    class Config:
        from_attributes = True