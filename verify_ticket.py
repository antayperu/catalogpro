"""
Script para verificar si CP-UX-009 existe en Notion
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

# Query para buscar CP-UX-009
url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"

try:
    response = requests.post(url, headers=headers, json={})
    
    if response.status_code == 200:
        data = response.json()
        results = data.get("results", [])
        
        # Buscar CP-UX-009
        found = False
        for page in results:
            props = page.get("properties", {})
            id_prop = props.get("ID", {})
            title_data = id_prop.get("title", [])
            if title_data:
                ticket_id = title_data[0].get("plain_text", "")
                if ticket_id == "CP-UX-009":
                    found = True
                    print(f"✅ CONFIRMADO: Ticket CP-UX-009 existe en Notion")
                    print(f"   Page ID: {page.get('id')}")
                    
                    # Mostrar estado actual
                    estado = props.get("Estado", {}).get("select", {}).get("name", "")
                    print(f"   Estado actual: {estado}")
                    break
        
        if not found:
            print("❌ Ticket CP-UX-009 NO encontrado en Notion")
            print("   Necesita ser creado")
    else:
        print(f"❌ Error al consultar Notion: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"❌ Error: {e}")
