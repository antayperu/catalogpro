import sys
sys.path.insert(0, 'c:/dev/catalogpro')

print('Validando fix completo de PDF...')

from main import EnhancedPDFExporter
import pandas as pd

# Crear DataFrame de prueba SIN jerarquía (como el caso del usuario)
df = pd.DataFrame({
    'Código': ['P001', 'P002'],
    'Producto': ['Test1', 'Test2'],
    'Descripción': ['Desc1', 'Desc2'],
    'Unidad': ['UND', 'UND'],
    'Precio': [100, 200],
    'Stock': [10, 20],
    'ImagenURL': ['https://picsum.photos/200', 'https://picsum.photos/201'],
    'Línea': [None, None],
    'Familia': [None, None],
    'Grupo': [None, None],
    'Marca': [None, None]
})

exporter = EnhancedPDFExporter()

try:
    pdf_bytes, stats = exporter.generate_pdf_optimized(
        df, 'Test Business', 'S/', '123456', 'test@test.com'
    )
    
    print(f'✅ Tipo: {type(pdf_bytes).__name__}')
    print(f'✅ Es bytes: {isinstance(pdf_bytes, bytes)}')
    print(f'✅ Tamaño: {len(pdf_bytes):,} bytes')
    print(f'✅ Páginas: {stats["page_count"]}')
    print('\n🎯 VALIDACIÓN EXITOSA - PDF generado correctamente')
    
except Exception as e:
    print(f'❌ ERROR: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
