"""
Script para actualizar CP-UX-009 a estado Done en Notion
"""
import requests
import json
import streamlit as st

# Leer credenciales desde secrets.toml (NO hardcodear)
NOTION_TOKEN = st.secrets["notion"]["NOTION_TOKEN"]
DATABASE_ID = "2e67544a512b80e88a33df625486a013"

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# 1. Buscar el ticket CP-UX-009
url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"

try:
    response = requests.post(url, headers=headers, json={})
    
    if response.status_code == 200:
        data = response.json()
        results = data.get("results", [])
        
        # Buscar CP-UX-009
        page_id = None
        for page in results:
            props = page.get("properties", {})
            id_prop = props.get("ID", {})
            title_data = id_prop.get("title", [])
            if title_data:
                ticket_id = title_data[0].get("plain_text", "")
                if ticket_id == "CP-UX-009":
                    page_id = page.get('id')
                    print(f"✅ Ticket CP-UX-009 encontrado: {page_id}")
                    break
        
        if page_id:
            # 2. Actualizar estado a "Done"
            update_url = f"https://api.notion.com/v1/pages/{page_id}"
            update_data = {
                "properties": {
                    "Estado": {
                        "select": {
                            "name": "Done"
                        }
                    }
                }
            }
            
            update_response = requests.patch(update_url, headers=headers, json=update_data)
            
            if update_response.status_code == 200:
                print("✅ Ticket CP-UX-009 actualizado a estado 'Done' en Notion")
            else:
                print(f"❌ Error al actualizar: {update_response.status_code}")
                print(update_response.text)
        else:
            print("❌ Ticket CP-UX-009 no encontrado")
    else:
        print(f"❌ Error al consultar Notion: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"❌ Error: {e}")
