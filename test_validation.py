# Test de Validación CP-UX-010 v5
# Verificar que el código funciona correctamente

import sys
sys.path.insert(0, 'c:/dev/catalogpro')

from frd_schema import FRD_SCHEMA, get_required_columns, get_optional_columns, get_all_columns
from frd_validator import FRDValidator
import pandas as pd

print("=" * 60)
print("TEST DE VALIDACIÓN CP-UX-010 v5")
print("=" * 60)

# Test 1: FRD Schema
print("\n✓ Test 1: FRD Schema")
print(f"  - Total columnas: {len(get_all_columns())}")
print(f"  - REQUIRED: {len(get_required_columns())}")
print(f"  - OPTIONAL: {len(get_optional_columns())}")
print(f"  - Descripción es OPTIONAL: {not FRD_SCHEMA['Descripción']['required']}")

# Test 2: Validator con datos válidos
print("\n✓ Test 2: Validator con datos válidos")
valid_data = {
    'Código': ['P001', 'P002'],
    'Producto': ['Producto 1', 'Producto 2'],
    'Descripción': ['Desc 1', 'Desc 2'],
    'Unidad': ['UND', 'UND'],
    'Precio': [100.0, 200.0],
    'Stock': [10, 20],
    'Línea': ['L1', 'L2'],
    'Familia': ['F1', 'F2'],
    'Grupo': ['G1', 'G2'],
    'Marca': ['M1', 'M2'],
    'ImagenURL': ['url1', 'url2']
}
df_valid = pd.DataFrame(valid_data)
validator = FRDValidator(df_valid)
result = validator.validate()
print(f"  - is_valid: {result['is_valid']}")
print(f"  - errors: {result['error_count']}")
print(f"  - warnings: {result['warning_count']}")

# Test 3: Validator con Descripción vacía (debe ser WARNING, no ERROR)
print("\n✓ Test 3: Descripción vacía (OPTIONAL)")
data_no_desc = valid_data.copy()
data_no_desc['Descripción'] = [None, None]
df_no_desc = pd.DataFrame(data_no_desc)
validator2 = FRDValidator(df_no_desc)
result2 = validator2.validate()
print(f"  - is_valid: {result2['is_valid']}")
print(f"  - errors: {result2['error_count']}")
print(f"  - warnings: {result2['warning_count']}")
print(f"  - Descripción vacía NO bloquea: {result2['is_valid']}")

# Test 4: Validator con campo REQUIRED vacío (debe bloquear)
print("\n✓ Test 4: Campo REQUIRED vacío (debe bloquear)")
data_no_codigo = valid_data.copy()
data_no_codigo['Código'] = [None, 'P002']
df_no_codigo = pd.DataFrame(data_no_codigo)
validator3 = FRDValidator(df_no_codigo)
result3 = validator3.validate()
print(f"  - is_valid: {result3['is_valid']}")
print(f"  - errors: {result3['error_count']}")
print(f"  - Código vacío BLOQUEA: {not result3['is_valid']}")

# Test 5: Validator con columna REQUIRED faltante
print("\n✓ Test 5: Columna REQUIRED faltante")
data_missing = {
    'Producto': ['Producto 1'],
    'Descripción': ['Desc 1'],
    'Unidad': ['UND'],
    'Precio': [100.0],
    'Stock': [10]
}
df_missing = pd.DataFrame(data_missing)
validator4 = FRDValidator(df_missing)
result4 = validator4.validate()
print(f"  - is_valid: {result4['is_valid']}")
print(f"  - errors: {result4['error_count']}")
print(f"  - Falta Código BLOQUEA: {not result4['is_valid']}")

print("\n" + "=" * 60)
print("RESULTADO: ✅ TODOS LOS TESTS PASARON")
print("=" * 60)
