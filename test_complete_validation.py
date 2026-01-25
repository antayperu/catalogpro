# Test Completo CP-UX-010 v5 - Validación Metodología Antay
# Verificar que TODA la implementación funciona correctamente

import sys
sys.path.insert(0, 'c:/dev/catalogpro')

print("=" * 70)
print("VALIDACIÓN COMPLETA CP-UX-010 v5 - METODOLOGÍA ANTAY")
print("=" * 70)

# Test 1: Imports
print("\n[1/6] Verificando imports...")
try:
    from frd_schema import FRD_SCHEMA, get_required_columns, get_optional_columns, get_all_columns
    from frd_validator import FRDValidator
    import pandas as pd
    print("✅ Todos los imports correctos")
except Exception as e:
    print(f"❌ Error en imports: {e}")
    sys.exit(1)

# Test 2: FRD Schema - Descripción OPTIONAL
print("\n[2/6] Verificando FRD Schema...")
try:
    assert not FRD_SCHEMA['Descripción']['required'], "Descripción debe ser OPTIONAL"
    assert len(get_required_columns()) == 5, f"Debe haber 5 REQUIRED, encontrados: {len(get_required_columns())}"
    assert len(get_optional_columns()) == 6, f"Debe haber 6 OPTIONAL, encontrados: {len(get_optional_columns())}"
    
    required = get_required_columns()
    expected_required = ['Código', 'Producto', 'Unidad', 'Precio', 'Stock']
    assert set(required) == set(expected_required), f"REQUIRED incorrectos: {required}"
    
    print("✅ FRD Schema correcto:")
    print(f"   - 5 REQUIRED: {', '.join(required)}")
    print(f"   - 6 OPTIONAL: Línea, Familia, Grupo, Marca, Descripción, ImagenURL")
except AssertionError as e:
    print(f"❌ {e}")
    sys.exit(1)

# Test 3: Validator - Datos válidos
print("\n[3/6] Validando con datos completos...")
try:
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
    
    assert result['is_valid'], "Datos válidos deben pasar validación"
    assert result['error_count'] == 0, f"No debe haber errores, encontrados: {result['error_count']}"
    assert result['warning_count'] == 0, f"No debe haber warnings, encontrados: {result['warning_count']}"
    
    print("✅ Validación de datos completos OK")
except AssertionError as e:
    print(f"❌ {e}")
    sys.exit(1)

# Test 4: Validator - Descripción vacía (debe ser WARNING)
print("\n[4/6] Validando Descripción vacía (OPTIONAL)...")
try:
    data_no_desc = valid_data.copy()
    data_no_desc['Descripción'] = [None, None]
    df_no_desc = pd.DataFrame(data_no_desc)
    validator2 = FRDValidator(df_no_desc)
    result2 = validator2.validate()
    
    assert result2['is_valid'], "Descripción vacía NO debe bloquear (es OPTIONAL)"
    assert result2['error_count'] == 0, f"No debe haber errores, encontrados: {result2['error_count']}"
    assert result2['warning_count'] > 0, "Debe haber al menos 1 warning por Descripción vacía"
    
    print("✅ Descripción vacía genera WARNING (no bloquea)")
    print(f"   - is_valid: True")
    print(f"   - warnings: {result2['warning_count']}")
except AssertionError as e:
    print(f"❌ {e}")
    sys.exit(1)

# Test 5: Validator - Campo REQUIRED vacío (debe bloquear)
print("\n[5/6] Validando campo REQUIRED vacío...")
try:
    data_no_codigo = valid_data.copy()
    data_no_codigo['Código'] = [None, 'P002']
    df_no_codigo = pd.DataFrame(data_no_codigo)
    validator3 = FRDValidator(df_no_codigo)
    result3 = validator3.validate()
    
    assert not result3['is_valid'], "Campo REQUIRED vacío DEBE bloquear"
    assert result3['error_count'] > 0, "Debe haber al menos 1 error"
    
    print("✅ Campo REQUIRED vacío bloquea importación")
    print(f"   - is_valid: False")
    print(f"   - errors: {result3['error_count']}")
except AssertionError as e:
    print(f"❌ {e}")
    sys.exit(1)

# Test 6: Validator - Columna REQUIRED faltante
print("\n[6/6] Validando columna REQUIRED faltante...")
try:
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
    
    assert not result4['is_valid'], "Columna REQUIRED faltante DEBE bloquear"
    assert result4['error_count'] > 0, "Debe haber al menos 1 error"
    
    # Verificar que el error menciona la columna faltante
    has_missing_error = any(
        error['type'] == 'MISSING_REQUIRED_COLUMN' 
        for error in result4['errors']
    )
    assert has_missing_error, "Debe haber error tipo MISSING_REQUIRED_COLUMN"
    
    print("✅ Columna REQUIRED faltante bloquea importación")
    print(f"   - is_valid: False")
    print(f"   - errors: {result4['error_count']}")
except AssertionError as e:
    print(f"❌ {e}")
    sys.exit(1)

# Test 7: Verificar que main.py tiene las funciones correctas
print("\n[7/7] Verificando funciones en main.py...")
try:
    with open('c:/dev/catalogpro/main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar que _render_preview_workflow tiene source_type
    assert 'def _render_preview_workflow(self, df, source_name, source_type=' in content, \
        "_render_preview_workflow debe tener parámetro source_type"
    
    # Verificar que las keys son únicas
    assert 'key=f"cancel_import_{source_type}"' in content, \
        "Debe usar keys únicas con source_type"
    
    assert 'key=f"confirm_import_{source_type}"' in content, \
        "Debe usar keys únicas con source_type"
    
    # Verificar que NO existe el botón "Descargar reporte de validación"
    assert 'Descargar reporte de validación' not in content, \
        "NO debe existir botón 'Descargar reporte de validación' (no está en FRD)"
    
    # Verificar que Google Sheets NO tiene botón "Importar" intermedio
    # Debe tener solo "Validar" y luego preview con "Confirmar importación"
    sheets_section = content[content.find('# ===== GOOGLE SHEETS TAB ====='):content.find('# ===== RENDER DATA TABLE')]
    
    # Contar botones "Importar" en sección Sheets (debe ser 0)
    import_count = sheets_section.count('st.button("Importar"')
    assert import_count == 0, f"Google Sheets NO debe tener botón 'Importar' intermedio, encontrados: {import_count}"
    
    print("✅ Funciones en main.py correctas:")
    print("   - _render_preview_workflow con source_type ✓")
    print("   - Keys únicas por tab ✓")
    print("   - Sin 'Descargar reporte de validación' ✓")
    print("   - Google Sheets sin botón 'Importar' intermedio ✓")
    
except AssertionError as e:
    print(f"❌ {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error inesperado: {e}")
    sys.exit(1)

print("\n" + "=" * 70)
print("✅ VALIDACIÓN COMPLETA EXITOSA - TODOS LOS TESTS PASARON")
print("=" * 70)
print("\nResumen:")
print("✓ FRD Schema: 5 REQUIRED, 6 OPTIONAL")
print("✓ Descripción es OPTIONAL (no bloquea)")
print("✓ Validación funciona correctamente")
print("✓ Keys únicas por tab (sin duplicados)")
print("✓ Sin funcionalidades no-FRD")
print("✓ Google Sheets simplificado (sin botón Importar intermedio)")
print("\n🎯 CÓDIGO LISTO PARA PRODUCCIÓN según Metodología Antay")
