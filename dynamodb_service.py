from typing import List, Optional
from datetime import date
from decimal import Decimal
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
from model import ProyeccionInsumo
from config import table


class DynamoDBService:
    """Servicio para interactuar con DynamoDB"""
    
    @staticmethod
    def _proyeccion_to_item(proyeccion: ProyeccionInsumo) -> dict:
        """Convierte un objeto ProyeccionInsumo a formato DynamoDB"""
        return {
            'tienda_id': proyeccion.tienda_id,
            'fecha_proyeccion_semana': f"{proyeccion.fecha_proyeccion.isoformat()}#{proyeccion.semana}",
            'fecha_proyeccion': proyeccion.fecha_proyeccion.isoformat(),
            'nombre_tienda': proyeccion.nombre_tienda,
            'categoria_insumo': proyeccion.categoria_insumo,
            'unidad_medida': proyeccion.unidad_medida,
            'cantidad_estimada': str(proyeccion.cantidad_estimada),
            'semana': proyeccion.semana,
            'origen_modelo': proyeccion.origen_modelo,
            'fecha_generacion': proyeccion.fecha_generacion.isoformat(),
            'estado_proyeccion': proyeccion.estado_proyeccion,
            'cantidad_despachada': str(proyeccion.cantidad_despachada),
            'cantidad_consumida_real': str(proyeccion.cantidad_consumida_real),
            'diferencia_vs_real': str(proyeccion.diferencia_vs_real),
            'usuario_ajuste': proyeccion.usuario_ajuste,
            'fecha_confirmacion': proyeccion.fecha_confirmacion.isoformat(),
            'observaciones': proyeccion.observaciones
        }
    
    @staticmethod
    def _item_to_proyeccion(item: dict) -> ProyeccionInsumo:
        """Convierte un item de DynamoDB a objeto ProyeccionInsumo"""
        return ProyeccionInsumo(
            fecha_proyeccion=date.fromisoformat(item['fecha_proyeccion']),
            tienda_id=item['tienda_id'],
            nombre_tienda=item['nombre_tienda'],
            categoria_insumo=item['categoria_insumo'],
            unidad_medida=item['unidad_medida'],
            cantidad_estimada=Decimal(item['cantidad_estimada']),
            semana=item['semana'],
            origen_modelo=item['origen_modelo'],
            fecha_generacion=date.fromisoformat(item['fecha_generacion']),
            estado_proyeccion=item['estado_proyeccion'],
            cantidad_despachada=Decimal(item['cantidad_despachada']),
            cantidad_consumida_real=Decimal(item['cantidad_consumida_real']),
            diferencia_vs_real=Decimal(item['diferencia_vs_real']),
            usuario_ajuste=item['usuario_ajuste'],
            fecha_confirmacion=date.fromisoformat(item['fecha_confirmacion']),
            observaciones=item.get('observaciones')
        )
    
    @staticmethod
    def crear_proyeccion(proyeccion: ProyeccionInsumo) -> ProyeccionInsumo:
        """Crea una nueva proyección en DynamoDB"""
        try:
            item = DynamoDBService._proyeccion_to_item(proyeccion)
            table.put_item(Item=item)
            return proyeccion
        except ClientError as e:
            raise Exception(f"Error al crear proyección: {e.response['Error']['Message']}")
    
    @staticmethod
    def listar_todas() -> List[ProyeccionInsumo]:
        """Lista todas las proyecciones"""
        try:
            response = table.scan()
            items = response.get('Items', [])
            
            # Manejar paginación si hay muchos items
            while 'LastEvaluatedKey' in response:
                response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                items.extend(response.get('Items', []))
            
            return [DynamoDBService._item_to_proyeccion(item) for item in items]
        except ClientError as e:
            raise Exception(f"Error al listar proyecciones: {e.response['Error']['Message']}")
    
    @staticmethod
    def obtener_por_tienda(tienda_id: str) -> List[ProyeccionInsumo]:
        """Obtiene todas las proyecciones de una tienda específica"""
        try:
            response = table.query(
                KeyConditionExpression=Key('tienda_id').eq(tienda_id)
            )
            items = response.get('Items', [])
            
            # Manejar paginación
            while 'LastEvaluatedKey' in response:
                response = table.query(
                    KeyConditionExpression=Key('tienda_id').eq(tienda_id),
                    ExclusiveStartKey=response['LastEvaluatedKey']
                )
                items.extend(response.get('Items', []))
            
            return [DynamoDBService._item_to_proyeccion(item) for item in items]
        except ClientError as e:
            raise Exception(f"Error al obtener proyecciones por tienda: {e.response['Error']['Message']}")
    
    @staticmethod
    def obtener_por_semana(semana: str) -> List[ProyeccionInsumo]:
        """Obtiene todas las proyecciones de una semana específica usando GSI"""
        try:
            response = table.query(
                IndexName='semana-index',
                KeyConditionExpression=Key('semana').eq(semana)
            )
            items = response.get('Items', [])
            
            # Manejar paginación
            while 'LastEvaluatedKey' in response:
                response = table.query(
                    IndexName='semana-index',
                    KeyConditionExpression=Key('semana').eq(semana),
                    ExclusiveStartKey=response['LastEvaluatedKey']
                )
                items.extend(response.get('Items', []))
            
            return [DynamoDBService._item_to_proyeccion(item) for item in items]
        except ClientError as e:
            raise Exception(f"Error al obtener proyecciones por semana: {e.response['Error']['Message']}")
    
    @staticmethod
    def obtener_por_categoria(categoria: str) -> List[ProyeccionInsumo]:
        """Obtiene todas las proyecciones de una categoría específica usando GSI"""
        try:
            response = table.query(
                IndexName='categoria-index',
                KeyConditionExpression=Key('categoria_insumo').eq(categoria)
            )
            items = response.get('Items', [])
            
            # Manejar paginación
            while 'LastEvaluatedKey' in response:
                response = table.query(
                    IndexName='categoria-index',
                    KeyConditionExpression=Key('categoria_insumo').eq(categoria),
                    ExclusiveStartKey=response['LastEvaluatedKey']
                )
                items.extend(response.get('Items', []))
            
            return [DynamoDBService._item_to_proyeccion(item) for item in items]
        except ClientError as e:
            raise Exception(f"Error al obtener proyecciones por categoría: {e.response['Error']['Message']}")
    
    @staticmethod
    def eliminar_proyeccion(tienda_id: str, fecha_proyeccion: str, semana: str) -> bool:
        """Elimina una proyección específica"""
        try:
            fecha_proyeccion_semana = f"{fecha_proyeccion}#{semana}"
            response = table.delete_item(
                Key={
                    'tienda_id': tienda_id,
                    'fecha_proyeccion_semana': fecha_proyeccion_semana
                },
                ReturnValues='ALL_OLD'
            )
            return 'Attributes' in response
        except ClientError as e:
            raise Exception(f"Error al eliminar proyección: {e.response['Error']['Message']}")
    
    @staticmethod
    def eliminar_por_tienda_y_semana(tienda_id: str, semana: str) -> int:
        """Elimina todas las proyecciones de una tienda en una semana específica"""
        try:
            # Primero obtener todos los items que coinciden
            response = table.query(
                KeyConditionExpression=Key('tienda_id').eq(tienda_id)
            )
            items = response.get('Items', [])
            
            # Filtrar por semana
            items_to_delete = [item for item in items if item['semana'] == semana]
            
            # Eliminar cada item
            deleted_count = 0
            for item in items_to_delete:
                table.delete_item(
                    Key={
                        'tienda_id': item['tienda_id'],
                        'fecha_proyeccion_semana': item['fecha_proyeccion_semana']
                    }
                )
                deleted_count += 1
            
            return deleted_count
        except ClientError as e:
            raise Exception(f"Error al eliminar proyecciones: {e.response['Error']['Message']}")
    
    @staticmethod
    def actualizar_proyeccion(proyeccion: ProyeccionInsumo) -> ProyeccionInsumo:
        """Actualiza una proyección existente"""
        try:
            item = DynamoDBService._proyeccion_to_item(proyeccion)
            table.put_item(Item=item)
            return proyeccion
        except ClientError as e:
            raise Exception(f"Error al actualizar proyección: {e.response['Error']['Message']}")