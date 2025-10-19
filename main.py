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

# Configuración de la página
st.set_page_config(
    page_title="CatalogPro Enhanced - Catálogo Digital",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# CLASES AUXILIARES MEJORADAS
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
            
        # Verificar caché
        cache_key = f"{image_url}_{max_size}"
        if cache_key in self.image_cache:
            return self.image_cache[cache_key]
            
        try:
            response = requests.get(str(image_url), timeout=10)
            response.raise_for_status()
            
            image = Image.open(io.BytesIO(response.content))
            
            # Redimensionar si es necesario
            if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Convertir a RGB si es necesario
            if image.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
                
            # Guardar en caché
            self.image_cache[cache_key] = image
            return image
            
        except Exception as e:
            st.warning(f"No se pudo cargar imagen: {str(e)}")
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
    """Clase para generar catálogos visuales de productos"""
    
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
                        self._render_product_card(product, currency)
                        
    def _render_product_card(self, product, currency):
        """Renderizar una tarjeta de producto individual"""
        with st.container():
            image = self.image_manager.download_image(product['ImagenURL'])
            st.image(image, use_container_width=True)
            
            st.markdown(f"""
            <div style="font-size: 1.2rem; font-weight: bold; color: #2c3e50; margin-bottom: 0.5rem;">
                {product['Producto']}
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div style="color: #7f8c8d; font-size: 0.9rem; margin-bottom: 1rem;">
                {product['Descripción']}
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 1])
            with col1:
                st.markdown(f"""
                <div style="font-size: 0.8rem; color: #95a5a6;">
                    Por {product['Unidad']}
                </div>
                """, unsafe_allow_html=True)
                
            with col2:
                st.markdown(f"""
                <div style="font-size: 1.4rem; font-weight: bold; color: #e74c3c; text-align: right;">
                    {currency} {product['Precio']:.2f}
                </div>
                """, unsafe_allow_html=True)
                
            # Botones de acción
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"💬 WhatsApp", key=f"whatsapp_{product['Producto']}", help="Consultar por WhatsApp"):
                    message = f"Hola! Me interesa el producto: {product['Producto']} - {product['Descripción']} - Precio: {currency} {product['Precio']:.2f}"
                    whatsapp_url = f"https://wa.me/?text={quote(message)}"
                    st.markdown(f'<a href="{whatsapp_url}" target="_blank">🔗 Abrir WhatsApp</a>', unsafe_allow_html=True)
            
            with col2:
                if st.button(f"📧 Email", key=f"email_{product['Producto']}", help="Añadir a email"):
                    if 'email_products' not in st.session_state:
                        st.session_state.email_products = []
                    
                    # Evitar duplicados
                    product_dict = product.to_dict()
                    if not any(p['Producto'] == product_dict['Producto'] for p in st.session_state.email_products):
                        st.session_state.email_products.append(product_dict)
                        st.success("✅ Añadido!")
                    else:
                        st.info("Ya añadido")
                
            st.markdown("---")

class EnhancedPDFExporter:
    """Clase mejorada para exportar catálogos a PDF con imágenes - CALIDAD MEJORADA"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.image_manager = ImageManager()
        
    def generate_pdf_with_images(self, df, business_name, currency):
        """Generar PDF del catálogo con imágenes de productos - VERSION MEJORADA"""
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
        
        # Header mejorado con mejor diseño
        story.extend(self._create_enhanced_header(business_name))
        
        # Información del catálogo con mejor formato
        story.extend(self._create_enhanced_catalog_info(df, currency))
        
        # Productos con diseño mejorado
        story.extend(self._create_enhanced_product_cards(df, currency))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
        
    def _create_enhanced_header(self, business_name):
        """Crear header mejorado del PDF"""
        story = []
        
        # Logo si existe con mejor dimensionamiento
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
        
        # Título mejorado con mejor tipografía
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
        
        # Línea decorativa
        story.append(Spacer(1, 10))
        
        return story
        
    def _create_enhanced_catalog_info(self, df, currency):
        """Crear información del catálogo con mejor diseño"""
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
        <b>Fecha de Generación:</b> {datetime.now().strftime('%d de %B, %Y')}<br/>
        <b>Total de Productos:</b> {len(df)} items<br/>
        <b>Moneda:</b> {currency}<br/>
        <b>Precio Promedio:</b> {currency} {df['Precio'].mean():.2f}
        """
        
        story.append(Paragraph(info_text, info_style))
        story.append(Spacer(1, 20))
        
        return story
        
    def _create_enhanced_product_cards(self, df, currency):
        """Crear tarjetas de productos con diseño mejorado"""
        story = []
        
        # Productos por página optimizado
        products_per_page = 6  # 3 filas de 2 productos para mejor espaciado
        total_products = len(df)
        
        for page_start in range(0, total_products, products_per_page):
            page_end = min(page_start + products_per_page, total_products)
            page_products = df.iloc[page_start:page_end]
            
            # Crear filas de productos con mejor espaciado
            product_data = []
            for i in range(0, len(page_products), 2):
                row_data = []
                
                # Producto 1
                product1 = page_products.iloc[i]
                product1_cell = self._create_enhanced_product_cell(product1, currency)
                row_data.append(product1_cell)
                
                # Producto 2 (si existe)
                if i + 1 < len(page_products):
                    product2 = page_products.iloc[i + 1]
                    product2_cell = self._create_enhanced_product_cell(product2, currency)
                    row_data.append(product2_cell)
                else:
                    row_data.append("")  # Celda vacía si es impar
                
                product_data.append(row_data)
            
            # Crear tabla con mejor estilo
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
                    ('BACKGROUND', (0, 0), (-1, -1), colors.white),
                ]))
                
                story.append(products_table)
                story.append(Spacer(1, 20))
                
                # Añadir página nueva si no es la última página
                if page_end < total_products:
                    story.append(PageBreak())
        
        return story
        
    def _create_enhanced_product_cell(self, product, currency):
        """Crear celda de producto mejorada con mejor diseño"""
        
        # Imagen del producto con mejor dimensionamiento
        product_image = None
        try:
            image = self.image_manager.download_image(product['ImagenURL'], max_size=(300, 300))
            img_buffer = io.BytesIO()
            image.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            product_image = RLImage(img_buffer, width=2*inch, height=2*inch)
        except:
            # Imagen placeholder mejorada
            pass
        
        # Estilos mejorados para texto
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
        
        # Crear contenido de la celda
        cell_data = []
        
        if product_image:
            cell_data.append([product_image])
        
        cell_data.append([Paragraph(f"<b>{product['Producto']}</b>", title_style)])
        
        description = str(product['Descripción'])[:80] + ('...' if len(str(product['Descripción'])) > 80 else '')
        cell_data.append([Paragraph(f"<i>{description}</i>", desc_style)])
        
        cell_data.append([Paragraph(f"{currency} {product['Precio']:.2f}", price_style)])
        cell_data.append([Paragraph(f"Por {product['Unidad']}", unit_style)])
        
        # Crear tabla interna para la celda
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
                'subject': 'Catálogo de Productos - {business_name}',
                'body': '''Estimado/a cliente,

Nos complace enviarle nuestro catálogo actualizado de productos.

📋 INFORMACIÓN DEL CATÁLOGO:
• Total de productos: {total_products}
• Moneda: {currency}
• Fecha: {fecha}

📄 ADJUNTO:
Por favor encuentre adjunto nuestro catálogo completo en formato PDF con imágenes y descripciones detalladas de todos nuestros productos.

📱 CONTACTO:
Para consultas, pedidos o mayor información, no dude en contactarnos por WhatsApp o responder este email.

Saludos cordiales,
{business_name}

---
Catálogo generado con CatalogPro Enhanced'''
            },
            'productos_seleccionados': {
                'subject': 'Productos de su Interés - {business_name}',
                'body': '''Estimado/a cliente,

Como solicitado, le enviamos información sobre los productos de su interés:

🛍️ PRODUCTOS SELECCIONADOS:
{product_list}

📄 CATÁLOGO COMPLETO:
Adjuntamos también nuestro catálogo completo para su referencia.

📱 SIGUIENTE PASO:
Para realizar su pedido o consultar disponibilidad, contáctenos por WhatsApp o responda este email.

Saludos cordiales,
{business_name}

---
Catálogo generado con CatalogPro Enhanced'''
            }
        }
    
    def generate_mailto_url(self, to_email, business_name, df, currency, template_type='catalogo_completo', selected_products=None):
        """Generar URL mailto con email pre-completado"""
        
        template = self.templates[template_type]
        
        # Preparar variables para el email
        template_vars = {
            'business_name': business_name,
            'total_products': len(df),
            'currency': currency,
            'fecha': datetime.now().strftime('%d/%m/%Y'),
            'product_list': self._format_product_list(selected_products, currency) if selected_products else ""
        }
        
        # Generar asunto y cuerpo
        subject = template['subject'].format(**template_vars)
        body = template['body'].format(**template_vars)
        
        # Crear URL mailto
        mailto_url = f"mailto:{to_email}?subject={quote(subject)}&body={quote(body)}"
        
        return mailto_url
    
    def _format_product_list(self, products, currency):
        """Formatear lista de productos para email"""
        if not products:
            return ""
        
        formatted_list = ""
        for i, product in enumerate(products, 1):
            formatted_list += f"{i}. {product['Producto']}\n"
            formatted_list += f"   Descripción: {product['Descripción']}\n"
            formatted_list += f"   Precio: {currency} {product['Precio']:.2f}\n"
            formatted_list += f"   Unidad: {product['Unidad']}\n\n"
        
        return formatted_list.strip()

class HTMLExporter:
    """Clase para exportar catálogos a HTML completo"""
    
    def __init__(self):
        self.image_manager = ImageManager()
        
    def generate_html_catalog(self, df, business_name, currency):
        """Generar catálogo HTML completo"""
        
        html_template = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{business_name} - Catálogo Digital</title>
            <style>
                {self._get_css_styles()}
            </style>
        </head>
        <body>
            <header class="header">
                <div class="container">
                    <h1>{business_name}</h1>
                    <p>Catálogo Digital de Productos</p>
                </div>
            </header>
            
            <main class="main">
                <div class="container">
                    <div class="catalog-info">
                        <p><strong>Fecha:</strong> {datetime.now().strftime('%d/%m/%Y')}</p>
                        <p><strong>Total productos:</strong> {len(df)}</p>
                        <p><strong>Moneda:</strong> {currency}</p>
                    </div>
                    
                    <div class="product-grid">
                        {self._generate_product_cards_html(df, currency)}
                    </div>
                </div>
            </main>
            
            <footer class="footer">
                <div class="container">
                    <p>© 2025 {business_name}. Generado con CatalogPro.</p>
                </div>
            </footer>
        </body>
        </html>
        """
        
        return html_template
    
    def _get_css_styles(self):
        """Obtener estilos CSS para el catálogo HTML"""
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Arial', sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f8f9fa;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem 0;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }
        
        .header p {
            font-size: 1.2rem;
            opacity: 0.9;
        }
        
        .main {
            padding: 2rem 0;
        }
        
        .catalog-info {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .product-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
        }
        
        .product-card {
            background: white;
            border-radius: 15px;
            padding: 1.5rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .product-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }
        
        .product-image {
            width: 100%;
            height: 200px;
            object-fit: cover;
            border-radius: 10px;
            margin-bottom: 1rem;
        }
        
        .product-title {
            font-size: 1.3rem;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 0.5rem;
        }
        
        .product-description {
            color: #7f8c8d;
            margin-bottom: 1rem;
            font-size: 0.95rem;
        }
        
        .product-footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .product-unit {
            font-size: 0.85rem;
            color: #95a5a6;
        }
        
        .product-price {
            font-size: 1.4rem;
            font-weight: bold;
            color: #e74c3c;
        }
        
        .whatsapp-btn {
            display: inline-block;
            background: #25d366;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 25px;
            text-decoration: none;
            font-weight: bold;
            margin-top: 1rem;
            transition: background-color 0.3s ease;
        }
        
        .whatsapp-btn:hover {
            background: #128c7e;
        }
        
        .footer {
            background: #2c3e50;
            color: white;
            text-align: center;
            padding: 1rem 0;
            margin-top: 3rem;
        }
        
        @media (max-width: 768px) {
            .product-grid {
                grid-template-columns: 1fr;
            }
            
            .header h1 {
                font-size: 2rem;
            }
        }
        """
    
    def _generate_product_cards_html(self, df, currency):
        """Generar tarjetas de productos en HTML"""
        cards_html = ""
        
        for _, product in df.iterrows():
            # Procesar imagen
            image_url = product['ImagenURL']
            if pd.isna(image_url) or not image_url or str(image_url) == 'nan':
                image_src = "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHJlY3Qgd2lkdGg9IjEwMCUiIGhlaWdodD0iMTAwJSIgZmlsbD0iI2YwZjBmMCIvPgo8dGV4dCB4PSI1MCUiIHk9IjUwJSIgZm9udC1mYW1pbHk9IkFyaWFsIiBmb250LXNpemU9IjE4IiBmaWxsPSIjOTk5IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkeT0iLjNlbSI+U2luIGltYWdlbjwvdGV4dD4KPC9zdmc+"
            else:
                image_src = str(image_url)
            
            # Mensaje WhatsApp
            whatsapp_message = f"Hola! Me interesa el producto: {product['Producto']} - {product['Descripción']} - Precio: {currency} {product['Precio']:.2f}"
            whatsapp_url = f"https://wa.me/?text={quote(whatsapp_message)}"
            
            card_html = f"""
            <div class="product-card">
                <img src="{image_src}" alt="{product['Producto']}" class="product-image">
                <div class="product-title">{product['Producto']}</div>
                <div class="product-description">{product['Descripción']}</div>
                <div class="product-footer">
                    <span class="product-unit">Por {product['Unidad']}</span>
                    <span class="product-price">{currency} {product['Precio']:.2f}</span>
                </div>
                <a href="{whatsapp_url}" class="whatsapp-btn" target="_blank">💬 Consultar por WhatsApp</a>
            </div>
            """
            
            cards_html += card_html
        
        return cards_html

# =============================================================================
# APLICACIÓN PRINCIPAL MEJORADA v1.1.1
# =============================================================================

class EnhancedCatalogApp:
    def __init__(self):
        self.data_handler = DataHandler()
        self.catalog_generator = CatalogGenerator()
        self.pdf_exporter = EnhancedPDFExporter()
        self.data_cleaner = DataCleaner()
        self.email_marketing = SimpleEmailMarketing()
        self.html_exporter = HTMLExporter()
        
    def run(self):
        self.setup_styles()
        self.render_header()
        self.render_sidebar()
        self.render_main_content()
        
    def setup_styles(self):
        """Configurar estilos CSS personalizados"""
        st.markdown("""
        <style>
        .main-header {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
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
        
        .feature-badge {
            background: linear-gradient(45deg, #ff6b6b, #ee5a24);
            color: white;
            padding: 0.3rem 0.6rem;
            border-radius: 15px;
            font-size: 0.8rem;
            font-weight: bold;
            margin-left: 0.5rem;
        }
        
        .easy-badge {
            background: linear-gradient(45deg, #2ecc71, #27ae60);
            color: white;
            padding: 0.3rem 0.6rem;
            border-radius: 15px;
            font-size: 0.8rem;
            font-weight: bold;
            margin-left: 0.5rem;
        }
        
        .fixed-badge {
            background: linear-gradient(45deg, #9b59b6, #8e44ad);
            color: white;
            padding: 0.3rem 0.6rem;
            border-radius: 15px;
            font-size: 0.8rem;
            font-weight: bold;
            margin-left: 0.5rem;
        }
        
        .stButton > button {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 5px;
            padding: 0.5rem 1rem;
            font-weight: bold;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        
        .email-button {
            background: linear-gradient(45deg, #3498db, #2980b9) !important;
            color: white !important;
            border: none !important;
            padding: 10px 20px !important;
            border-radius: 25px !important;
            font-weight: bold !important;
            text-decoration: none !important;
            display: inline-block !important;
            margin: 10px 0 !important;
        }
        
        .email-button:hover {
            background: linear-gradient(45deg, #2980b9, #3498db) !important;
            transform: translateY(-2px) !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
    def render_header(self):
        """Renderizar el encabezado principal"""
        st.markdown("""
        <div class="main-header">
            <h1>🛍️ CatalogPro Enhanced</h1>
            <p>Genera catálogos profesionales con imágenes, email marketing súper fácil y exportación HTML</p>
            <span class="feature-badge">v1.1.1</span>
            <span class="feature-badge">PDF + Imágenes</span>
            <span class="easy-badge">Email Súper Fácil</span>
            <span class="feature-badge">Export HTML</span>
            <span class="fixed-badge">Bugs Fixed</span>
        </div>
        """, unsafe_allow_html=True)
        
    def render_sidebar(self):
        """Renderizar la barra lateral con opciones"""
        st.sidebar.header("📊 Configuración")
        
        # Información del negocio
        st.sidebar.subheader("🏢 Información del Negocio")
        business_name = st.sidebar.text_input("Nombre del negocio", "Mi Empresa")
        currency = st.sidebar.selectbox("Moneda", ["S/", "$", "€", "£"], index=0)
        
        # Configuración de diseño
        st.sidebar.subheader("🎨 Diseño")
        columns = st.sidebar.slider("Columnas por fila", 1, 4, 3)
        
        # Logo del negocio
        st.sidebar.subheader("🏢 Logo del Negocio")
        uploaded_logo = st.sidebar.file_uploader(
            "Subir logo",
            type=['png', 'jpg', 'jpeg'],
            help="Recomendado: PNG, 300x100px máximo, fondo transparente"
        )

        if uploaded_logo is not None:
            st.sidebar.image(uploaded_logo, width=200)
            st.session_state.logo = uploaded_logo
        else:
            st.session_state.logo = None

        # Info simplificada de email
        st.sidebar.subheader("📧 Email Marketing")
        st.sidebar.success("✅ Súper fácil - Sin configuración!")
        st.sidebar.info("💡 Solo necesitas el email del destinatario. Tu cliente de email se abrirá automáticamente.")
        
        # Guardar configuración en session_state
        st.session_state.business_name = business_name
        st.session_state.currency = currency
        st.session_state.columns = columns
        
        # Estadísticas mejoradas
        if 'df' in st.session_state and st.session_state.df is not None:
            st.sidebar.subheader("📈 Estadísticas")
            df = st.session_state.df
            
            total_products = len(df)
            avg_price = df['Precio'].mean()
            max_price = df['Precio'].max()
            min_price = df['Precio'].min()
            
            st.sidebar.metric("Total de productos", total_products)
            st.sidebar.metric("Precio promedio", f"{currency} {avg_price:.2f}")
            st.sidebar.metric("Precio máximo", f"{currency} {max_price:.2f}")
            st.sidebar.metric("Precio mínimo", f"{currency} {min_price:.2f}")
            
            # NUEVO: Mostrar fuentes de datos
            if hasattr(st.session_state, 'data_sources') and st.session_state.data_sources:
                st.sidebar.subheader("📊 Fuentes de Datos")
                for source in st.session_state.data_sources:
                    st.sidebar.write(f"• {source}")
                    
    def render_main_content(self):
        """Renderizar el contenido principal"""
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Cargar Datos", "👀 Vista Previa", "📄 Exportar", "📧 Email Fácil", "ℹ️ Ayuda"])
        
        with tab1:
            self.render_data_loading()
            
        with tab2:
            self.render_catalog()
            
        with tab3:
            self.render_export_options()
            
        with tab4:
            self.render_simple_email_marketing()
            
        with tab5:
            self.render_help()
            
    def render_data_loading(self):
        """Renderizar la sección de carga de datos - MEJORADA para múltiples fuentes"""
        st.header("📊 Cargar Datos del Catálogo")
        
        # NUEVO: Botón para limpiar todos los datos
        if 'df' in st.session_state and st.session_state.df is not None:
            col_clean1, col_clean2 = st.columns([3, 1])
            with col_clean2:
                if st.button("🗑️ Limpiar Todos los Datos", type="secondary"):
                    st.session_state.df = None
                    if 'data_sources' in st.session_state:
                        st.session_state.data_sources = []
                    st.success("✅ Datos limpiados completamente!")
                    st.rerun()
            
            with col_clean1:
                total_products = len(st.session_state.df)
                sources_count = len(getattr(st.session_state, 'data_sources', []))
                st.info(f"📊 **Datos actuales:** {total_products} productos de {sources_count} fuente(s)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📁 Cargar archivo Excel")
            uploaded_file = st.file_uploader(
                "Selecciona un archivo Excel (.xlsx)",
                type=['xlsx'],
                help="El archivo debe contener las columnas: ImagenURL, Producto, Descripción, Unidad, Precio"
            )
            
            if uploaded_file is not None:
                try:
                    with st.spinner("Cargando datos..."):
                        df = self.data_handler.load_excel(uploaded_file)
                        cleaned_df = self.data_cleaner.clean_data(df)
                        
                        # MEJORADO: Combinar con datos existentes en lugar de sobrescribir
                        if 'df' in st.session_state and st.session_state.df is not None:
                            combined_df = pd.concat([st.session_state.df, cleaned_df], ignore_index=True).drop_duplicates(subset=['Producto'], keep='last')
                            st.session_state.df = combined_df
                            
                            # Tracking de fuentes
                            if 'data_sources' not in st.session_state:
                                st.session_state.data_sources = []
                            st.session_state.data_sources.append(f"Excel: {uploaded_file.name}")
                            
                            st.success(f"✅ Datos combinados! Total: {len(combined_df)} productos ({len(cleaned_df)} nuevos desde Excel)")
                        else:
                            st.session_state.df = cleaned_df
                            st.session_state.data_sources = [f"Excel: {uploaded_file.name}"]
                            st.success(f"✅ Archivo Excel cargado! {len(cleaned_df)} productos encontrados.")
                        
                        st.subheader("👀 Vista previa de los datos")
                        display_df = st.session_state.df.tail().copy()  # Mostrar últimos datos añadidos
                        display_df['Descripción'] = display_df['Descripción'].apply(
                            lambda x: str(x)[:100] + '...' if len(str(x)) > 100 else str(x)
                        )
                        st.dataframe(display_df)
                        
                except Exception as e:
                    st.error(f"❌ Error al cargar el archivo Excel: {str(e)}")
                    
        with col2:
            st.subheader("🔗 Desde Google Sheets")
            sheets_url = st.text_input(
                "URL de Google Sheets",
                placeholder="https://docs.google.com/spreadsheets/d/..."
            )
            
            if st.button("Cargar desde Google Sheets"):
                if sheets_url:
                    try:
                        with st.spinner("Cargando desde Google Sheets..."):
                            df = self.data_handler.load_google_sheets(sheets_url)
                            cleaned_df = self.data_cleaner.clean_data(df)
                            
                            # MEJORADO: Combinar con datos existentes
                            if 'df' in st.session_state and st.session_state.df is not None:
                                combined_df = pd.concat([st.session_state.df, cleaned_df], ignore_index=True).drop_duplicates(subset=['Producto'], keep='last')
                                st.session_state.df = combined_df
                                
                                # Tracking de fuentes
                                if 'data_sources' not in st.session_state:
                                    st.session_state.data_sources = []
                                st.session_state.data_sources.append("Google Sheets")
                                
                                st.success(f"✅ Datos combinados! Total: {len(combined_df)} productos ({len(cleaned_df)} nuevos desde Google Sheets)")
                            else:
                                st.session_state.df = cleaned_df
                                st.session_state.data_sources = ["Google Sheets"]
                                st.success(f"✅ Google Sheets cargado! {len(cleaned_df)} productos encontrados.")
                            
                            st.subheader("👀 Vista previa de los datos")
                            display_df = st.session_state.df.tail().copy()  # Mostrar últimos datos
                            display_df['Descripción'] = display_df['Descripción'].apply(
                                lambda x: str(x)[:100] + '...' if len(str(x)) > 100 else str(x)
                            )
                            st.dataframe(display_df)
                            
                    except Exception as e:
                        st.error(f"❌ Error al cargar desde Google Sheets: {str(e)}")
                else:
                    st.warning("⚠️ Por favor, ingresa una URL válida de Google Sheets")
                    
        # Ejemplo de estructura de datos
        st.subheader("📋 Estructura de datos requerida")
        example_data = {
            'ImagenURL': ['https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=300', 'https://images.unsplash.com/photo-1549298916-b41d501d3772?w=300'],
            'Producto': ['Aceite Primor', 'Galleta Oreo'],
            'Descripción': ['Aceite vegetal 1L', 'Paquete x 6 unidades'],
            'Unidad': ['Unidad', 'Paquete'],
            'Precio': [10.50, 4.20]
        }
        example_df = pd.DataFrame(example_data)
        st.dataframe(example_df)
        
    def render_catalog(self):
        """Renderizar el catálogo de productos - VISTA PREVIA PARA EL DUEÑO"""
        st.header("👀 Vista Previa del Catálogo")
        st.info("💡 Esta es una vista previa de cómo verán tus clientes el catálogo. Usa los filtros para personalizar antes de exportar.")
        
        if 'df' not in st.session_state or st.session_state.df is None:
            st.warning("⚠️ Por favor, carga primero los datos en la pestaña 'Cargar Datos'")
            return
            
        df = st.session_state.df
        
        # Limpiar lista de productos seleccionados para email
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("🗑️ Limpiar selección de email"):
                st.session_state.email_products = []
                st.success("Lista de email limpiada!")
        
        with col2:
            # Mostrar productos seleccionados para email
            if 'email_products' in st.session_state and st.session_state.email_products:
                st.info(f"📧 Productos seleccionados para email: {len(st.session_state.email_products)}")
        
        # Filtros
        st.subheader("🔍 Filtros")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            search_term = st.text_input("🔍 Buscar producto")
            
        with col2:
            min_price = float(df['Precio'].min())
            max_price = float(df['Precio'].max())
            
            if min_price == max_price:
                st.info(f"💰 Precio único: {st.session_state.currency} {min_price:.2f}")
                price_range = (min_price, max_price)
            else:
                price_range = st.slider("💰 Rango de precios", 
                                       min_price, 
                                       max_price, 
                                       (min_price, max_price))
            
        with col3:
            if 'Unidad' in df.columns:
                units = ['Todos'] + list(df['Unidad'].unique())
                selected_unit = st.selectbox("📦 Unidad", units)
            else:
                selected_unit = 'Todos'
                
        # Aplicar filtros
        filtered_df = df.copy()
        
        if search_term:
            filtered_df = filtered_df[
                filtered_df['Producto'].str.contains(search_term, case=False, na=False) |
                filtered_df['Descripción'].str.contains(search_term, case=False, na=False)
            ]
            
        filtered_df = filtered_df[
            (filtered_df['Precio'] >= price_range[0]) & 
            (filtered_df['Precio'] <= price_range[1])
        ]
        
        if selected_unit != 'Todos':
            filtered_df = filtered_df[filtered_df['Unidad'] == selected_unit]
            
        # Mostrar productos
        if len(filtered_df) == 0:
            st.info("🔍 No se encontraron productos con los filtros seleccionados")
            return
            
        st.info(f"📊 Mostrando {len(filtered_df)} de {len(df)} productos")
        
        # Generar catálogo
        self.catalog_generator.render_catalog(filtered_df, st.session_state.columns, st.session_state.currency)
        
    def render_export_options(self):
        """Renderizar opciones de exportación mejoradas con GUIDANCE"""
        st.header("📄 Exportar Catálogo")
        
        if 'df' not in st.session_state or st.session_state.df is None:
            st.warning("⚠️ Por favor, carga primero los datos en la pestaña 'Cargar Datos'")
            return
            
        df = st.session_state.df
        
        # NUEVO: Guidance sobre cuándo usar cada formato
        st.subheader("📋 ¿Cuál formato elegir?")
        col_guide1, col_guide2 = st.columns(2)
        
        with col_guide1:
            st.info("""
            📄 **Usar PDF cuando:**
            • Envías por email como adjunto
            • Quieres imprimir el catálogo
            • Clientes prefieren documentos tradicionales
            • Presentaciones offline
            """)
            
        with col_guide2:
            st.info("""
            🌐 **Usar HTML cuando:**
            • Compartes links en redes sociales
            • Subes a tu página web
            • Clientes navegan desde móviles
            • Quieres mejor SEO
            """)
        
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("📊 PDF con Imágenes MEJORADO")
            st.markdown("**✨ v1.1.1** PDF profesional con diseño mejorado y mejor calidad")
            
            if st.button("🎨 Generar PDF Profesional"):
                try:
                    with st.spinner("Generando PDF con calidad mejorada..."):
                        pdf_buffer = self.pdf_exporter.generate_pdf_with_images(
                            df, 
                            st.session_state.business_name,
                            st.session_state.currency
                        )
                        
                        st.download_button(
                            label="📥 Descargar PDF Profesional",
                            data=pdf_buffer,
                            file_name=f"catalogo_profesional_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                            mime="application/pdf"
                        )
                        
                        st.success("✅ PDF profesional generado exitosamente!")
                        st.info("💡 **Calidad mejorada:** Mejor tipografía, espaciado optimizado, imágenes de mayor resolución")
                        
                except Exception as e:
                    st.error(f"❌ Error al generar PDF: {str(e)}")
                    
        with col2:
            st.subheader("🌐 Exportar HTML")
            st.markdown("**✨ Calidad Superior** Catálogo web completo y navegable")
            
            if st.button("🔗 Generar HTML"):
                try:
                    with st.spinner("Generando catálogo HTML..."):
                        html_content = self.html_exporter.generate_html_catalog(
                            df,
                            st.session_state.business_name,
                            st.session_state.currency
                        )
                        
                        st.download_button(
                            label="📥 Descargar HTML",
                            data=html_content.encode('utf-8'),
                            file_name=f"catalogo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                            mime="text/html"
                        )
                        
                        st.success("✅ Catálogo HTML generado exitosamente!")
                        st.info("💡 **Recomendado para:** Compartir en redes sociales y páginas web")
                        
                        # Vista previa
                        with st.expander("👀 Vista previa HTML"):
                            st.components.v1.html(html_content, height=600, scrolling=True)
                        
                except Exception as e:
                    st.error(f"❌ Error al generar HTML: {str(e)}")
                    
        with col3:
            st.subheader("📊 Resumen de Datos")
            
            total_products = len(df)
            avg_price = df['Precio'].mean()
            total_value = df['Precio'].sum()
            
            st.metric("Total productos", total_products)
            st.metric("Precio promedio", f"{st.session_state.currency} {avg_price:.2f}")
            st.metric("Valor total", f"{st.session_state.currency} {total_value:.2f}")
            
            # NUEVO: Mostrar fuentes de datos en resumen
            if hasattr(st.session_state, 'data_sources') and st.session_state.data_sources:
                st.write("**Fuentes de datos:**")
                for source in st.session_state.data_sources:
                    st.write(f"• {source}")
            
    def render_simple_email_marketing(self):
        """Renderizar funcionalidades de email marketing simplificadas con MEJORES MENSAJES"""
        st.header("📧 Email Marketing Súper Fácil")
        
        if 'df' not in st.session_state or st.session_state.df is None:
            st.warning("⚠️ Por favor, carga primero los datos en la pestaña 'Cargar Datos'")
            return
            
        df = st.session_state.df
        
        # Información destacada
        st.success("✨ **¡Sin configuración complicada!** Solo necesitas el email del destinatario.")
        st.info("💡 **Cómo funciona:** Se abrirá tu cliente de email (Gmail, Outlook, etc.) con todo pre-completado. Solo presiona 'Enviar'.")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📮 Enviar Catálogo por Email")
            
            # Email del destinatario
            to_email = st.text_input("📧 Email del destinatario", placeholder="cliente@ejemplo.com")
            
            # Tipo de envío
            email_type = st.selectbox(
                "📋 Tipo de email",
                ["catalogo_completo", "productos_seleccionados"],
                format_func=lambda x: "📋 Catálogo Completo" if x == "catalogo_completo" else "🛍️ Productos Seleccionados"
            )
            
            # Mostrar productos seleccionados si aplica
            if email_type == "productos_seleccionados":
                if 'email_products' in st.session_state and st.session_state.email_products:
                    st.write(f"📦 **Productos seleccionados:** {len(st.session_state.email_products)}")
                    with st.expander("Ver productos seleccionados"):
                        for product in st.session_state.email_products:
                            st.write(f"• **{product['Producto']}** - {st.session_state.currency} {product['Precio']:.2f}")
                else:
                    st.warning("⚠️ No has seleccionado productos. Ve al catálogo y usa los botones '📧 Email'")
                    st.info("💡 En la pestaña 'Vista Previa', haz clic en los botones '📧 Email' de los productos que te interesan.")
            
            # Botones de acción principales
            col1_1, col1_2 = st.columns(2)
            
            with col1_1:
                # Botón para generar PDF primero
                if st.button("📄 Generar PDF para Email", disabled=not to_email, use_container_width=True):
                    try:
                        with st.spinner("Generando PDF para adjuntar..."):
                            pdf_buffer = self.pdf_exporter.generate_pdf_with_images(
                                df, 
                                st.session_state.business_name,
                                st.session_state.currency
                            )
                            
                            # Guardar PDF en session state
                            st.session_state.pdf_for_email = pdf_buffer
                            
                            st.download_button(
                                label="📥 Descargar PDF para adjuntar",
                                data=pdf_buffer,
                                file_name=f"catalogo_{datetime.now().strftime('%Y%m%d')}.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
                            
                            st.success("✅ PDF listo! Descárgalo y tenlo preparado para adjuntar.")
                            
                    except Exception as e:
                        st.error(f"❌ Error al generar PDF: {str(e)}")
            
            with col1_2:
                # Botón para abrir email con MENSAJES MEJORADOS
                if st.button("📧 Abrir Email Pre-completado", disabled=not to_email, use_container_width=True):
                    try:
                        # Determinar productos seleccionados
                        selected_products = None
                        if email_type == "productos_seleccionados" and 'email_products' in st.session_state:
                            selected_products = st.session_state.email_products
                        
                        # Generar URL mailto
                        mailto_url = self.email_marketing.generate_mailto_url(
                            to_email=to_email,
                            business_name=st.session_state.business_name,
                            df=df,
                            currency=st.session_state.currency,
                            template_type=email_type,
                            selected_products=selected_products
                        )
                        
                        # MEJORADO: Mensajes más claros sobre el comportamiento
                        st.markdown(f"""
                        <script>
                        window.open('{mailto_url}', '_blank');
                        </script>
                        <div style="text-align: center; margin: 20px 0;">
                            <p style="color: green; font-weight: bold;">✅ Intentando abrir tu cliente de email...</p>
                            <p style="color: #666;">Si no se abrió automáticamente (normal en algunos navegadores), haz clic en el enlace de abajo:</p>
                            <a href="{mailto_url}" class="email-button">📧 Abrir Email Manualmente</a>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.info("💡 **Es normal que no se abra automáticamente** - Los navegadores modernos bloquean pop-ups por seguridad. Usa el enlace manual.")
                        st.success("🎉 **¡Email listo!** Revisa tu cliente de email, adjunta el PDF descargado y presiona enviar.")
                        
                        # Limpiar productos seleccionados después del envío
                        if 'email_products' in st.session_state:
                            st.session_state.email_products = []
                            
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
        
        with col2:
            st.subheader("📊 Información")
            
            st.markdown("### ✅ Ventajas")
            st.write("• ✨ **Cero configuración**")
            st.write("• 🚀 **Súper rápido**")
            st.write("• 🔒 **100% seguro**")
            st.write("• 📱 **Funciona en móviles**")
            
            # Productos seleccionados
            if 'email_products' in st.session_state:
                selected_count = len(st.session_state.email_products)
                st.metric("Productos seleccionados", selected_count)
            
            st.markdown("### 📋 Plantillas")
            st.write("• 📋 **Catálogo Completo**")
            st.write("• 🛍️ **Productos Seleccionados**")
            
            st.markdown("### 💡 Pasos Simples")
            st.write("1. **Email** del destinatario")
            st.write("2. **Generar PDF** para adjuntar")
            st.write("3. **Abrir Email** pre-completado")
            st.write("4. **Adjuntar PDF** y enviar")
                    
    def render_help(self):
        """Renderizar la sección de ayuda mejorada con nuevas funcionalidades"""
        st.header("ℹ️ Ayuda y Documentación")
        
        st.markdown("""
        ## 🚀 Cómo usar CatalogPro Enhanced v1.1.1
        
        ### ✨ Funcionalidades v1.1.1 - Bugs Corregidos
        - **✅ FIXED**: Múltiples fuentes de datos - Ahora Excel + Google Sheets se combinan
        - **✅ FIXED**: Calidad PDF mejorada - Diseño profesional igualado con HTML
        - **✅ IMPROVED**: Mensajes email más claros - Mejor guidance
        - **✅ NEW**: Guidance HTML vs PDF - Saber cuándo usar cada uno
        
        ### 📊 Múltiples Fuentes de Datos - ¡AHORA FUNCIONA!
        
        **Flujo recomendado:**
        1. **Carga Excel** con tu inventario base
        2. **Añade Google Sheets** con productos nuevos o actualizaciones  
        3. **Resultado**: Catálogo combinado de ambas fuentes
        4. **Botón limpiar**: Para empezar desde cero cuando necesites
        
        ### 📄 PDF vs 🌐 HTML - ¿Cuándo usar cada uno?
        
        **📄 PDF - Ideal para:**
        - Enviar por **email como adjunto**
        - **Imprimir** catálogos físicos
        - **Presentaciones** offline a clientes
        - Clientes que prefieren **documentos tradicionales**
        
        **🌐 HTML - Ideal para:**
        - **Compartir links** en WhatsApp/redes sociales
        - **Subir a páginas web** como sección productos
        - Clientes **jóvenes y digitales**
        - Mejor **SEO** y visibilidad web
        
        ### 📧 Email Marketing - Súper Simplificado
        
        **¿Por qué no se abre automáticamente?**
        - **Es normal** - Navegadores bloquean pop-ups por seguridad
        - **Usa enlace manual** - Está diseñado para eso
        - **Funciona igual** - Tu cliente de email se abre con todo listo
        
        ### 🎯 Proceso Paso a Paso Actualizado:
        
        #### 1. **Cargar Datos (Mejorado)**
        - Excel: Sube archivo .xlsx como base
        - Google Sheets: Añade productos adicionales
        - **Ambos se combinan** automáticamente
        - Usa "Limpiar datos" para empezar de cero
        
        #### 2. **Vista Previa** (Para el dueño)
        - Revisa cómo se verá el catálogo combinado
        - Filtra y configura antes de exportar
        - Selecciona productos específicos para email
        
        #### 3. **Exportar (Con Guidance)**
        - **Lee la guía** PDF vs HTML para decidir
        - **PDF**: Calidad mejorada, más profesional
        - **HTML**: Superior para digital
        
        #### 4. **Email Fácil (Mensajes Claros)**
        - Genera PDF primero
        - Abre email pre-completado
        - **Normal** si requiere clic manual
        - Adjunta PDF y envía
        
        ### 💡 Estructura de Datos (Sin Cambios)
        ```
        ImagenURL    | URL pública de imagen
        Producto     | Nombre del producto  
        Descripción  | Descripción detallada
        Unidad       | Unidad de venta (Kg, Unidad, etc)
        Precio       | Precio numérico (sin símbolos)
        ```
        
        ### 🛠️ Troubleshooting Actualizado
        
        **Múltiples fuentes no se combinan:**
        - ✅ **SOLUCIONADO** en v1.1.1
        - Ahora Excel + Google Sheets se suman automáticamente
        
        **PDF se ve mal comparado con HTML:**
        - ✅ **MEJORADO** en v1.1.1  
        - Calidad visual significativamente mejorada
        - Tipografía profesional, mejor espaciado
        
        **Email no se abre automáticamente:**
        - ✅ **ESPERADO** - Navegadores bloquean pop-ups
        - ✅ **SOLUCIÓN** - Usar enlace manual (diseñado para eso)
        - ✅ **MEJORADO** - Mensajes más claros sobre qué esperar
        
        **No sé si usar PDF o HTML:**
        - ✅ **SOLUCIONADO** - Guidance clara en pestaña Exportar
        - Regla simple: PDF para email/imprimir, HTML para web/links
        
        ### 📱 Compatibilidad (Sin Cambios)
        - **Navegadores**: Chrome, Firefox, Safari, Edge
        - **Email clients**: Gmail, Outlook, Apple Mail, etc
        - **Móviles**: Funciona en iOS y Android
        
        ### 🎉 Cambios v1.1.1 Resumen
        
        **Bugs Corregidos:**
        - ✅ Múltiples fuentes de datos
        - ✅ Calidad PDF mejorada
        - ✅ Mensajes email más claros
        - ✅ Guidance HTML vs PDF
        
        **Nuevas Features:**
        - 🆕 Tracking de fuentes de datos
        - 🆕 Botón limpiar datos
        - 🆕 Guidance cuándo usar cada formato
        - 🆕 Feedback mejorado al usuario
        """)

# Ejecutar la aplicación mejorada v1.1.1
if __name__ == "__main__":
    app = EnhancedCatalogApp()
    app.run()