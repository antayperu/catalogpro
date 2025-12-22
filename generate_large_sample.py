import pandas as pd
import numpy as np

# Define categories
lines = ['ELECTRO', 'HOGAR', 'MODA', 'DEPORTES', 'JUGUETES', 'AUTOMOTRIZ', 'BELLEZA', 'SALUD']
families = {
    'ELECTRO': ['COMPUTO', 'TELEFONIA', 'AUDIO', 'VIDEO', 'GAMING'],
    'HOGAR': ['COCINA', 'SALA', 'DORMITORIO', 'BAÑO', 'DECORACION'],
    'MODA': ['HOMBRE', 'MUJER', 'NIÑOS', 'CALZADO', 'ACCESORIOS'],
    'DEPORTES': ['FUTBOL', 'NATACION', 'FITNESS', 'CAMPING', 'CICLISMO'],
    'JUGUETES': ['EDUCATIVOS', 'FIGURAS', 'JUEGOS MESA', 'AIRE LIBRE'],
    'AUTOMOTRIZ': ['INTERIOR', 'EXTERIOR', 'MECANICA', 'LIMPIEZA'],
    'BELLEZA': ['MAQUILLAJE', 'PERFUMES', 'CUIDADO PIEL'],
    'SALUD': ['VITAMINAS', 'PRIMEROS AUXILIOS', 'ORTOPEDIA']
}
brands = ['SAMSUNG', 'LG', 'SONY', 'NIKE', 'ADIDAS', 'OSTER', 'DELL', 'HP', 'LOREAL', 'LEGO', 'MATTEL', 'TOYOTA', 'FORD']

# Generate 800 items
data = []
for i in range(1, 801):
    line = np.random.choice(lines)
    family = np.random.choice(families.get(line, ['GENERAL']))
    group = "GENERAL"
    brand = np.random.choice(brands)
    code = f"{brand[:3]}-{i:04d}"
    
    # Use reliable placeholder images that actually work to test download speed
    # Using different seeds to avoid local caching if the URL is the key
    img_url = f"https://picsum.photos/400?random={i}"
    
    data.append({
        'Línea': line,
        'Familia': family,
        'Grupo': group,
        'Marca': brand,
        'Código': code,
        'Producto': f"Producto {family} {i} Gran Calidad",
        'Descripción': f"Descripción detallada del producto {code} con características premium y alto rendimiento.",
        'Unidad': 'UND',
        'Precio': round(np.random.uniform(10, 2000), 2),
        'Stock': np.random.randint(0, 100),
        'ImagenURL': img_url
    })

df = pd.DataFrame(data)

# Save
df.to_excel('c:\\dev\\catalogpro\\ProductSample_Large.xlsx', index=False)
print("Large sample (800 items) created at c:\\dev\\catalogpro\\ProductSample_Large.xlsx")
