from fastapi import APIRouter, HTTPException
from typing import List
from model import ProyeccionInsumo
from dynamodb_service import DynamoDBService
from datetime import date
from decimal import Decimal

router = APIRouter(
    prefix="/proyecciones",
    tags=["proyecciones"],
    responses={404: {"description": "Proyección no encontrada"}},
)


@router.post("/registrar", response_model=ProyeccionInsumo, summary="Registrar proyección")
def crear_proyeccion(proyeccion: ProyeccionInsumo):
    """
    Registra una nueva proyección de insumos en DynamoDB.
    """
    try:
        return DynamoDBService.crear_proyeccion(proyeccion)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/listar", response_model=List[ProyeccionInsumo], summary="Listar todas las proyecciones")
def listar_proyecciones():
    """
    Lista todas las proyecciones almacenadas en DynamoDB.
    """
    try:
        proyecciones = DynamoDBService.listar_todas()
        return proyecciones
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/listar/{tienda_id}", response_model=List[ProyeccionInsumo], summary="Obtener proyecciones por tienda")
def obtener_por_tienda(tienda_id: str):
    """
    Obtiene todas las proyecciones de una tienda específica.
    """
    try:
        resultado = DynamoDBService.obtener_por_tienda(tienda_id)
        if not resultado:
            raise HTTPException(status_code=404, detail="No se encontraron proyecciones para esa tienda")
        return resultado
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/semana/{semana}", response_model=List[ProyeccionInsumo], summary="Obtener proyecciones por semana")
def obtener_por_semana(semana: str):
    """
    Obtiene todas las proyecciones de una semana específica.
    Ejemplo: semana = "2025-W41"
    """
    try:
        resultado = DynamoDBService.obtener_por_semana(semana)
        if not resultado:
            raise HTTPException(status_code=404, detail="No se encontraron proyecciones para esa semana")
        return resultado
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/categoria/{categoria}", response_model=List[ProyeccionInsumo], summary="Obtener proyecciones por categoría")
def obtener_por_categoria(categoria: str):
    """
    Obtiene todas las proyecciones de una categoría específica.
    Ejemplo: categoria = "crepas"
    """
    try:
        resultado = DynamoDBService.obtener_por_categoria(categoria)
        if not resultado:
            raise HTTPException(status_code=404, detail="No se encontraron proyecciones para esa categoría")
        return resultado
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/eliminar/{tienda_id}/{semana}", summary="Eliminar proyecciones por tienda y semana")
def eliminar_proyeccion(tienda_id: str, semana: str):
    """
    Elimina todas las proyecciones de una tienda en una semana específica.
    """
    try:
        deleted_count = DynamoDBService.eliminar_por_tienda_y_semana(tienda_id, semana)
        if deleted_count == 0:
            raise HTTPException(status_code=404, detail="No se encontró la proyección para eliminar")
        return {"mensaje": f"{deleted_count} proyección(es) eliminada(s)"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/actualizar", response_model=ProyeccionInsumo, summary="Actualizar proyección")
def actualizar_proyeccion(proyeccion: ProyeccionInsumo):
    """
    Actualiza una proyección existente en DynamoDB.
    """
    try:
        return DynamoDBService.actualizar_proyeccion(proyeccion)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generar", response_model=List[ProyeccionInsumo], summary="Generar proyecciones automáticamente")
def generar_proyecciones():
    """
    Genera proyecciones automáticamente para todas las tiendas y categorías.
    Ejemplo de cómo integrar con el modelo de ML.
    """
    try:
        # Aquí integrar consumo promedio o modelo de ML
        tiendas = [
            {"id": "T001", "nombre": "Salón Surco Central"}, 
            {"id": "T002", "nombre": "Salón Miraflores"}
        ]
        categorias = ["crepas", "waffles"]
        semana = "2025-W41"

        nuevas = []
        for tienda in tiendas:
            for categoria in categorias:
                proyeccion = ProyeccionInsumo(
                    fecha_proyeccion=date.fromisoformat("2025-10-05"),
                    tienda_id=tienda["id"],
                    nombre_tienda=tienda["nombre"],
                    categoria_insumo=categoria,
                    unidad_medida="Base de crepe" if categoria == "crepas" else "Base de waffle",
                    cantidad_estimada=Decimal("12.50"),
                    semana=semana,
                    origen_modelo="Promedio_Historico_v1",
                    fecha_generacion=date.today(),
                    estado_proyeccion="pendiente",
                    cantidad_despachada=Decimal("11.00"),
                    cantidad_consumida_real=Decimal("11.80"),
                    diferencia_vs_real=Decimal("0.70"),
                    usuario_ajuste="sistema_autajuste",
                    fecha_confirmacion=date.fromisoformat("2025-10-06"),
                    observaciones="Generado automáticamente"
                )
                DynamoDBService.crear_proyeccion(proyeccion)
                nuevas.append(proyeccion)
        
        return nuevas
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))