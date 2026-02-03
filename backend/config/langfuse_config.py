from langfuse import Langfuse
from dotenv import load_dotenv
import os

load_dotenv()

# Inicializar Langfuse
try:
    langfuse = Langfuse(
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
        secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
        host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com"),
        enabled=bool(os.getenv("LANGFUSE_PUBLIC_KEY"))  # Solo habilitar si hay clave
    )
except Exception as e:
    print(f"Warning: Langfuse no pudo inicializarse: {e}")
    langfuse = None

def get_langfuse_client():
    """Retorna el cliente de Langfuse configurado"""
    return langfuse