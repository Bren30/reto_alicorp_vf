from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID

class ApprovalRequest(BaseModel):
    """Request para aprobar/rechazar contenido"""
    status: str  # "approved" o "rejected"
    
class AuditResult(BaseModel):
    """Resultado de auditoría multimodal"""
    content_id: Optional[UUID] = None
    manual_id: Optional[str] = None
    manual_name: Optional[str] = None
    compliant: bool
    score: float
    issues: List[str]
    recommendations: List[str]
    analysis: str
    message: str