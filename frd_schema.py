"""
FRD Schema Definition for CatalogPro
Defines required and optional fields with validation rules
Aligned with FRD v1.1 - BR-09 and BR-10
"""

FRD_SCHEMA = {
    # BR-10: Agrupaciones opcionales (Línea/Familia/Grupo/Marca)
    'Línea': {
        'required': False,  # OPTIONAL per BR-10
        'type': 'string',
        'example': 'ELECTRO',
        'description': 'Línea de producto (categoría principal)'
    },
    'Familia': {
        'required': False,  # OPTIONAL per BR-10
        'type': 'string',
        'example': 'COMPUTO',
        'description': 'Familia de producto (subcategoría)'
    },
    'Grupo': {
        'required': False,  # OPTIONAL per BR-10
        'type': 'string',
        'example': 'LAPTOPS',
        'description': 'Grupo de producto (clasificación específica)'
    },
    'Marca': {
        'required': False,  # OPTIONAL per BR-10
        'type': 'string',
        'example': 'DELL',
        'description': 'Marca del producto'
    },
    # Campos REQUIRED (core del producto)
    'Código': {
        'required': True,
        'type': 'string',
        'example': 'DL-5520',
        'description': 'Código único del producto (SKU)'
    },
    'Producto': {
        'required': True,
        'type': 'string',
        'example': 'Laptop Inspiron 15',
        'description': 'Nombre comercial del producto'
    },
    'Descripción': {
        'required': False,  # OPTIONAL - Cambio de negocio v5
        'type': 'string',
        'example': 'Core i5 8GB RAM 256GB SSD',
        'description': 'Descripción detallada del producto'
    },
    'Unidad': {
        'required': True,
        'type': 'string',
        'example': 'UND',
        'description': 'Unidad de medida (UND, KG, LT, etc.)'
    },
    'Precio': {
        'required': True,
        'type': 'float',
        'example': 1299.99,
        'description': 'Precio unitario en moneda local'
    },
    'Stock': {
        'required': True,
        'type': 'int',
        'example': 50,
        'description': 'Cantidad disponible en inventario'
    },
    # BR-09: ImagenURL opcional
    'ImagenURL': {
        'required': False,  # OPTIONAL per BR-09
        'type': 'string',
        'example': 'https://ejemplo.com/producto.jpg',
        'description': 'URL de la imagen del producto'
    }
}

def get_required_columns():
    """Retorna lista de columnas obligatorias"""
    return [col for col, spec in FRD_SCHEMA.items() if spec['required']]

def get_optional_columns():
    """Retorna lista de columnas opcionales"""
    return [col for col, spec in FRD_SCHEMA.items() if not spec['required']]

def get_all_columns():
    """Retorna lista de todas las columnas"""
    return list(FRD_SCHEMA.keys())

def get_column_spec(column_name):
    """Retorna especificación de una columna"""
    return FRD_SCHEMA.get(column_name, None)
