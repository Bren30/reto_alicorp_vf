from supabase import create_client, Client
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

# Obtener credenciales
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Validar que existan las credenciales
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Faltan credenciales de Supabase en el archivo .env")

# Crear cliente de Supabase (singleton)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_supabase_client() -> Client:
    """
    Retorna el cliente de Supabase configurado
    """
    return supabase

# Función helper para verificar conexión
async def check_database_connection():
    """
    Verifica que la conexión a Supabase funcione
    """
    try:
        # Intenta hacer una query simple
        result = supabase.table("brand_manuals").select("count").execute()
        return {"status": "connected", "database": "supabase"}
    except Exception as e:
        return {"status": "error", "message": str(e)}