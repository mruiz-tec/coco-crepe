import os
import boto3
from botocore.exceptions import ClientError

# Configuración de AWS
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
DYNAMODB_TABLE_NAME = os.getenv("DYNAMODB_TABLE_NAME", "ProyeccionesInsumos")

# Cliente de DynamoDB
dynamodb = boto3.resource(
    'dynamodb',
    region_name=AWS_REGION,
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
)

table = dynamodb.Table(DYNAMODB_TABLE_NAME)


def create_table_if_not_exists():
    """
    Crea la tabla de DynamoDB si no existe.
    Esta función es útil para desarrollo/testing.
    """
    dynamodb_client = boto3.client(
        'dynamodb',
        region_name=AWS_REGION,
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
    )
    
    try:
        dynamodb_client.describe_table(TableName=DYNAMODB_TABLE_NAME)
        print(f"Tabla {DYNAMODB_TABLE_NAME} ya existe")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print(f"Creando tabla {DYNAMODB_TABLE_NAME}...")
            
            table = dynamodb_client.create_table(
                TableName=DYNAMODB_TABLE_NAME,
                KeySchema=[
                    {
                        'AttributeName': 'tienda_id',
                        'KeyType': 'HASH'  # Partition key
                    },
                    {
                        'AttributeName': 'fecha_proyeccion_semana',
                        'KeyType': 'RANGE'  # Sort key
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'tienda_id',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'fecha_proyeccion_semana',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'semana',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'categoria_insumo',
                        'AttributeType': 'S'
                    }
                ],
                GlobalSecondaryIndexes=[
                    {
                        'IndexName': 'semana-index',
                        'KeySchema': [
                            {
                                'AttributeName': 'semana',
                                'KeyType': 'HASH'
                            }
                        ],
                        'Projection': {
                            'ProjectionType': 'ALL'
                        },
                        'ProvisionedThroughput': {
                            'ReadCapacityUnits': 5,
                            'WriteCapacityUnits': 5
                        }
                    },
                    {
                        'IndexName': 'categoria-index',
                        'KeySchema': [
                            {
                                'AttributeName': 'categoria_insumo',
                                'KeyType': 'HASH'
                            }
                        ],
                        'Projection': {
                            'ProjectionType': 'ALL'
                        },
                        'ProvisionedThroughput': {
                            'ReadCapacityUnits': 5,
                            'WriteCapacityUnits': 5
                        }
                    }
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
            )
            
            # Esperar a que la tabla esté activa
            waiter = dynamodb_client.get_waiter('table_exists')
            waiter.wait(TableName=DYNAMODB_TABLE_NAME)
            print(f"Tabla {DYNAMODB_TABLE_NAME} creada exitosamente")
        else:
            raise