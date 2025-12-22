import pandas as pd
import math

# Mock Data
data = {
    'Producto': [f'Prod {i}' for i in range(1, 101)], # 100 items
    'Línea': ['Electro', 'Hogar'] * 50,
    'Familia': ['TV', 'Muebles'] * 50,
    'Marca': ['Sony', 'Ikea'] * 50,
    'Precio': [100.0, 200.0] * 50,
    'Descripción': ['Desc'] * 100,
    'ImagenURL': ['http://img.com/1.jpg'] * 100,
    'Unidad': ['UND'] * 100
}
df = pd.DataFrame(data)

# Test 1: Pagination Logic
items_per_page = 24
total_products = len(df)
total_pages = math.ceil(total_products / items_per_page)

print(f"Total Pages: {total_pages} (Expected 5 for 100 items / 24)")
assert total_pages == 5

# Page 1
page = 1
start_idx = (page - 1) * items_per_page
end_idx = min(start_idx + items_per_page, total_products)
page_df = df.iloc[start_idx:end_idx]
print(f"Page 1 items: {len(page_df)} (Expected 24)")
assert len(page_df) == 24
assert page_df.iloc[0]['Producto'] == 'Prod 1'

# Page 5 (Last page)
page = 5
start_idx = (page - 1) * items_per_page
end_idx = min(start_idx + items_per_page, total_products)
page_df = df.iloc[start_idx:end_idx]
expected_last_page_items = 100 - (24 * 4) # 4
print(f"Page 5 items: {len(page_df)} (Expected 4)")
assert len(page_df) == 4
assert page_df.iloc[-1]['Producto'] == 'Prod 100'

# Test 2: Filtering + Pagination
# Filter: Línea = Electro (50 items)
filtered = df[df['Línea'] == 'Electro']
total_pages_filt = math.ceil(len(filtered) / items_per_page)
print(f"Filtered Total Pages: {total_pages_filt} (Expected 3 for 50 items)") # 24, 24, 2
assert total_pages_filt == 3

# Test 3: Slice Logic
page = 3
start_idx = (page - 1) * items_per_page
end_idx = min(start_idx + items_per_page, len(filtered))
page_df_filt = filtered.iloc[start_idx:end_idx]
print(f"Filtered Page 3 items: {len(page_df_filt)} (Expected 2)")
assert len(page_df_filt) == 2

print("\n✅ LOGIC VERIFICATION PASSED")
