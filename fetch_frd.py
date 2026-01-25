"""
Script para descargar el FRD de CatalogPro desde Notion con token actualizado
"""
import os
from notion_client import Client
import requests
import json
import streamlit as st

# Leer credenciales desde secrets.toml (NO hardcodear)
NOTION_TOKEN = st.secrets["notion"]["NOTION_TOKEN"]
PAGE_ID = "2377544a512b804db020d8e8b62fd00d"
OUTPUT_FILE = "docs/FRD_CatalogPro.md"

def get_block_content(block):
    """Extrae contenido de un bloque de Notion"""
    block_type = block.get("type")
    content = ""
    prefix = ""
    
    if block_type == "paragraph":
        rich_text = block.get("paragraph", {}).get("rich_text", [])
        if rich_text:
            content = "".join([t.get("plain_text", "") for t in rich_text])
    elif block_type == "heading_1":
        prefix = "# "
        rich_text = block.get("heading_1", {}).get("rich_text", [])
        if rich_text:
            content = "".join([t.get("plain_text", "") for t in rich_text])
    elif block_type == "heading_2":
        prefix = "## "
        rich_text = block.get("heading_2", {}).get("rich_text", [])
        if rich_text:
            content = "".join([t.get("plain_text", "") for t in rich_text])
    elif block_type == "heading_3":
        prefix = "### "
        rich_text = block.get("heading_3", {}).get("rich_text", [])
        if rich_text:
            content = "".join([t.get("plain_text", "") for t in rich_text])
    elif block_type == "bulleted_list_item":
        prefix = "- "
        rich_text = block.get("bulleted_list_item", {}).get("rich_text", [])
        if rich_text:
            content = "".join([t.get("plain_text", "") for t in rich_text])
    elif block_type == "numbered_list_item":
        prefix = "1. "
        rich_text = block.get("numbered_list_item", {}).get("rich_text", [])
        if rich_text:
            content = "".join([t.get("plain_text", "") for t in rich_text])
    elif block_type == "code":
        code_info = block.get("code", {})
        rich_text = code_info.get("rich_text", [])
        language = code_info.get("language", "")
        if rich_text:
            code_content = "".join([t.get("plain_text", "") for t in rich_text])
            return f"```{language}\n{code_content}\n```"
    elif block_type == "quote":
        prefix = "> "
        rich_text = block.get("quote", {}).get("rich_text", [])
        if rich_text:
            content = "".join([t.get("plain_text", "") for t in rich_text])
    elif block_type == "callout":
        rich_text = block.get("callout", {}).get("rich_text", [])
        icon = block.get("callout", {}).get("icon", {})
        emoji = ""
        if icon.get("type") == "emoji":
            emoji = icon.get("emoji", "💡")
        if rich_text:
            content = f"{emoji} " + "".join([t.get("plain_text", "") for t in rich_text])
    elif block_type == "divider":
        return "---"
    elif block_type == "table":
        return "[TABLA]"
    elif block_type == "child_page":
        title = block.get("child_page", {}).get("title", "Sub-página")
        return f"### [{title}]"
    elif block_type == "toggle":
        prefix = "▶ "
        rich_text = block.get("toggle", {}).get("rich_text", [])
        if rich_text:
            content = "".join([t.get("plain_text", "") for t in rich_text])
    else:
        # Para bloques desconocidos, intentar extraer texto si existe
        return f"[BLOCK: {block_type}]"

    if content:
        return f"{prefix}{content}"
    
    return ""

def fetch_children_recursive(client, block_id, depth=0, file_handle=None):
    """Descarga recursivamente todos los bloques hijos"""
    indent = "  " * depth
    try:
        response = client.blocks.children.list(block_id=block_id)
        results = response.get("results", [])
        
        for block in results:
            text = get_block_content(block)
            if text:
                print(f"{indent}{text[:100]}...")  # Mostrar solo primeros 100 caracteres
                if file_handle:
                    file_handle.write(f"{text}\n")
            
            if block.get("has_children"):
                fetch_children_recursive(client, block["id"], depth + 1, file_handle)
                
    except Exception as e:
        import traceback
        print(f"{indent}Error al obtener bloques hijos para {block_id}: {e}")
        print(f"{indent}Detalles: {traceback.format_exc()}")

def fetch_frd():
    """Descarga el FRD de CatalogPro desde Notion"""
    print(f"🔗 Conectando a Notion con token actualizado...")
    print(f"📄 Descargando FRD (Page ID: {FRD_PAGE_ID})...")
    
    client = Client(auth=NOTION_TOKEN)
    
    # Obtener metadata de la página
    try:
        page = client.pages.retrieve(page_id=FRD_PAGE_ID)
        title = "FRD - CatalogPro Enhanced v2"
        print(f"✅ Página encontrada: {title}")
    except Exception as e:
        print(f"❌ Error al acceder a la página: {e}")
        import traceback
        print(traceback.format_exc())
        return
    
    # Crear directorio si no existe
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    # Descargar contenido
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("# FRD - CatalogPro Enhanced v2\n")
        f.write(f"# Última sincronización: {os.environ.get('USERNAME', 'User')} - [LIVE NOTION FETCH]\n")
        f.write(f"# Fuente: https://exciting-guitar-bc0.notion.site/FRD-CatalogPro-Enhanced-v2-9e20b04a516e4fa2a8bedb0fb18e4b7f\n\n")
        print("📥 Descargando contenido desde Notion...")
        fetch_children_recursive(client, FRD_PAGE_ID, file_handle=f)
    
    print(f"\n✅ FRD descargado exitosamente en: {OUTPUT_FILE}")
    print(f"📋 Este documento es ahora el SSOT (Single Source of Truth) para CatalogPro")

if __name__ == "__main__":
    fetch_frd()
