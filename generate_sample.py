import pandas as pd
import numpy as np

# Define categories
lines = ['ELECTRO', 'HOGAR', 'MODA', 'DEPORTES']
families = {
    'ELECTRO': ['COMPUTO', 'TELEFONIA', 'AUDIO'],
    'HOGAR': ['COCINA', 'SALA', 'DORMITORIO'],
    'MODA': ['HOMBRE', 'MUJER', 'NIÑOS'],
    'DEPORTES': ['FUTBOL', 'NATACION', 'FITNESS']
}
brands = ['SAMSUNG', 'LG', 'SONY', 'NIKE', 'ADIDAS', 'OSTER', 'DELL', 'HP']

# Generate sample data
data = []
for i in range(1, 51):
    line = np.random.choice(lines)
    family = np.random.choice(families[line])
    group = "GENERAL"
    brand = np.random.choice(brands)
    code = f"{brand[:3]}-{i:04d}"
    
    data.append({
        'Línea': line,
        'Familia': family,
        'Grupo': group,
        'Marca': brand,
        'Código': code,
        'Producto': f"Producto {family} {i}",
        'Descripción': f"Descripción detallada del producto {code} con características premium.",
        'Unidad': 'UND',
        'Precio': round(np.random.uniform(10, 2000), 2),
        'Stock': np.random.randint(0, 100),
        'ImagenURL': f"https://picsum.photos/400?random={i}"
    })

df = pd.DataFrame(data)

# Save
df.to_excel('c:\\dev\\catalogpro\\ProductSample_Enterprise.xlsx', index=False)
print("Enterprise sample created at c:\\dev\\catalogpro\\ProductSample_Enterprise.xlsx")
