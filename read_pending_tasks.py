"""
Script simple para leer base de datos de Notion usando requests
Enfoque escalable y profesional usando API REST directamente
"""
import requests
import json
from datetime import datetime
import streamlit as st
import os

# Leer credenciales desde secrets.toml (NO hardcodear)
NOTION_TOKEN = st.secrets["notion"]["NOTION_TOKEN"]
DATABASE_ID = "2e67544a512b80e88a33df625486a013"

# Headers para la API de Notion
HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def read_database():
    """Lee la base de datos usando la API REST de Notion"""
    print(f"🔗 Conectando a Notion API REST...")
    print(f"📊 Leyendo base de datos: {DATABASE_ID}\n")
    
    # URL para query de base de datos
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    
    try:
        # Hacer POST request para query
        response = requests.post(url, headers=HEADERS, json={})
        
        if response.status_code != 200:
            print(f"❌ Error: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return
        
        data = response.json()
        results = data.get("results", [])
        
        if not results:
            print("⚠️ No se encontraron entradas en la base de datos")
            return
        
        print(f"✅ Se encontraron {len(results)} entradas\n")
        print("=" * 80)
        
        # Procesar cada entrada
        all_entries = []
        for idx, page in enumerate(results, 1):
            props = page.get("properties", {})
            page_id = page.get("id", "")
            
            print(f"\n📌 Entrada #{idx}")
            print("-" * 80)
            
            entry_data = {"id": page_id, "properties": {}}
            
            # Procesar cada propiedad
            for prop_name, prop_value in props.items():
                prop_type = prop_value.get("type")
                value = None
                
                if prop_type == "title":
                    title_data = prop_value.get("title", [])
                    if title_data:
                        value = " ".join([t.get("plain_text", "") for t in title_data])
                        print(f"   📝 {prop_name}: {value}")
                
                elif prop_type == "rich_text":
                    text_data = prop_value.get("rich_text", [])
                    if text_data:
                        value = " ".join([t.get("plain_text", "") for t in text_data])
                        print(f"   📄 {prop_name}: {value}")
                
                elif prop_type == "number":
                    value = prop_value.get("number")
                    if value is not None:
                        print(f"   🔢 {prop_name}: {value}")
                
                elif prop_type == "select":
                    select_data = prop_value.get("select", {})
                    if select_data:
                        value = select_data.get("name", "")
                        print(f"   🏷️ {prop_name}: {value}")
                
                elif prop_type == "multi_select":
                    multi_select_data = prop_value.get("multi_select", [])
                    if multi_select_data:
                        value = [item.get("name", "") for item in multi_select_data]
                        print(f"   🏷️ {prop_name}: {', '.join(value)}")
                
                elif prop_type == "date":
                    date_data = prop_value.get("date", {})
                    if date_data:
                        start = date_data.get("start", "")
                        end = date_data.get("end", "")
                        value = f"{start} → {end}" if end else start
                        print(f"   📅 {prop_name}: {value}")
                
                elif prop_type == "checkbox":
                    value = prop_value.get("checkbox", False)
                    status = "✅" if value else "⬜"
                    print(f"   {status} {prop_name}: {value}")
                
                elif prop_type == "url":
                    value = prop_value.get("url", "")
                    if value:
                        print(f"   🔗 {prop_name}: {value}")
                
                elif prop_type == "email":
                    value = prop_value.get("email", "")
                    if value:
                        print(f"   📧 {prop_name}: {value}")
                
                elif prop_type == "status":
                    status_data = prop_value.get("status", {})
                    if status_data:
                        value = status_data.get("name", "")
                        print(f"   🎯 {prop_name}: {value}")
                
                entry_data["properties"][prop_name] = {
                    "type": prop_type,
                    "value": value
                }
            
            all_entries.append(entry_data)
        
        print("\n" + "=" * 80)
        
        # Guardar en archivo Markdown
        output_file = "docs/PENDIENTES_NOTION.md"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("# Licencias_CatalogPro - Tareas Pendientes\n\n")
            f.write(f"**Última sincronización:** {os.environ.get('USERNAME', 'User')}\n")
            f.write(f"**Total de entradas:** {len(results)}\n\n")
            f.write("---\n\n")
            
            for idx, entry in enumerate(all_entries, 1):
                # Buscar el título
                title = f"Entrada {idx}"
                for prop_name, prop_data in entry["properties"].items():
                    if prop_data["type"] == "title" and prop_data["value"]:
                        title = prop_data["value"]
                        break
                
                f.write(f"## {idx}. {title}\n\n")
                
                # Escribir propiedades
                for prop_name, prop_data in entry["properties"].items():
                    if prop_data["type"] != "title" and prop_data["value"]:
                        value = prop_data["value"]
                        if isinstance(value, list):
                            value = ", ".join(value)
                        f.write(f"- **{prop_name}:** {value}\n")
                
                f.write("\n")
        
        print(f"\n✅ Datos guardados en: {output_file}")
        
        # También guardar como JSON para procesamiento posterior
        json_file = "docs/PENDIENTES_NOTION.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(all_entries, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Datos JSON guardados en: {json_file}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    read_database()
