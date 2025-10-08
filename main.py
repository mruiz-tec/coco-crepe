from fastapi import FastAPI
from app.routes.proyecciones import router as proyecciones_router
from mangum import Mangum
from config import create_table_if_not_exists
import os

# Cargar variables de entorno si existe archivo .env
from dotenv import load_dotenv
load_dotenv()

app = FastAPI(
    title="API de Proyección de Insumos",
    description="API para gestionar proyecciones de demanda de insumos en tiendas",
    version="1.0.0"
)

# Incluir routers
app.include_router(proyecciones_router)

# Evento de inicio: crear tabla si no existe (solo en desarrollo)
@app.on_event("startup")
async def startup_event():
    # Solo crear tabla automáticamente en desarrollo
    if os.getenv("ENVIRONMENT") == "development":
        create_table_if_not_exists()

# Handler para AWS Lambda
handler = Mangum(app)


@app.get("/", tags=["health"])
def health_check():
    """Endpoint de verificación de salud"""
    return {
        "status": "healthy",
        "service": "API de Proyección de Insumos",
        "version": "1.0.0"
    }