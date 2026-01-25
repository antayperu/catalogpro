"""
Script para crear ticket CP-UX-010 en Notion - CORREGIDO
"""
import requests
import streamlit as st

# Leer credenciales desde secrets.toml (NO hardcodear)
NOTION_TOKEN = st.secrets["notion"]["NOTION_TOKEN"]
DATABASE_ID = "2e67544a512b80e88a33df625486a013"

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# Primero, obtener la estructura de la base de datos para ver los campos exactos
print("🔍 Consultando estructura de la base de datos...")
query_url = f"https://api.notion.com/v1/databases/{DATABASE_ID}"

try:
    db_response = requests.get(query_url, headers=headers)
    
    if db_response.status_code == 200:
        db_data = db_response.json()
        properties = db_data.get("properties", {})
        print("✅ Campos disponibles en la base de datos:")
        for prop_name, prop_data in properties.items():
            print(f"   - {prop_name}: {prop_data.get('type')}")
        
        # Crear el ticket con la estructura correcta
        print("\n📝 Creando ticket CP-UX-010...")
        
        create_url = "https://api.notion.com/v1/pages"
        
        new_page = {
            "parent": {"database_id": DATABASE_ID},
            "properties": {
                "ID": {
                    "title": [
                        {
                            "text": {
                                "content": "CP-UX-010"
                            }
                        }
                    ]
                },
                "Estado": {
                    "select": {
                        "name": "Done"
                    }
                }
            }
        }
        
        create_response = requests.post(create_url, headers=headers, json=new_page)
        
        if create_response.status_code == 200:
            print("✅ Ticket CP-UX-010 creado exitosamente en Notion")
            print(f"   Page ID: {create_response.json().get('id')}")
        else:
            print(f"❌ Error al crear ticket: {create_response.status_code}")
            print(f"   Respuesta: {create_response.text}")
    else:
        print(f"❌ Error al consultar base de datos: {db_response.status_code}")
        print(db_response.text)
        
except Exception as e:
    print(f"❌ Error: {e}")
