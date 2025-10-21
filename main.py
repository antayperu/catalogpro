import streamlit as st
import pandas as pd
import requests
from PIL import Image, ImageDraw, ImageFont
import io
import base64
from datetime import datetime
import json
import os
from urllib.parse import urlparse, quote
import time
import re
import numpy as np
import math
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from auth import check_authentication, AuthManager
import time

__version__ = "1.2"

# Configuración de la página
st.set_page_config(
    page_title="CatalogPro",
    page_icon="assets/favicon_antay.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# CLASES AUXILIARES MEJORADAS v{__version__}
# =============================================================================

class DataHandler:
    """Clase para manejar la carga de datos desde diferentes fuentes"""
    
    def __init__(self):
        self.required_columns = ['ImagenURL', 'Producto', 'Descripción', 'Unidad', 'Precio']
        
    def load_excel(self, uploaded_file):
        """Cargar datos desde un archivo Excel"""
        try:
            df = pd.read_excel(uploaded_file)
            self._validate_columns(df)
            return df
        except Exception as e:
            raise Exception(f"Error al cargar archivo Excel: {str(e)}")
    
    def load_google_sheets(self, sheets_url):
        """Cargar datos desde Google Sheets"""
        try:
            csv_url = self._convert_sheets_url_to_csv(sheets_url)
            df = pd.read_csv(csv_url)
            self._validate_columns(df)
            return df
        except Exception as e:
            raise Exception(f"Error al cargar Google Sheets: {str(e)}")
    
    def _convert_sheets_url_to_csv(self, sheets_url):
        """Convertir URL de Google Sheets a formato CSV exportable"""
        sheet_id_match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', sheets_url)
        if not sheet_id_match:
            raise ValueError("URL de Google Sheets no válida")
        sheet_id = sheet_id_match.group(1)
        csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
        return csv_url
    
    def _validate_columns(self, df):
        """Validar que el DataFrame tenga las columnas requeridas"""
        missing_columns = []
        for col in self.required_columns:
            if col not in df.columns:
                missing_columns.append(col)
        if missing_columns:
            raise ValueError(f"Faltan las siguientes columnas: {', '.join(missing_columns)}")

class DataCleaner:
    """Clase para limpiar y validar datos del catálogo"""
    
    def clean_data(self, df):
        """Limpiar y validar datos del DataFrame"""
        cleaned_df = df.copy()
        cleaned_df = self._clean_basic_data(cleaned_df)
        cleaned_df = self._clean_prices(cleaned_df)
        cleaned_df = self._clean_image_urls(cleaned_df)
        cleaned_df = self._clean_text_fields(cleaned_df)
        cleaned_df = self._remove_invalid_rows(cleaned_df)
        return cleaned_df
        
    def _clean_basic_data(self, df):
        """Limpiar datos básicos"""
        df = df.dropna(how='all')
        df = df.reset_index(drop=True)
        return df
        
    def _clean_prices(self, df):
        """Limpiar y validar precios"""
        if 'Precio' not in df.columns:
            return df
        df['Precio'] = df['Precio'].astype(str).str.replace(',', '')
        df['Precio'] = pd.to_numeric(df['Precio'], errors='coerce')
        df = df[df['Precio'] > 0]
        return df
        
    def _clean_image_urls(self, df):
        """Limpiar URLs de imágenes"""
        if 'ImagenURL' not in df.columns:
            return df
        df['ImagenURL'] = df['ImagenURL'].astype(str).str.strip()
        df['ImagenURL'] = df['ImagenURL'].replace('nan', np.nan)
        return df
        
    def _clean_text_fields(self, df):
        """Limpiar campos de texto"""
        text_columns = ['Producto', 'Descripción', 'Unidad']
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()
                df[col] = df[col].str.replace(r'\s+', ' ', regex=True)
                df[col] = df[col].str.title()
                df[col] = df[col].replace('Nan', np.nan)
        return df
        
    def _remove_invalid_rows(self, df):
        """Eliminar filas con datos críticos faltantes"""
        required_fields = ['Producto', 'Precio']
        for field in required_fields:
            if field in df.columns:
                df = df.dropna(subset=[field])
        return df

class ImageManager:
    """Clase para manejar la descarga y procesamiento de imágenes"""
    
    def __init__(self):
        self.placeholder_image = self._generate_placeholder_image()
        self.image_cache = {}
        
    def download_image(self, image_url, max_size=(400, 400)):
        """Descargar imagen desde URL con caché"""
        if pd.isna(image_url) or not image_url or str(image_url) == 'nan':
            return self.placeholder_image
            
        cache_key = f"{image_url}_{max_size}"
        if cache_key in self.image_cache:
            return self.image_cache[cache_key]
            
        try:
            response = requests.get(str(image_url), timeout=10)
            response.raise_for_status()
            
            image = Image.open(io.BytesIO(response.content))
            
            if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            if image.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
                
            self.image_cache[cache_key] = image
            return image
            
        except Exception as e:
            return self.placeholder_image
            
    def _generate_placeholder_image(self):
        """Generar imagen placeholder para productos sin imagen"""
        width, height = 300, 300
        image = Image.new('RGB', (width, height), color='#f0f0f0')
        draw = ImageDraw.Draw(image)
        
        draw.rectangle([10, 10, width-10, height-10], outline='#cccccc', width=2)
        
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()
            
        text = "Sin imagen"
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        text_x = (width - text_width) // 2
        text_y = (height - text_height) // 2
        
        draw.text((text_x, text_y), text, fill='#999999', font=font)
        return image

class CatalogGenerator:
    """Clase para generar catálogos visuales de productos - MEJORADA v{__version__}"""
    
    def __init__(self):
        self.image_manager = ImageManager()
        
    def render_catalog(self, df, columns=3, currency="S/"):
        """Renderizar el catálogo de productos en Streamlit"""
        total_products = len(df)
        rows = math.ceil(total_products / columns)
        
        for row in range(rows):
            cols = st.columns(columns)
            for col_idx in range(columns):
                product_idx = row * columns + col_idx
                if product_idx < total_products:
                    product = df.iloc[product_idx]
                    with cols[col_idx]:
                        self._render_product_card(product, currency, product_idx, row)
                        
    def _render_product_card(self, product, currency, product_idx, row):
        with st.container():
            # Image handling
            image = self.image_manager.download_image(product['ImagenURL'])
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            st.markdown(f"<div class='product-image-container'><img src='data:image/png;base64,{img_str}' alt='{product['Producto']}'></div>", unsafe_allow_html=True)

            st.markdown(f"<div class='product-title'>{product['Producto']}</div>", unsafe_allow_html=True)
            full_description = str(product['Descripción'])
            display_description = full_description[:80] + ('...' if len(full_description) > 80 else '')
            st.markdown(f"<div class='product-description' title='{full_description}'>{display_description}</div>", unsafe_allow_html=True)

            st.markdown("<div class='product-footer'>", unsafe_allow_html=True)
            st.markdown(f"<span class='product-unit'>Por {product['Unidad']}</span>", unsafe_allow_html=True)
            st.markdown(f"<span class='product-price'>{currency} {product['Precio']:.2f}</span>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            # Section for entrepreneur actions
            with st.expander("Compartir con Cliente"):
                st.markdown("##### Enviar a un cliente específico")
                
                # WhatsApp message customization
                default_message = f"Estimado cliente, le hago llegar información del producto: {product['Producto']} - Precio: {currency} {product['Precio']:.2f}. Quedo a su disposición para cualquier consulta."
                whatsapp_message = st.text_area("Mensaje de WhatsApp:", default_message, key=f"wa_msg_{row}_{product_idx}", height=150)
                
                if st.button("Generar Enlace de WhatsApp", key=f"send_wa_{row}_{product_idx}", use_container_width=True):
                    if whatsapp_message:
                        whatsapp_url = f"https://wa.me/?text={quote(whatsapp_message)}"
                        st.markdown(f'<a href="{whatsapp_url}" target="_blank" style="display:inline-block;padding:0.5rem 1rem;background-color:#25D366;color:white;border-radius:25px;text-decoration:none;">Abrir WhatsApp para Enviar</a>', unsafe_allow_html=True)
                    else:
                        st.warning("El mensaje no puede estar vacío.")

                st.markdown("---")
                
                # Add to email selection
                if st.button("Añadir a Selección de Email", key=f"add_em_{row}_{product_idx}", use_container_width=True):
                    if 'email_products' not in st.session_state:
                        st.session_state.email_products = []

                    product_dict = product.to_dict()
                    if not any(p['Producto'] == product_dict['Producto'] for p in st.session_state.email_products):
                        st.session_state.email_products.append(product_dict)
                        st.success(f"✅ ¡{product['Producto']} añadido a la selección de email!")
                    else:
                        st.info(f"ℹ️ {product['Producto']} ya estaba en la selección.")

        st.markdown("---")
class EnhancedPDFExporter:
    """Clase mejorada para exportar catálogos a PDF con imágenes"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.image_manager = ImageManager()
        
    def generate_pdf_with_images(self, df, business_name, currency):
        """Generar PDF del catálogo con imágenes de productos"""
        buffer = io.BytesIO()
        
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=50,
            leftMargin=50,
            topMargin=50,
            bottomMargin=50
        )
        
        story = []
        story.extend(self._create_enhanced_header(business_name))
        story.extend(self._create_enhanced_catalog_info(df, currency))
        story.extend(self._create_enhanced_product_cards(df, currency))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
        
    def _create_enhanced_header(self, business_name):
        """Crear header mejorado del PDF"""
        story = []
        
        if hasattr(st.session_state, 'logo') and st.session_state.logo is not None:
            try:
                logo_image = Image.open(st.session_state.logo)
                logo_buffer = io.BytesIO()
                logo_image.save(logo_buffer, format='PNG')
                logo_buffer.seek(0)
                pdf_logo = RLImage(logo_buffer, width=2.5*inch, height=1.2*inch)
                story.append(pdf_logo)
                story.append(Spacer(1, 15))
            except:
                pass
        
        title_style = ParagraphStyle(
            name='EnhancedTitle',
            parent=self.styles['Title'],
            fontSize=28,
            spaceAfter=25,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2c3e50'),
            fontName='Helvetica-Bold'
        )
        
        subtitle_style = ParagraphStyle(
            name='EnhancedSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#7f8c8d'),
            fontName='Helvetica'
        )
        
        story.append(Paragraph(business_name, title_style))
        story.append(Paragraph("Catálogo de Productos Profesional", subtitle_style))
        story.append(Spacer(1, 10))
        
        return story
        
    def _create_enhanced_catalog_info(self, df, currency):
        """Crear información del catálogo"""
        story = []
        
        info_style = ParagraphStyle(
            name='CatalogInfo',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=25,
            leftIndent=20,
            rightIndent=20,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#34495e')
        )
        
        info_text = f"""
        <b>Fecha:</b> {datetime.now().strftime('%d/%m/%Y')}<br/>
        <b>Total:</b> {len(df)} productos<br/>
        <b>Moneda:</b> {currency}<br/>
        <b>Promedio:</b> {currency} {df['Precio'].mean():.2f}
        """
        
        story.append(Paragraph(info_text, info_style))
        story.append(Spacer(1, 20))
        
        return story
        
    def _create_enhanced_product_cards(self, df, currency):
        """Crear tarjetas de productos mejoradas"""
        story = []
        
        products_per_page = 6
        total_products = len(df)
        
        for page_start in range(0, total_products, products_per_page):
            page_end = min(page_start + products_per_page, total_products)
            page_products = df.iloc[page_start:page_end]
            
            product_data = []
            for i in range(0, len(page_products), 2):
                row_data = []
                
                product1 = page_products.iloc[i]
                product1_cell = self._create_enhanced_product_cell(product1, currency)
                row_data.append(product1_cell)
                
                if i + 1 < len(page_products):
                    product2 = page_products.iloc[i + 1]
                    product2_cell = self._create_enhanced_product_cell(product2, currency)
                    row_data.append(product2_cell)
                else:
                    row_data.append("")
                
                product_data.append(row_data)
            
            if product_data:
                products_table = Table(product_data, colWidths=[4*inch, 4*inch])
                products_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 15),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 15),
                    ('TOPPADDING', (0, 0), (-1, -1), 15),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 25),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#ecf0f1')),
                ]))
                
                story.append(products_table)
                story.append(Spacer(1, 20))
                
                if page_end < total_products:
                    story.append(PageBreak())
        
        return story
        
    def _create_enhanced_product_cell(self, product, currency):
        """Crear celda de producto mejorada"""
        product_image = None
        try:
            image = self.image_manager.download_image(product['ImagenURL'], max_size=(300, 300))
            img_buffer = io.BytesIO()
            image.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            product_image = RLImage(img_buffer, width=2*inch, height=2*inch)
        except:
            pass
        
        title_style = ParagraphStyle(
            name='ProductTitle',
            parent=self.styles['Normal'],
            fontSize=14,
            spaceAfter=8,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2c3e50'),
            fontName='Helvetica-Bold'
        )
        
        desc_style = ParagraphStyle(
            name='ProductDesc',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=8,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#7f8c8d'),
            fontName='Helvetica'
        )
        
        price_style = ParagraphStyle(
            name='ProductPrice',
            parent=self.styles['Normal'],
            fontSize=16,
            spaceAfter=5,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#e74c3c'),
            fontName='Helvetica-Bold'
        )
        
        unit_style = ParagraphStyle(
            name='ProductUnit',
            parent=self.styles['Normal'],
            fontSize=9,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#95a5a6'),
            fontName='Helvetica'
        )
        
        cell_data = []
        
        if product_image:
            cell_data.append([product_image])
        
        cell_data.append([Paragraph(f"<b>{product['Producto']}</b>", title_style)])
        
        description = str(product['Descripción'])[:80] + ('...' if len(str(product['Descripción'])) > 80 else '')
        cell_data.append([Paragraph(f"<i>{description}</i>", desc_style)])
        
        cell_data.append([Paragraph(f"{currency} {product['Precio']:.2f}", price_style)])
        cell_data.append([Paragraph(f"Por {product['Unidad']}", unit_style)])
        
        inner_table = Table(cell_data, colWidths=[3.5*inch])
        inner_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        return inner_table

class SimpleEmailMarketing:
    """Clase simplificada para email marketing usando mailto:"""
    
    def __init__(self):
        self.templates = self._load_email_templates()
        
    def _load_email_templates(self):
        """Cargar plantillas de email predefinidas"""
        return {
            'catalogo_completo': {
                'subject': 'Catálogo - {business_name}',
                'body': '''Estimado cliente,

Catálogo actualizado de productos.

Total: {total_products}
Moneda: {currency}
Fecha: {fecha}

Adjunto PDF con detalles.

Saludos,
{business_name}'''
            },
            'productos_seleccionados': {
                'subject': 'Productos de Interés - {business_name}',
                'body': '''Estimado cliente,

Productos seleccionados:

{product_list}

Saludos,
{business_name}'''
            }
        }
    
    def generate_mailto_url(self, to_email, business_name, df, currency, template_type='catalogo_completo', selected_products=None):
        """Generar URL mailto con email pre-completado"""
        template = self.templates[template_type]
        
        template_vars = {
            'business_name': business_name,
            'total_products': len(df),
            'currency': currency,
            'fecha': datetime.now().strftime('%d/%m/%Y'),
            'product_list': self._format_product_list(selected_products, currency) if selected_products else ""
        }
        
        subject = template['subject'].format(**template_vars)
        body = template['body'].format(**template_vars)
        
        mailto_url = f"mailto:{to_email}?subject={quote(subject)}&body={quote(body)}"
        
        return mailto_url
    
    def _format_product_list(self, products, currency):
        """Formatear lista de productos para email"""
        if not products:
            return ""
        
        formatted_list = ""
        for i, product in enumerate(products, 1):
            formatted_list += f"{i}. {product['Producto']}\n"
            formatted_list += f"   Precio: {currency} {product['Precio']:.2f}\n\n"
        
        return formatted_list.strip()

class HTMLExporter:
    """Clase para exportar catálogos a HTML completo"""
    
    def __init__(self):
        self.image_manager = ImageManager()
        
    def generate_html_catalog(self, df, business_name, currency, phone_number):
        """Generar catálogo HTML completo"""
        
        html_template = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{business_name} - Catálogo</title>
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{ font-family: Arial, sans-serif; background: #f8f9fa; }}
                .container {{ max-width: 1200px; margin: 0 auto; padding: 0 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 2rem 0; text-align: center; }}
                .header h1 {{ font-size: 2.5rem; margin-bottom: 0.5rem; }}
                .main {{ padding: 2rem 0; }}
                .catalog-info {{ background: white; padding: 1.5rem; border-radius: 10px; margin-bottom: 2rem; }}
                .product-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; }}
                .product-card {{ background: white; border-radius: 15px; padding: 1.5rem; box-shadow: 0 4px 15px rgba(0,0,0,0.1); transition: transform 0.3s; }}
                .product-card:hover {{ transform: translateY(-5px); box-shadow: 0 8px 25px rgba(0,0,0,0.15); }}
                .product-image {{ width: 100%; height: 200px; object-fit: cover; border-radius: 10px; margin-bottom: 1rem; }}
                .product-title {{ font-size: 1.3rem; font-weight: bold; color: #2c3e50; margin-bottom: 0.5rem; }}
                .product-description {{ color: #7f8c8d; margin-bottom: 1rem; }}
                .product-footer {{ display: flex; justify-content: space-between; align-items: center; }}
                .product-price {{ font-size: 1.4rem; font-weight: bold; color: #e74c3c; }}
                .whatsapp-btn {{ display: inline-block; background: #25d366; color: white; padding: 0.5rem 1rem; border-radius: 25px; text-decoration: none; font-weight: bold; margin-top: 1rem; }}
                .footer {{ background: #2c3e50; color: white; text-align: center; padding: 1rem 0; margin-top: 3rem; }}
                @media (max-width: 768px) {{ .product-grid {{ grid-template-columns: 1fr; }} }}
            </style>
        </head>
        <body>
            <header class="header">
                <div class="container">
                    <h1>{business_name}</h1>
                    <p>Catálogo Digital</p>
                </div>
            </header>
            <main class="main">
                <div class="container">
                    <div class="catalog-info">
                        <p><strong>Fecha:</strong> {datetime.now().strftime('%d/%m/%Y')}</p>
                        <p><strong>Total:</strong> {len(df)} productos</p>
                        <p><strong>Moneda:</strong> {currency}</p>
                    </div>
                    <div class="product-grid">
                        {self._generate_product_cards_html(df, currency, phone_number)}
                    </div>
                </div>
            </main>
            <footer class="footer">
                <div class="container">
                    <p>© 2025 {business_name}</p>
                </div>
            </footer>
        </body>
        </html>
        """
        
        return html_template
    
    def _generate_product_cards_html(self, df, currency, phone_number):
        """Generar tarjetas de productos en HTML"""
        cards_html = ""
        
        for _, product in df.iterrows():
            image_url = product['ImagenURL']
            if pd.isna(image_url) or not image_url or str(image_url) == 'nan':
                image_src = "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHJlY3Qgd2lkdGg9IjEwMCUiIGhlaWdodD0iMTAwJSIgZmlsbD0iI2YwZjBmMCIvPgo8dGV4dCB4PSI1MCUiIHk9IjUwJSIgZm9udC1mYW1pbHk9IkFyaWFsIiBmb250LXNpemU9IjE4IiBmaWxsPSIjOTk5IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkeT0iLjNlbSI+U2luIGltYWdlbjwvdGV4dD4KPC9zdmc+"
            else:
                image_src = str(image_url)
            
            whatsapp_message = f"Hola! Me interesa: {product['Producto']} - {currency} {product['Precio']:.2f}"
            whatsapp_url = f"https://wa.me/{phone_number}?text={quote(whatsapp_message)}" if phone_number else f"https://wa.me/?text={quote(whatsapp_message)}"
            
            card_html = f"""
            <div class="product-card">
                <img src="{image_src}" alt="{product['Producto']}" class="product-image">
                <div class="product-title">{product['Producto']}</div>
                <div class="product-description">{product['Descripción']}</div>
                <div class="product-footer">
                    <span>Por {product['Unidad']}</span>
                    <span class="product-price">{currency} {product['Precio']:.2f}</span>
                </div>
                <a href="{whatsapp_url}" class="whatsapp-btn" target="_blank">💬 Consultar</a>
            </div>
            """
            
            cards_html += card_html
        
        return cards_html
    # =============================================================================
# PARTE 2: APLICACIÓN PRINCIPAL v{__version__} - COPIAR DESPUÉS DE PARTE 1
# =============================================================================

# NOTA IMPORTANTE: Este código va DESPUÉS de toda la Parte 1 en main.py
# La Parte 1 contiene todas las clases auxiliares
# Esta Parte 2 contiene solo la clase EnhancedCatalogApp y el if __name__

# =============================================================================
# CLASE PRINCIPAL MEJORADA
# =============================================================================

class CatalogProApp:
    """Aplicación principal con mejoras UX/UI v{__version__}"""
    
    def __init__(self):
        self.data_handler = DataHandler()
        self.catalog_generator = CatalogGenerator()
        self.pdf_exporter = EnhancedPDFExporter()
        self.data_cleaner = DataCleaner()
        self.email_marketing = SimpleEmailMarketing()
        self.html_exporter = HTMLExporter()

        if 'df' not in st.session_state:
            st.session_state.df = None
        if 'data_sources' not in st.session_state:
            st.session_state.data_sources = []
        if 'email_products' not in st.session_state:
            st.session_state.email_products = []
        if 'viewed_catalog' not in st.session_state:
            st.session_state.viewed_catalog = False
        if 'exported' not in st.session_state:
            st.session_state.exported = False
        if 'logo' not in st.session_state:
            st.session_state.logo = None
        if 'auth_manager' not in st.session_state:
            st.session_state.auth_manager = None
        
    def run(self):
        # PRIMERO: Verificar autenticación
        auth = check_authentication()
        self.auth_manager = auth # Assign to instance attribute
        st.session_state.auth_manager = auth # Also keep in session_state for other uses
        
        # Calcular is_admin una sola vez
        is_admin = False
        if st.session_state.get("authenticated"):
            is_admin = auth.is_admin(st.session_state.user_email)

        # DESPUÉS: Continuar normal
        self.setup_styles()
        self.render_header()
        self.render_sidebar(is_admin)
        self.render_main_content(is_admin)

    def _update_user_setting(self, setting_key, new_value):
        """Helper to update a single user setting and save it."""
        if st.session_state.authenticated and st.session_state.user_email:
            user_email = st.session_state.user_email
            user_info = st.session_state.user_info

            # Update the specific setting in user_info
            user_info[setting_key] = new_value
            st.session_state.user_info = user_info # Update session state

            # Call AuthManager to persist the change
            self.auth_manager.update_user_settings(
                user_email,
                user_info.get('business_name', ''),
                user_info.get('currency', 'S/'),
                user_info.get('phone_number', '')
            )
            st.session_state.auth_manager = self.auth_manager # Update auth_manager in session state
        
    def setup_styles(self):
        """Estilos CSS mejorados"""
        st.markdown("""
        <style>
        .main-header {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 10px;
            margin-bottom: 1rem;
            text-align: center;
        }
        .main-header h1 {
            color: white;
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }
        .main-header p {
            color: #f0f0f0;
            font-size: 1.2rem;
        }
        .feature-badge, .easy-badge, .ux-badge {
            color: white;
            padding: 0.3rem 0.6rem;
            border-radius: 15px;
            font-size: 0.8rem;
            font-weight: bold;
            margin-left: 0.5rem;
        }
        .feature-badge {
            background: linear-gradient(45deg, #ff6b6b, #ee5a24);
        }
        .easy-badge {
            background: linear-gradient(45deg, #2ecc71, #27ae60);
        }
        .ux-badge {
            background: linear-gradient(45deg, #3498db, #2980b9);
        }
        .progress-step {
            text-align: center;
            padding: 1rem;
            border-radius: 8px;
            background: #f8f9fa;
        }
        .progress-step.completed {
            background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);
            color: white;
        }
        .progress-step.active {
            background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
            color: white;
        }
        .filter-chip {
            display: inline-block;
            background: #e3f2fd;
            color: #1976d2;
            padding: 6px 12px;
            border-radius: 16px;
            margin: 4px;
            font-size: 0.9rem;
        }
        .empty-state {
            text-align: center;
            padding: 4rem 2rem;
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border-radius: 16px;
            margin: 2rem 0;
        }
        .stButton > button {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 5px;
            padding: 0.5rem 1rem;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        /* Estilos de las tarjetas de productos basados en el exportador HTML */
        .product-card {
            background: white;
            border-radius: 15px;
            padding: 1.5rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s;
            height: 100%; /* Asegura que las tarjetas en una fila tengan la misma altura */
            display: flex;
            flex-direction: column;
        }
        .product-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }
        .product-image-container {
            width: 100%;
            height: 200px; /* Fixed height for all images */
            overflow: hidden; /* Hide parts of the image that are cropped */
            border-radius: 10px; /* Rounded corners for the container */
            margin-bottom: 1rem;
        }
        .product-image-container img {
            width: 100%;
            height: 100%;
            object-fit: cover; /* Crop to fill the container */
            object-position: center; /* Center the cropped image */
        }
        .product-title {
            font-size: 1.3rem;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 0.5rem;
        }
        .product-description {
            color: #7f8c8d;
            font-size: 0.9rem;
            margin-bottom: 1rem;
            flex-grow: 1; /* Permite que la descripción ocupe el espacio disponible */
        }
        .product-footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: auto; /* Empuja el footer hacia abajo */
        }
        .product-price {
            font-size: 1.4rem;
            font-weight: bold;
            color: #e74c3c;
        }
        .product-unit {
            font-size: 0.8rem;
            color: #95a5a6;
        }
        .product-actions-container {
            display: flex;
            gap: 0.5rem;
            margin-top: 1rem;
        }
        .stButton > button.whatsapp-button {
            background: #25d366; /* WhatsApp green */
            color: white;
            border-radius: 25px;
            padding: 0.5rem 1rem;
            font-weight: bold;
            border: none;
            transition: background 0.2s;
        }
        .stButton > button.whatsapp-button:hover {
            background: #1da851;
        }
        .stButton > button.email-button {
            background: #3498db; /* Streamlit blue */
            color: white;
            border-radius: 25px;
            padding: 0.5rem 1rem;
            font-weight: bold;
            border: none;
            transition: background 0.2s;
        }
        .stButton > button.email-button:hover {
            background: #2980b9;
        }
        </style>
        """, unsafe_allow_html=True)
        
    def render_header(self):
        st.markdown(f"""
        <div class="main-header">
            <h1>CatalogPro</h1>
            <p>Tu solución profesional para catálogos digitales</p>
            <p>by Antay Perú</p>
            <span class="feature-badge">v{__version__}</span>
            <span class="feature-badge">PDF</span>
            <span class="easy-badge">Email Fácil</span>
        </div>
        """, unsafe_allow_html=True)
    
    def render_sidebar(self, is_admin):
        st.sidebar.header("📊 Configuración")
        
        # Get user info from session state
        user_info = st.session_state.user_info if st.session_state.authenticated else {}

        with st.sidebar.expander("🏢 Negocio", expanded=True):
            # Business Name
            current_biz_name = user_info.get('business_name', 'Mi Empresa')
            business_name = st.text_input(
                "Nombre", 
                value=current_biz_name, 
                key="biz",
                on_change=lambda: self._update_user_setting('business_name', st.session_state.biz)
            )

            # Currency
            currencies = ["S/", "$", "€", "£"]
            current_currency = user_info.get('currency', 'S/')
            currency_index = currencies.index(current_currency) if current_currency in currencies else 0
            currency = st.selectbox(
                "Moneda", 
                currencies, 
                index=currency_index, 
                key="cur",
                on_change=lambda: self._update_user_setting('currency', st.session_state.cur)
            )

            # Phone Number
            current_phone_number = user_info.get('phone_number', '')
            phone_number = st.text_input(
                "Número de WhatsApp", 
                value=current_phone_number, 
                placeholder="Ej: 51987654321", 
                key="phone",
                on_change=lambda: self._update_user_setting('phone_number', st.session_state.phone)
            )

        with st.sidebar.expander("🎨 Diseño", expanded=False):
            columns = st.slider("Columnas", 1, 4, 3, key="col")
            uploaded_logo = st.file_uploader("Logo", type=['png','jpg','jpeg'], key="log")
            if uploaded_logo:
                st.image(uploaded_logo, width=200)
                st.session_state.logo = uploaded_logo
            else:
                st.session_state.logo = None
        
        # Update session state with current values (even if not changed, for consistency)
        st.session_state.business_name = business_name
        st.session_state.currency = currency
        st.session_state.columns = columns
        st.session_state.phone_number = phone_number
        
        if 'df' in st.session_state and st.session_state.df is not None:
            with st.sidebar.expander("📈 Stats", expanded=True):
                df = st.session_state.df
                st.metric("Total", len(df))
                st.metric("Promedio", f"{currency} {df['Precio'].mean():.2f}")
                
    def render_main_content(self, is_admin):
        if is_admin:
            tabs_list = ["📊 Cargar", "👀 Preview", "📄 Exportar", 
                         "📧 Email", "👨‍💼 Admin", "ℹ️ Ayuda"]
            tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(tabs_list)
        else:
            tabs_list = ["📊 Cargar", "👀 Preview", "📄 Exportar", 
                         "📧 Email", "ℹ️ Ayuda"]
            tab1, tab2, tab3, tab4, tab5 = st.tabs(tabs_list)
        
        with tab1:
            self.render_data_loading()
        with tab2:
            self.render_catalog()
        with tab3:
            self.render_export_options()
        with tab4:
            self.render_simple_email_marketing()
        
        if is_admin:
            with tab5:
                self.render_admin_panel()
            with tab6:
                self.render_help()
        else:
            with tab5:
                self.render_help()
    
    def render_empty_state(self, tipo, context=''):
        states = {
            'no_data': ('📦', 'Vacío', 'Carga productos', '📊 Cargar'),
            'no_results': ('🔍', 'Sin resultados', 'Ajusta filtros', '🗑️ Limpiar'),
            'no_email_products': ('📧', 'Sin selección', 'Ve a Preview', '👀 Preview')
        }
        icon, title, desc, btn = states[tipo]
        st.markdown(f'<div class="empty-state"><div style="font-size:4rem">{icon}</div><h2>{title}</h2><p style="color:#7f8c8d">{desc}</p></div>', unsafe_allow_html=True)
        if st.button(btn, use_container_width=True, type="primary", key=f"es_{tipo}_{context}_{id(self)}"):
            st.info("💡 Usa tabs arriba")
    
    def render_active_filters(self, search, price_range, unit, min_p, max_p):
        filters = []
        if search:
            filters.append(('', f"'{search}'"))
        if price_range != (min_p, max_p):
            filters.append(('', f"{price_range[0]:.0f}-{price_range[1]:.0f}"))
        if unit != 'Todos':
            filters.append(('', unit))
        
        if filters:
            st.markdown("**Filtros activos:**")
            html = ""
            for icon, label in filters:
                html += f'<span class="filter-chip">{icon} {label}</span>'
            st.markdown(html, unsafe_allow_html=True)
            if st.button("Limpiar", key="clf"):
                st.rerun()
            st.markdown("---")
    
    def render_data_loading_with_progress(self, df, cleaned_df, source):
        progress = st.progress(0)
        status = st.empty()
        
        try:
            status.text("🧹 Limpiando...")
            progress.progress(33)
            time.sleep(0.3)
            
            status.text("🔄 Combinando...")
            progress.progress(66)
            
            if 'df' in st.session_state and st.session_state.df is not None:
                dupes = cleaned_df[cleaned_df['Producto'].isin(st.session_state.df['Producto'])]
                if len(dupes) > 0:
                    st.warning(f"{len(dupes)} duplicados")
                
                combined = pd.concat([st.session_state.df, cleaned_df], ignore_index=True)
                combined = combined.drop_duplicates(subset=['Producto'], keep='last')
                st.session_state.df = combined
                
                if 'data_sources' not in st.session_state:
                    st.session_state.data_sources = []
                st.session_state.data_sources.append(source)
                
                status.text("✅ Completado!")
                progress.progress(100)
                time.sleep(0.5)
                progress.empty()
                status.empty()
                st.success(f"Total: {len(combined)} ({len(cleaned_df)} nuevos)")
            else:
                st.session_state.df = cleaned_df
                st.session_state.data_sources = [source]
                status.text("✅ Completado!")
                progress.progress(100)
                time.sleep(0.5)
                progress.empty()
                status.empty()
                st.success(f"{len(cleaned_df)} productos")
        except Exception as e:
            progress.empty()
            status.empty()
            raise e
            
    def render_data_loading(self):
        st.header("Cargar Datos")
        
        if 'df' in st.session_state and st.session_state.df is not None:
            c1, c2 = st.columns([3, 1])
            with c2:
                if st.button("🗑️ Limpiar", type="secondary", key="cld"):
                    st.session_state.df = None
                    st.session_state.data_sources = []
                    st.success("✅ Limpiado!")
                    st.rerun()
            with c1:
                st.info(f"{len(st.session_state.df)} productos")
        
        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader("Excel")
            file = st.file_uploader("Archivo .xlsx", type=['xlsx'], key="exc")
            
            if file:
                try:
                    df = self.data_handler.load_excel(file)
                    cleaned = self.data_cleaner.clean_data(df)
                    self.render_data_loading_with_progress(df, cleaned, f"Excel: {file.name}")
                    
                    st.subheader("👀 Preview")
                    display = st.session_state.df.tail(5).copy()
                    display['Descripción'] = display['Descripción'].apply(lambda x: str(x)[:60]+'...' if len(str(x))>60 else str(x))
                    st.dataframe(display, use_container_width=True)
                except Exception as e:
                    st.error(f"❌ {str(e)}")
                    
        with c2:
            st.subheader("Google Sheets")
            url = st.text_input("URL", key="gurl")
            
            if st.button("Cargar", key="gld"):
                if url:
                    try:
                        df = self.data_handler.load_google_sheets(url)
                        cleaned = self.data_cleaner.clean_data(df)
                        self.render_data_loading_with_progress(df, cleaned, "Sheets")
                        
                        st.subheader("👀 Preview")
                        display = st.session_state.df.tail(5).copy()
                        display['Descripción'] = display['Descripción'].apply(lambda x: str(x)[:60]+'...' if len(str(x))>60 else str(x))
                        st.dataframe(display, use_container_width=True)
                    except Exception as e:
                        st.error(f"❌ {str(e)}")
                else:
                    st.warning("URL requerida")
        
        st.subheader("📋 Estructura")
        ex = pd.DataFrame({
            'ImagenURL': ['https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=300'],
            'Producto': ['Aceite'],
            'Descripción': ['1L'],
            'Unidad': ['Unidad'],
            'Precio': [10.50]
        })
        st.dataframe(ex, use_container_width=True)
        
    def render_catalog(self):
        st.header("Vista Previa")

        if 'df' in st.session_state and st.session_state.df is not None:
            st.session_state.viewed_catalog = True
            df = st.session_state.df

            c1, c2 = st.columns(2)
            with c1:
                if st.button("Limpiar email", key="cle"):
                    st.session_state.email_products = []
                    st.success("✅!")
            with c2:
                if 'email_products' in st.session_state and st.session_state.email_products:
                    st.info(f"{len(st.session_state.email_products)}")

            st.subheader("Filtros")
            c1, c2, c3 = st.columns(3)

            with c1:
                search = st.text_input("Buscar", key="srch")
            with c2:
                minp = float(df['Precio'].min())
                maxp = float(df['Precio'].max())
                if minp == maxp:
                    st.info(f"💰 {st.session_state.currency} {minp:.2f}")
                    prange = (minp, maxp)
                else:
                    prange = st.slider("Precio", minp, maxp, (minp, maxp), key="pr")
            with c3:
                units = ['Todos'] + list(df['Unidad'].unique())
                unit = st.selectbox("Unidad", units, key="un")

            self.render_active_filters(search, prange, unit, minp, maxp)

            filtered = df.copy()
            if search:
                filtered = filtered[filtered['Producto'].str.contains(search, case=False, na=False) | filtered['Descripción'].str.contains(search, case=False, na=False)]
            filtered = filtered[(filtered['Precio']>=prange[0]) & (filtered['Precio']<=prange[1])]
            if unit != 'Todos':
                filtered = filtered[filtered['Unidad']==unit]

            if len(filtered) == 0:
                self.render_empty_state('no_results', 'catalog_tab_no_results')
                return

            st.info(f"{len(filtered)} de {len(df)}")

            if len(filtered) < len(df):
                if st.button(f"Exportar {len(filtered)} Filtrados", key="exf"):
                    with st.spinner("..."):
                        pdf = self.pdf_exporter.generate_pdf_with_images(filtered, st.session_state.business_name, st.session_state.currency)
                        st.download_button("Descargar", pdf, f"filtrado_{datetime.now().strftime('%Y%m%d')}.pdf", "application/pdf", key="dlf")
                        st.success("¡Email listo en tu cliente de correo!")
                st.markdown("---")

            self.catalog_generator.render_catalog(filtered, st.session_state.columns, st.session_state.currency)
        else:
            self.render_empty_state('no_data', 'catalog_tab_no_df')
        
    def render_export_options(self):
        st.header("Exportar")
        
        if 'df' not in st.session_state or st.session_state.df is None:
            self.render_empty_state('no_data', 'export_tab_no_df')
            return
            
        df = st.session_state.df
        
        st.subheader("Selecciona el Formato de Exportación")
        c1, c2 = st.columns(2)
        with c1:
            st.info("**PDF:** Email, imprimir")
        with c2:
            st.info("**HTML:** Web, redes")
        st.markdown("---")
        
        c1, c2, c3 = st.columns(3)
        
        with c1:
            st.subheader("PDF")
            if st.button("Generar PDF", key="gpdf"):
                try:
                    with st.spinner("Generando PDF..."):
                        pdf = self.pdf_exporter.generate_pdf_with_images(df, st.session_state.business_name, st.session_state.currency)
                        st.download_button("Descargar PDF", pdf, f"catalogo_{datetime.now().strftime('%Y%m%d')}.pdf", "application/pdf", key="dlp") 
                        st.session_state.exported = True
                        st.success("¡PDF generado con éxito!")
                except Exception as e:
                    st.error(f"Error al generar PDF: {str(e)}")
                    
        with c2:
            st.subheader("HTML")
            if st.button("Generar HTML", key="ghml"):
                try:
                    with st.spinner("..."):
                        html = self.html_exporter.generate_html_catalog(df, st.session_state.business_name, st.session_state.currency, st.session_state.get('phone_number'))
                        st.download_button("📥 Descargar", html.encode('utf-8'), f"catalogo_{datetime.now().strftime('%Y%m%d')}.html", "text/html", key="dlh")
                        st.session_state.exported = True
                        st.success("¡HTML generado con éxito!")
                except Exception as e:
                    st.error(f"❌ {str(e)}")
                    
        with c3:
            st.subheader("Resumen")
            st.metric("Total", len(df))
            st.metric("Promedio", f"{st.session_state.currency} {df['Precio'].mean():.2f}")
            
    def render_simple_email_marketing(self):
        st.header("Email")
        
        if 'df' not in st.session_state or st.session_state.df is None:
            self.render_empty_state('no_data', 'email_tab_no_df')
            return
            
        df = st.session_state.df
        st.info("¡Funcionalidad de email lista para usar!")
        
        to_email = st.text_input("Email del Destinatario", key="toe")
        email_type = st.selectbox("Tipo", ["catalogo_completo", "productos_seleccionados"], format_func=lambda x: "Completo" if x=="catalogo_completo" else "Seleccionados", key="ety")
        
        if email_type == "productos_seleccionados":
            if 'email_products' in st.session_state and st.session_state.email_products:
                st.write(f"{len(st.session_state.email_products)}")
            else:
                self.render_empty_state('no_email_products', 'email_tab_no_products')
        
        c1_1, c1_2 = st.columns(2)
        
        with c1_1:
            if st.button("Descargar PDF", disabled=not to_email, key="pem"):
                try:
                    with st.spinner("..."):
                        pdf = self.pdf_exporter.generate_pdf_with_images(df, st.session_state.business_name, st.session_state.currency)
                        st.download_button("Descargar PDF", pdf, f"catalogo_{datetime.now().strftime('%Y%m%d')}.pdf", "application/pdf", key="dlem")
                        st.success("¡PDF descargado con éxito!")
                except Exception as e:
                    st.error(f"❌ {str(e)}")
        
        with c1_2:
            if st.button("Abrir en Cliente de Email", disabled=not to_email, key="oem"):
                try:
                    sel = None
                    if email_type == "productos_seleccionados" and 'email_products' in st.session_state:
                        sel = st.session_state.email_products
                    
                    mailto = self.email_marketing.generate_mailto_url(to_email, st.session_state.business_name, df, st.session_state.currency, email_type, sel)
                    st.markdown(f'<a href="{mailto}" target="_blank" style="background:#3498db;color:white;padding:10px 20px;border-radius:25px;text-decoration:none;display:inline-block">Abrir Email</a>', unsafe_allow_html=True)
                    st.info("Usa enlace si no abre")
                    st.success("¡Email listo en tu cliente de correo!")
                    if 'email_products' in st.session_state:
                        st.session_state.email_products = []
                except Exception as e:
                    st.error(f"❌ {str(e)}")
        

                    
    def render_help(self):
        st.header("Guía de Usuario de CatalogPro")
        st.markdown("¡Bienvenido! Esta guía te ayudará a sacar el máximo provecho de CatalogPro.")

        st.markdown("---")

        # --- Guía General ---
        st.subheader("Pasos Principales")

        with st.expander("Paso 1: Iniciar Sesión", expanded=True):
            st.markdown("""
            Para acceder a la aplicación, simplemente ingresa tu **email y contraseña** autorizados. 
            
            Si no tienes acceso, contacta al administrador de la cuenta (verás su correo en la pantalla de login).
            """)

        with st.expander("Paso 2: Configurar tu Negocio", expanded=False):
            st.markdown("""
            Antes de crear tu catálogo, personalízalo con tu marca desde la **barra lateral izquierda**. Estas opciones aparecerán en todos tus catálogos exportados.

            *   **🏢 Negocio:**
                *   **Nombre:** El nombre de tu empresa.
                *   **Moneda:** El símbolo de la moneda que usas (S/, $, €, etc.).
                *   **Número de WhatsApp:** Tu número de contacto para que los clientes puedan consultarte desde el catálogo HTML.

            *   **🎨 Diseño:**
                *   **Columnas:** Define cuántos productos se mostrarán por fila en la `Vista Previa`.
                *   **Logo:** Sube el logo de tu empresa. Aparecerá en la cabecera de tus catálogos en PDF, dándoles un toque más profesional.
            """)

        with st.expander("Paso 3: Cargar Tus Productos", expanded=False):
            st.markdown("""
            Es el paso clave para crear tu catálogo. Tienes dos opciones:
            
            *   **Subir un archivo Excel (.xlsx):** Ideal para quienes ya gestionan su inventario en hojas de cálculo.
            *   **Usar un enlace de Google Sheets:** Perfecto para catálogos colaborativos o basados en la nube.

            **Formato Requerido:**
            Tu archivo debe tener **exactamente** las siguientes 5 columnas para funcionar correctamente:
            
            | Nombre de Columna | Descripción                                    |
            |-------------------|------------------------------------------------|
            | `ImagenURL`       | Enlace público (URL) a la imagen del producto. |
            | `Producto`        | Nombre del producto.                           |
            | `Descripción`     | Breve descripción del producto.                |
            | `Unidad`          | Unidad de venta (Ej: Kg, Litro, Paquete).      |
            | `Precio`          | Precio del producto (solo el número).          |

            💡 **Consejo:** Puedes descargar un archivo de ejemplo desde la pestaña `Cargar` para usarlo como plantilla.
            """)

        with st.expander("Paso 4: Visualizar y Filtrar (Preview)"):
            st.markdown("""
            Una vez cargados tus productos, esta pestaña te permite:
            
            *   **Ver tu catálogo** tal como lo vería un cliente.
            *   **Usar los filtros** (buscar por nombre, rango de precio o unidad) para encontrar productos específicos rápidamente).
            *   **Compartir un producto individualmente:** Usa el botón `Compartir con Cliente` en cada tarjeta de producto para enviar un mensaje personalizado por WhatsApp o para añadirlo a una lista de envío por email.
            """)

        with st.expander("Paso 5: Exportar tu Catálogo"):
            st.markdown("""
            Aquí es donde creas los archivos finales de tu catálogo. Tienes dos formatos poderosos:

            *   **PDF (📄):** La mejor opción para:
                *   Enviar por correo como un archivo adjunto profesional.
                *   Imprimir tu catálogo.
                *   Compartir en un formato de documento clásico.

            *   **HTML (🌐):** La mejor opción para:
                *   **Compartir como un enlace web** en WhatsApp, redes sociales o tu página web.
                *   Ofrecer una experiencia interactiva y fácil de navegar, especialmente en móviles.
            """)

        with st.expander("Paso 6: Enviar por Email"):
            st.markdown("""
            Esta pestaña te permite enviar rápidamente un correo electrónico a tus clientes. 
            
            1.  **Ingresa el email** del destinatario.
            2.  **Elige el tipo de correo:** puedes enviar el catálogo completo o solo los productos que seleccionaste previamente en la pestaña `Preview`.
            3.  **Haz clic en `Abrir Email`:** Esto abrirá tu aplicación de correo predeterminada (Gmail, Outlook, etc.) con un borrador listo para enviar.
            """)

        # --- Guía de Administrador ---
        auth = st.session_state.auth_manager
        if auth and auth.is_admin(st.session_state.user_email):
            st.markdown("---")
            st.subheader("Guía para Administradores")
            with st.expander("Gestión de Usuarios en el Panel 'Admin'"):
                st.markdown("""
                Como administrador, tienes acceso a la pestaña `Admin` para gestionar quién puede usar la aplicación.

                *   **Agregar Usuario:** En la parte superior, encontrarás un formulario para añadir nuevos usuarios. Simplemente completa los datos (incluyendo una contraseña inicial) y haz clic en `Agregar Usuario`.
                
                *   **Gestionar Usuarios Existentes:** En la lista `Usuarios Autorizados`, puedes expandir el perfil de cada usuario para:
                    *   **Cambiar Rol:** Usa el botón `Hacer Admin` o `Quitar Admin` para cambiar los permisos de un usuario.
                    *   **Cambiar Contraseña:** Utiliza el formulario para asignarle una nueva contraseña a un usuario si la olvida.
                    *   **Eliminar Usuario:** Haz clic en el ícono de la papelera (🗑️) para revocar el acceso permanentemente.
                """)

        # --- Preguntas Frecuentes ---
        st.markdown("---")
        st.subheader("Preguntas Frecuentes (FAQ)")
        with st.expander("Mis imágenes no se cargan, ¿qué hago?"):
            st.markdown("""
            Esto suele ocurrir por dos razones:
            1.  **La URL no es pública:** La URL de la imagen debe ser accesible para cualquiera en internet. No funcionará si la imagen está en tu computadora o en un servicio privado como Google Drive sin compartirla públicamente.
            2.  **La URL no es una imagen directa:** La URL debe terminar en `.jpg`, `.png`, `.gif`, etc. 

            **Solución Rápida:**
            1.  Busca una imagen en Google.
            2.  Haz clic derecho sobre la imagen y selecciona **"Copiar dirección de imagen"**.
            3.  Pega esa URL en tu archivo Excel o Google Sheets. Si la imagen se ve en el navegador al pegar la URL, ¡funcionará en CatalogPro!
            """)

        with st.expander("¿Qué es el usuario 'admin@antayperu.com'?"):
            st.markdown("""
            Es el **usuario raíz** o **super-administrador** del sistema. Se crea por defecto para asegurar que siempre haya una forma de acceder y gestionar la aplicación. Por seguridad, este usuario no puede ser eliminado ni se le pueden quitar los permisos de administrador desde la interfaz.
            """)

    def render_admin_panel(self):
        """Panel de administración de usuarios"""
        st.header("👨‍💼 Panel de Administración")
        
        auth = st.session_state.auth_manager
        
        if not auth.is_admin(st.session_state.user_email):
            st.error("No tienes permisos de administrador")
            return
        
        st.subheader("Agregar Usuario")
        
        with st.form("add_user_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                new_email = st.text_input("Email", placeholder="usuario@empresa.com")
                new_name = st.text_input("Nombre", placeholder="Juan Pérez")
                new_business = st.text_input("Empresa", placeholder="Mi Empresa S.A.")
            with c2:
                new_password = st.text_input("Contraseña", type="password")
                confirm_password = st.text_input("Confirmar Contraseña", type="password")
            
            submitted = st.form_submit_button("Agregar Usuario", use_container_width=True, type="primary")
            
            if submitted:
                if new_email and new_name and new_business and new_password:
                    if new_password == confirm_password:
                        try:
                            if auth.add_user(new_email, new_name, new_business, new_password):
                                st.success(f"Usuario {new_email} agregado!")
                                st.balloons()
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.warning("Email ya registrado")
                        except Exception as e:
                            st.error(f"{str(e)}")
                    else:
                        st.error("Las contraseñas no coinciden")
                else:
                    st.error("❌ Completa todos los campos")
        
        st.markdown("---")
        
        st.subheader("Usuarios Autorizados")
        
        users_list = auth.get_all_users()
        
        if not users_list:
            st.info("ℹ️ No hay usuarios registrados")
        else:
            search = st.text_input("Buscar", key="adm_search")
            
            filtered = users_list
            if search:
                filtered = [u for u in users_list if search.lower() in u['email'].lower() or search.lower() in u['info'].get('name', '').lower()]
            
            st.write(f"**Total:** {len(users_list)} | **Mostrando:** {len(filtered)}")
            
            for user in filtered:
                email = user['email']
                info = user['info']
                
                with st.expander(f"👤 {info.get('name', 'Sin nombre')} - {email}"):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**Email:** {email}")
                        st.write(f"**Nombre:** {info.get('name', 'N/A')}")
                        st.write(f"**Empresa:** {info.get('business_name', 'N/A')}")
                        st.write(f"**Registrado:** {info.get('created_at', 'N/A')[:10]}")
                        
                        last = info.get('last_login')
                        st.write(f"**Último acceso:** {last[:10] if last else 'Nunca'}")
                        st.write(f"**Rol:** {'Admin' if info.get('is_admin') else 'Usuario'}")
                    
                    with col2:
                        if email != auth.admin_email:
                            if st.button("", key=f"del_{email}", help="Eliminar usuario", type="secondary"):
                                if auth.remove_user(email):
                                    st.success(f"✅ {email} eliminado")
                                    time.sleep(1)
                                    st.rerun()
                            
                            is_currently_admin = info.get('is_admin', False)
                            button_text = "Quitar Admin" if is_currently_admin else "Hacer Admin"
                            if st.button(button_text, key=f"toggle_admin_{email}", help="Cambiar rol de usuario"):
                                if auth.toggle_admin_status(email):
                                    st.success(f"Rol de {email} actualizado.")
                                    time.sleep(1)
                                    st.rerun()
                        else:
                            st.info("Admin Principal")

                    with st.form(f"update_pass_{email}"):
                        st.markdown("**Cambiar Contraseña**")
                        new_pass = st.text_input("Nueva Contraseña", type="password", key=f"new_pass_{email}")
                        confirm_pass = st.text_input("Confirmar Nueva Contraseña", type="password", key=f"confirm_pass_{email}")
                        
                        if st.form_submit_button("Cambiar Contraseña", use_container_width=True):
                            if new_pass and new_pass == confirm_pass:
                                if auth.update_password(email, new_pass):
                                    st.success("Contraseña actualizada!")
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.error("No se pudo actualizar")
                            elif not new_pass:
                                st.warning("La contraseña no puede estar vacía")
                            else:
                                st.error("Las contraseñas no coinciden")
        
        st.markdown("---")
        
        st.subheader("Estadísticas")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total", len(users_list))
        
        with col2:
            admins = sum(1 for u in users_list if u['info'].get('is_admin'))
            st.metric("Admins", admins)
        
        with col3:
            st.metric("Regulares", len(users_list) - admins)

# =============================================================================
# EJECUTAR
# =============================================================================

if __name__ == "__main__":
    app = CatalogProApp()
    app.run()