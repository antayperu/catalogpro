"""
Script para actualizar ticket CP-UX-010 en Notion con información completa
"""
import requests
import streamlit as st

# Leer credenciales desde secrets.toml (NO hardcodear)
NOTION_TOKEN = st.secrets["notion"]["NOTION_TOKEN"]
PAGE_ID = "2377544a512b804db020d8e8b62fd00de7930fac5"  # ID del ticket creado

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# Actualizar el ticket con toda la información
url = f"https://api.notion.com/v1/pages/{PAGE_ID}"

# Descripción completa del ticket
descripcion = """Mejoras UX corporativas en tab Cargar:

CAMBIOS IMPLEMENTADOS:
✅ Título "Importar Datos" con microcopy explicativo
✅ Eliminados emojis decorativos (🗑️, 👀, 📋)
✅ Estructura de ejemplo en expander colapsado
✅ Mensajes de error descriptivos con contexto
✅ Spinners durante carga ("Importando datos...", "Validando estructura...")
✅ Labels profesionales en inputs
✅ Feedback con formato bold y captions explicativos

BENEFICIOS:
- Aspecto corporativo y profesional
- Mejor guía para el usuario
- Feedback claro en caso de error
- Reducción de ruido visual"""

criterios_aceptacion = """AC-01: Título "Importar Datos" con microcopy
AC-02: Cero emojis en botones y headers
AC-03: Estructura en expander colapsado
AC-04: Mensajes de error descriptivos
AC-05: Spinners durante carga
AC-06: Funcionalidad intacta"""

update_data = {
    "properties": {
        "Módulo": {
            "select": {
                "name": "UI/UX"
            }
        },
        "Descripción": {
            "rich_text": [
                {
                    "text": {
                        "content": descripcion
                    }
                }
            ]
        },
        "AC (Criterios de aceptación)": {
            "rich_text": [
                {
                    "text": {
                        "content": criterios_aceptacion
                    }
                }
            ]
        }
    }
}

try:
    response = requests.patch(url, headers=headers, json=update_data)
    
    if response.status_code == 200:
        print("✅ Ticket CP-UX-010 actualizado exitosamente en Notion")
        print(f"   Page ID: {PAGE_ID}")
        print("\n📋 Información agregada:")
        print("   - Módulo: UI/UX")
        print("   - Descripción completa con cambios y beneficios")
        print("   - Criterios de aceptación (6 items)")
    else:
        print(f"❌ Error al actualizar: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"❌ Error: {e}")
