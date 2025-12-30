"""
Script to read the Antay Fábrica de Software methodology from Notion
"""
import os
import streamlit as st
from notion_client import Client
import json

# Setup Notion Client using Secrets
try:
    notion = Client(auth=st.secrets["NOTION_TOKEN"])
except Exception:
    # Fallback/Error handling if secret is missing
    print("Warning: NOTION_TOKEN not found in st.secrets")
    notion = None

PAGE_ID = "16a3c6146059806497fbf86d6349603d"

def extract_text_from_block(block):
    """Extract text content from a Notion block"""
    text_content = []
    block_type = block.get('type')
    
    if block_type in ['paragraph', 'heading_1', 'heading_2', 'heading_3', 'bulleted_list_item', 'numbered_list_item', 'quote', 'callout', 'toggle']:
        rich_text = block.get(block_type, {}).get('rich_text', [])
        for text_obj in rich_text:
            text_content.append(text_obj.get('plain_text', ''))
    
    return ''.join(text_content)

def read_blocks_recursively(client, block_id, level=0):
    """Recursively read all blocks and their children"""
    content = []
    
    try:
        blocks = client.blocks.children.list(block_id=block_id)
        
        for block in blocks.get('results', []):
            block_type = block.get('type')
            indent = "  " * level
            
            # Extract text
            text = extract_text_from_block(block)
            
            # Format based on block type
            if block_type == 'heading_1':
                content.append(f"\n{indent}# {text}")
            elif block_type == 'heading_2':
                content.append(f"\n{indent}## {text}")
            elif block_type == 'heading_3':
                content.append(f"\n{indent}### {text}")
            elif block_type == 'bulleted_list_item':
                content.append(f"{indent}- {text}")
            elif block_type == 'numbered_list_item':
                content.append(f"{indent}1. {text}")
            elif block_type == 'quote':
                content.append(f"{indent}> {text}")
            elif block_type == 'callout':
                content.append(f"{indent}📌 {text}")
            elif block_type == 'toggle':
                content.append(f"{indent}▶ {text}")
            elif text:
                content.append(f"{indent}{text}")
            
            # Check if block has children
            if block.get('has_children'):
                child_content = read_blocks_recursively(client, block['id'], level + 1)
                content.extend(child_content)
            
            # Check for child pages
            if block_type == 'child_page':
                page_title = block.get('child_page', {}).get('title', 'Untitled')
                content.append(f"\n{indent}📄 **Subpage: {page_title}**")
                child_content = read_blocks_recursively(client, block['id'], level + 1)
                content.extend(child_content)
    
    except Exception as e:
        content.append(f"{indent}[Error reading blocks: {str(e)}]")
    
    return content

def main():
    print("🔗 Conectando a Notion...")
    client = Client(auth=NOTION_TOKEN)
    
    # Get page metadata
    print(f"📖 Leyendo página: {PAGE_ID}")
    page = client.pages.retrieve(page_id=PAGE_ID)
    
    # Get page title
    title_property = page.get('properties', {}).get('title', {})
    title_text = ""
    if title_property.get('type') == 'title':
        title_array = title_property.get('title', [])
        if title_array:
            title_text = title_array[0].get('plain_text', 'Sin título')
    
    print(f"📄 Título: {title_text}\n")
    print("=" * 80)
    print(f"METODOLOGÍA ANTAY FÁBRICA DE SOFTWARE")
    print("=" * 80)
    print(f"\nTítulo de la página: {title_text}\n")
    
    # Read all blocks recursively
    print("📚 Leyendo contenido completo (incluyendo subpáginas)...\n")
    content = read_blocks_recursively(client, PAGE_ID)
    
    # Print content
    for line in content:
        print(line)
    
    print("\n" + "=" * 80)
    print("✅ Metodología Antay cargada exitosamente")
    print("=" * 80)
    
    # Save to file
    output_file = "antay_methodology.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"METODOLOGÍA ANTAY FÁBRICA DE SOFTWARE\n")
        f.write(f"{'=' * 80}\n\n")
        f.write(f"Título: {title_text}\n\n")
        f.write('\n'.join(content))
    
    print(f"\n💾 Metodología guardada en: {output_file}")

if __name__ == "__main__":
    main()
