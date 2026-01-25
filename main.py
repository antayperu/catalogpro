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
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from auth import check_authentication, AuthManager
from reportlab.pdfgen import canvas
import time

# CP-UX-010 v4: FRD Schema and Validator
from frd_schema import FRD_SCHEMA, get_required_columns, get_optional_columns, get_all_columns
from frd_validator import FRDValidator

class NumberedCanvas(canvas.Canvas):
    """Canvas avanzado que soporta 'Página X de Y'"""
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """Metodo mágico que rellena el total de páginas al final"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)
        
    def draw_page_number(self, page_count):
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor('#7f8c8d'))
        page_text = f"Página {self._pageNumber} de {page_count}"
        self.drawRightString(A4[0] - 50, 40, page_text)

# Configuración de la página
st.set_page_config(
    page_title="CatalogPro Enhanced - Catálogo Digital",
    page_icon=" ",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# CLASES AUXILIARES MEJORADAS v1.2
# =============================================================================

class DataHandler:
    """Clase para manejar la carga de datos desde diferentes fuentes"""
    
    def __init__(self):
        self.required_columns = ['Línea', 'Familia', 'Marca', 'Código', 'Producto', 'Descripción', 'Unidad', 'Precio', 'Stock', 'ImagenURL']
        
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
        cleaned_df = self._clean_prices_and_stock(cleaned_df)
        cleaned_df = self._clean_image_urls(cleaned_df)
        cleaned_df = self._clean_text_fields(cleaned_df)
        cleaned_df = self._remove_invalid_rows(cleaned_df)
        cleaned_df = self._optimize_datatypes(cleaned_df)
        return cleaned_df
        
    def _clean_basic_data(self, df):
        """Limpiar datos básicos"""
        df = df.dropna(how='all')
        df = df.reset_index(drop=True)
        return df
        
    def _clean_prices_and_stock(self, df):
        """Limpiar y validar precios y stock"""
        # Limpieza de precios
        if 'Precio' in df.columns:
            df['Precio'] = df['Precio'].astype(str).str.replace(',', '')
            df['Precio'] = pd.to_numeric(df['Precio'], errors='coerce')
            df = df[df['Precio'] > 0]
            
        # Limpieza de stock
        if 'Stock' in df.columns:
            df['Stock'] = pd.to_numeric(df['Stock'], errors='coerce').fillna(0).astype('int32')
            
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
        text_columns = ['Producto', 'Descripción', 'Unidad', 'Línea', 'Familia', 'Grupo', 'Marca', 'Código']
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

    def _optimize_datatypes(self, df):
        """Optimizar tipos de datos para escalabilidad"""
        # Convertir campos de jerarquía a Categorías para ahorrar memoria
        category_cols = ['Línea', 'Familia', 'Grupo', 'Marca', 'Unidad']
        for col in category_cols:
            if col in df.columns:
                df[col] = df[col].astype('category')
        
        return df

class ImageManager:
    """Clase para manejar la descarga y procesamiento de imágenes"""
    
    MAX_CACHE_SIZE = 1000 # Max number of files
    CACHE_DIR = os.path.abspath(os.path.join(os.getcwd(), '.img_cache'))

    def __init__(self):
        self.placeholder_image = self._generate_placeholder_image()
        
        # 1. Setup Disk Cache Directory (Best Effort)
        self.disk_cache_enabled = False
        try:
            if not os.path.exists(self.CACHE_DIR):
                os.makedirs(self.CACHE_DIR, exist_ok=True)
            self.disk_cache_enabled = True
            # Optional: Cleanup on init (LRU-like could be expensive on every start, keeping simple limit)
            self._cleanup_cache() 
        except Exception as e:
            print(f"Warning: Disabling disk cache due to error: {e}")
            st.error(f"Disk Cache Init Error: {e}") # Show in UI for debug
            self.disk_cache_enabled = False

        # 2. Persist Session Cache (Memory Layer)
        if 'image_cache_persistent' not in st.session_state:
            st.session_state['image_cache_persistent'] = {}
        self.image_cache = st.session_state['image_cache_persistent']

    def _get_cache_path(self, url, max_size):
        """Generates a secure MD5 filename from URL"""
        import hashlib
        hash_obj = hashlib.md5(f"{url}_{max_size}".encode('utf-8'))
        return os.path.join(self.CACHE_DIR, f"{hash_obj.hexdigest()}.jpg")

    def _cleanup_cache(self):
        """Enforces MAX_CACHE_SIZE by deleting oldest files (LRU approximation)"""
        try:
            files = [os.path.join(self.CACHE_DIR, f) for f in os.listdir(self.CACHE_DIR)]
            if len(files) > self.MAX_CACHE_SIZE:
                # Sort by access time (oldest first)
                files.sort(key=lambda x: os.path.getmtime(x) if os.path.exists(x) else 0)
                # Delete excess files
                num_to_delete = len(files) - self.MAX_CACHE_SIZE
                for f in files[:num_to_delete]:
                    try:
                        os.remove(f)
                    except:
                        pass
        except Exception:
            pass # Fail silently on cleanup
        
    def download_image(self, image_url, max_size=(400, 400)):
        """Descargar imagen desde URL con caché y Headers"""
        if pd.isna(image_url) or not image_url or str(image_url) == 'nan':
            return self.placeholder_image, "empty"
            
        cache_key = f"{image_url}_{max_size}"
        # 1. Check Memory Cache
        if cache_key in self.image_cache:
            return self.image_cache[cache_key], "cache"
        
        # 2. Check Disk Cache (if enabled)
        cache_path = None
        if self.disk_cache_enabled:
            cache_path = self._get_cache_path(image_url, max_size)
            if os.path.exists(cache_path):
                try:
                    # Simple open, no pickle
                    image = Image.open(cache_path)
                    image.load() # Verify integrity
                    self.image_cache[cache_key] = image # Promote to memory
                    return image, "disk"
                except Exception:
                    # Corrupt file? Delete it
                    try: os.remove(cache_path)
                    except: pass

        # 3. Download from Net
        try:
            # FIX: User-Agent to avoid 403 blocks
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(str(image_url), headers=headers, timeout=10) # 10s timeout
            response.raise_for_status()
            
            image = Image.open(io.BytesIO(response.content))
            
            # Convert P to RGBA/RGB
            if image.mode == 'P':
                image = image.convert('RGBA')
            
            # Thumbnail processing (Save space)
            if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Ensure RGB for JPEG saving
            if image.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            
            # 4. Save to Disk Cache (if enabled)
            if self.disk_cache_enabled and cache_path:
                try:
                    # Save as standard JPEG
                    image.save(cache_path, "JPEG", quality=85)
                except Exception as e:
                    pass 
            
            image.load()    
            self.image_cache[cache_key] = image
            return image, "download"
            
        except Exception as e:
            # print(f"Error downloading {image_url}: {e}") # Debug log
            return self.placeholder_image, "error"

    def download_images_concurrently(self, urls, max_workers=10, progress_callback=None):
        """
        Descarga múltiples imágenes en paralelo.
        Returns: Dict with stats {'total', 'ok', 'failed', 'empty', 'cached'}
        """
        import concurrent.futures
        
        stats = {'total': len(urls), 'valid_urls': 0, 'ok': 0, 'failed': 0, 'empty': 0, 'cached': 0}
        
        unique_urls = [u for u in list(set(urls)) if pd.notna(u) and u and str(u) != 'nan']
        stats['valid_urls'] = len(unique_urls)
        stats['empty'] = stats['total'] - stats['valid_urls']
        
        total = len(unique_urls)
        completed = 0
        
        if total == 0:
            return stats
        
        # Pre-check cache to avoid unnecessary threads
        to_download = [u for u in unique_urls if f"{u}_{(300, 300)}" not in self.image_cache and f"{u}_{(400, 400)}" not in self.image_cache]
        cached_count = total - len(to_download)
        
        if progress_callback and cached_count > 0:
            progress_callback(cached_count, total)
            completed = cached_count
            stats['cached'] = cached_count
            stats['ok'] += cached_count

        if not to_download:
            return stats

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Create a dictionary to map future to url
            future_to_url = {executor.submit(self.download_image, url, (300, 300)): url for url in to_download}
            
            for future in concurrent.futures.as_completed(future_to_url):
                completed += 1
                if progress_callback:
                    progress_callback(completed, total)
                try:
                    img, status = future.result() # Now returns tuple (image, status)
                    if status == 'error':
                        stats['failed'] += 1
                    else:
                        stats['ok'] += 1
                except Exception:
                    stats['failed'] += 1
                    
        return stats
    
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
    """Clase para generar catálogos visuales de productos - MEJORADA v1.2"""
    
    def __init__(self):
        self.image_manager = ImageManager()
        
    def render_catalog(self):
        st.header("Vista Previa")

        if 'df' in st.session_state and st.session_state.df is not None:
            st.session_state.viewed_catalog = True
            df = st.session_state.df
            
            # --- View Settings ---
            show_images = st.session_state.get('show_preview_images', True)
            currency = st.session_state.currency if 'currency' in st.session_state else "S/"
            columns = 3

            c1, c2 = st.columns(2)
        start_idx = (current_page - 1) * st.session_state.items_per_page
        end_idx = start_idx + st.session_state.items_per_page
        
        # Sliced dataframe for current page
        page_df = df.iloc[start_idx:end_idx]
        
        # Render Controls
        c_top1, c_top2, c_top3 = st.columns([2, 5, 2])
        with c_top1:
             st.caption(f"Mostrando {start_idx + 1} - {min(end_idx, total_products)} de {total_products}")
        with c_top3:
             # Pagination Buttons
             c_prev, c_page, c_next = st.columns([1, 2, 1])
             with c_prev:
                 if st.button("◀", key="prev_page", disabled=current_page==1):
                     st.session_state.preview_page -= 1
                     st.rerun()
             with c_next:
                 if st.button("▶", key="next_page", disabled=current_page>=total_pages):
                     st.session_state.preview_page += 1
                     st.rerun()
             with c_page:
                 st.caption(f"Pág {current_page}/{total_pages}")

        rows = math.ceil(len(page_df) / columns)
        
        for row in range(rows):
            cols = st.columns(columns)
            for col_idx in range(columns):
                # Calculate index relative to the sliced dataframe
                local_idx = row * columns + col_idx
                if local_idx < len(page_df):
                    product = page_df.iloc[local_idx]
                    # Calculate global index for unique keys
                    global_idx = start_idx + local_idx
                    with cols[col_idx]:
                        self._render_product_card(product, currency, global_idx, row, show_images)
                        
    def _render_product_card(self, product, currency, product_idx, row, show_images=True):
        with st.container():
            # Image handling with Lazy Toggle
            if show_images:
                image, status = self.image_manager.download_image(product['ImagenURL'])
                buffered = io.BytesIO()
                image.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                st.markdown(f"<div class='product-image-container'><img src='data:image/png;base64,{img_str}' alt='{product['Producto']}'></div>", unsafe_allow_html=True)
            else:
                # Placeholder HTML separate from ImageManager logic for pure speed
                st.markdown(f"""
                <div class='product-image-container' style='background-color:#f0f0f0;display:flex;align-items:center;justify-content:center;color:#999;font-size:0.8rem;'>
                    📷 {product['Producto'][:20]}...
                </div>
                """, unsafe_allow_html=True)

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
                whatsapp_message = st.text_area("Mensaje de WhatsApp:", default_message, key=f"wa_msg_{product_idx}", height=150)
                
                if st.button("Generar Enlace de WhatsApp", key=f"send_wa_{product_idx}", use_container_width=True):
                    if whatsapp_message:
                        whatsapp_url = f"https://wa.me/?text={quote(whatsapp_message)}"
                        st.markdown(f'<a href="{whatsapp_url}" target="_blank" style="display:inline-block;padding:0.5rem 1rem;background-color:#25D366;color:white;border-radius:25px;text-decoration:none;">Abrir WhatsApp para Enviar</a>', unsafe_allow_html=True)
                    else:
                        st.warning("El mensaje no puede estar vacío.")

                st.markdown("---")
                
                # Add to email selection
                if st.button("Añadir a Selección de Email", key=f"add_em_{product_idx}", use_container_width=True):
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
        self.business_name_for_footer = ""
        self.phone_number_for_footer = ""
        self.email_for_footer = ""

    def _clean_text(self, val):
        """Clean nan values from text fields"""
        if pd.isna(val) or str(val).lower() == 'nan':
            return ""
        return str(val)

    def _get_pro_image(self, image_url):
        """
        Retrieves an image and resizes it to a fixed square frame (e.g. 1.5 inch)
        Maintains aspect ratio inside the box, pads with white if needed.
        Returns a ReportLab Image object.
        """
        try:
            pil_img, status = self.image_manager.download_image(image_url)
            
            # Target size in ReportLab points (1.5 inch = 108 pts approx)
            target_size_pts = 108 
            
            # Create a ReportLab Image from the PIL image
            # We save it to a buffer first to be safe with ReportLab's expected input
            img_buffer = io.BytesIO()
            pil_img.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            rl_img = RLImage(img_buffer)
            
            # Scaling logic: Fit inside target_size_pts x target_size_pts
            img_width, img_height = pil_img.size
            if img_width > img_height:
                factor = target_size_pts / img_width
            else:
                factor = target_size_pts / img_height
                
            rl_img.drawWidth = img_width * factor
            rl_img.drawHeight = img_height * factor
            
            # Force max dimensions just in case
            if rl_img.drawWidth > target_size_pts: rl_img.drawWidth = target_size_pts
            if rl_img.drawHeight > target_size_pts: rl_img.drawHeight = target_size_pts
            
            return rl_img
        except Exception:
            return None

    def _build_pdf_pro(self, df, business_name, currency, progress_callback=None, branding=None):
        """
        Professional Layout Engine (v2) - Enhanced with Hierarchy
        Order: Línea -> Familia -> Grupo -> Producto
        """
        story = []
        
        # Defaults if no branding provided
        if not branding:
            branding = {
                'primary': '#2c3e50', 
                'secondary': '#e74c3c', 
                'accent': '#3498db', 
                'text': '#2c3e50'
            }
        
        # Title Style
        title_style = ParagraphStyle('CustomTitle', parent=self.styles['Heading1'], fontSize=24, spaceAfter=20, alignment=TA_CENTER, textColor=colors.HexColor(branding['primary']))
        
        # Hierarchy Headers
        h1_style = ParagraphStyle('H1_Linea', parent=self.styles['Heading2'], fontSize=18, spaceBefore=20, spaceAfter=10, textColor=colors.HexColor(branding['secondary']), borderPadding=5, borderWidth=0)
        h2_style = ParagraphStyle('H2_Familia', parent=self.styles['Heading3'], fontSize=14, spaceBefore=10, spaceAfter=5, textColor=colors.HexColor(branding['accent']), leftIndent=10)
        h3_style = ParagraphStyle('H3_Grupo', parent=self.styles['Heading4'], fontSize=12, spaceBefore=5, spaceAfter=5, textColor=colors.HexColor(branding['text']), leftIndent=20)
        
        # Product Text Styles
        prod_name_style = ParagraphStyle('ProdName', parent=self.styles['Normal'], fontSize=10, leading=12, fontName='Helvetica-Bold', textColor=colors.HexColor(branding['text']))
        prod_desc_style = ParagraphStyle('ProdDesc', parent=self.styles['Normal'], fontSize=8, leading=10, textColor=colors.HexColor('#7f8c8d'))
        prod_meta_style = ParagraphStyle('ProdMeta', parent=self.styles['Normal'], fontSize=9, leading=11, textColor=colors.HexColor(branding['primary']))

        # --- COVER PAGE ---
        # Logo (Only on Page 1)
        if hasattr(st.session_state, 'logo') and st.session_state.logo:
            try:
                # Use standard PIL Image -> Bytes -> RLImage flow to be safe
                logo_pil = Image.open(st.session_state.logo)
                # Resize if too big (max width 300)
                if logo_pil.width > 300:
                    ratio = 300 / logo_pil.width
                    logo_pil = logo_pil.resize((300, int(logo_pil.height * ratio)), Image.Resampling.LANCZOS)
                
                logo_buf = io.BytesIO()
                logo_pil.save(logo_buf, format='PNG')
                logo_buf.seek(0)
                
                rl_logo = RLImage(logo_buf)
                rl_logo.hAlign = 'CENTER'
                story.append(rl_logo)
                story.append(Spacer(1, 20))
            except Exception as e:
                pass

        story.append(Paragraph(business_name, title_style))
        story.append(Paragraph(f"Catálogo de Productos - {datetime.now().strftime('%d/%m/%Y')}", ParagraphStyle('Date', parent=self.styles['Normal'], alignment=TA_CENTER)))
        story.append(Spacer(1, 30))
        story.append(PageBreak()) # Start products on Page 2
        
        # --- HIERARCHY PROCESSING ---
        # Ensure hierarchy columns exist
        hierarchy_cols = ['Línea', 'Familia', 'Grupo']
        valid_cols = [c for c in hierarchy_cols if c in df.columns]
        
        # Check if hierarchy columns have actual data (not all NaN)
        has_hierarchy_data = False
        if valid_cols:
            for col in valid_cols:
                if df[col].notna().any():
                    has_hierarchy_data = True
                    break
        
        # If no hierarchy data, process all products without grouping
        if not has_hierarchy_data or not valid_cols:
            # No hierarchy - process all products as one flat list
            valid_cols = []  # Don't group by anything
            df_sorted = df.sort_values(by=['Producto'])
            
            # Create a single "group" with all products
            grouped = [(None, df_sorted)]
        else:
            # Has hierarchy - use normal grouping
            # Sort Data
            sort_cols = valid_cols + ['Producto']
            df_sorted = df.sort_values(by=sort_cols)
            
            # Grouping Logic
            grouped = df_sorted.groupby(valid_cols)
        
        total_rows = len(df_sorted)
        processed_rows = 0
        
        # We can implement a "smart iterator" that checks previous key.
        prev_keys = [None] * len(valid_cols) if valid_cols else []
        
        # However, to use KeepTogether properly on the LOWEST level (Grupo + Products), we should group by the FULL hierarchy.
        
        for name, group in grouped:
            # 'name' is a tuple of values (Linea, Familia, Grupo)
            if not isinstance(name, tuple): name = (name,)
            
            # Check Level Changes (only if we have hierarchy)
            if prev_keys:  # Only process headers if we have hierarchy
                for i, val in enumerate(name):
                    if val != prev_keys[i]:
                        # Level i changed. Print Header i and all subsequent headers
                        clean_val = self._clean_text(val)
                        if not clean_val: continue
                        
                        if i == 0: story.append(Paragraph(str(clean_val).upper(), h1_style))
                        elif i == 1: story.append(Paragraph(str(clean_val), h2_style))
                        elif i == 2: story.append(Paragraph(str(clean_val), h3_style))
                        
                        # Reset lower levels
                        for j in range(i+1, len(prev_keys)):
                            prev_keys[j] = None
                        prev_keys[i] = val
                    
            # --- Build Product Table for this Group ---
            section_elements = []  
            data_matrix = []
            row_buffer = []
            
            for idx, row in group.iterrows():
                # Prepare Cell Content
                img_obj = self._get_pro_image(row['ImagenURL'])
                p_name = self._clean_text(row['Producto'])
                p_desc = self._clean_text(row.get('Descripción', ''))
                p_unit = self._clean_text(row.get('Unidad', ''))
                p_price = row['Precio']
                price_str = f"{currency} {float(p_price):.2f}" if pd.notna(p_price) else ""
                
                cell_content = [
                    img_obj if img_obj else Paragraph("Sin Imagen", prod_desc_style),
                    Spacer(1, 5),
                    Paragraph(p_name, prod_name_style),
                    Paragraph(p_desc[:100], prod_desc_style),
                    Spacer(1, 3),
                    Paragraph(f"<b>{price_str}</b> / {p_unit}", prod_meta_style)
                ]
                row_buffer.append(cell_content)
                if len(row_buffer) == 2:
                    data_matrix.append(row_buffer)
                    row_buffer = []

            if row_buffer:
                while len(row_buffer) < 2: row_buffer.append([])
                data_matrix.append(row_buffer)

            if data_matrix:
                t = Table(data_matrix, colWidths=[240, 240])
                t.setStyle(TableStyle([
                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                    ('LEFTPADDING', (0,0), (-1,-1), 10),
                    ('RIGHTPADDING', (0,0), (-1,-1), 10),
                    ('TOPPADDING', (0,0), (-1,-1), 10),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 15),
                    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#ecf0f1')),
                ]))
                
                # KeepTogether logic: Keep the whole table if small, or at least the first row?
                # Actually, the requirement says "Section Header" + "Products".
                # But here we already printed headers outside the Loop (above). 
                # This could result in orphaned H3.
                # FIX: We should accumulate elements and flush them with KeepTogether.
                
                # Since we are printing headers "on the fly" inside the loop based on diff, 
                # they are already added to 'story'. 'KeepTogether' won't work retroactively.
                # REFACTOR STRATEGY: Instead of direct append, build a 'block' of flowables.
                # But 'grouped' gives us the lowest level chunk.
                # So we can effectively wrap THIS chunk (Table) with the LAST Header (H3) if it was just printed.
                
                # Simpler: Just allow breaks for now, but KeepTogether the Table (or chunks of it).
                # ReportLab Table handles page breaks automatically unless wrapped in KeepTogether.
                # If we want to prevent orphaned headers, we should use KeepTogether([Header, Table]).
                # But headers are hierarchical.
                
                # Minimal Robust: Just add the table. If a header is at bottom, it's a known ReportLab issue.
                # Solving strictly requires a recursive build or buffering.
                # Given strict deadline, we stick to standard flow. The Table itself is unbreakable if wrapped, 
                # but we want it breakable.
                
                # COMPROMISE for v1.2.5: Add table to story. 
                story.append(t)
                story.append(Spacer(1, 10))
            
            processed_rows += len(group)
            if progress_callback:
                progress_callback(0.5 + 0.45 * (processed_rows / total_rows))
                
        return story

    def _add_footer(self, canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 9)
        canvas.setFillColor(colors.HexColor('#7f8c8d'))
        
        # Page number
        page_number_text = f"Página {doc.page}"
        canvas.drawRightString(A4[0] - 50, 40, page_number_text)
        
        # Contact info
        contact_info = self.business_name_for_footer
        if self.phone_number_for_footer:
            contact_info += f" | Tel: {self.phone_number_for_footer}"
        if self.email_for_footer:
            contact_info += f" | Email: {self.email_for_footer}"
        
        canvas.drawString(50, 40, contact_info)
        
        canvas.restoreState()

    def generate_pdf_with_images(self, df, business_name, currency, phone_number, user_email):
        """LEGACY: Generar PDF del catálogo con imágenes de productos"""
        self.business_name_for_footer = business_name
        self.phone_number_for_footer = phone_number
        self.email_for_footer = user_email
        buffer = io.BytesIO()
        
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=50,
            leftMargin=50,
            topMargin=50,
            bottomMargin=50
        )
        
        # ... (templates definitions kept same as separate methods if extracted, or inline)
        # Assuming templates are defined inside or as part of build process. 
        # For simplicity in this replacement, I'll rely on the existing templates logic in _build_pdf
        # But wait, original code had templates inline. I should preserve them or refactor.
        # To avoid massive duplicate code, I will refactor the build process into _build_pdf_doc
        
        return self._build_pdf_doc(doc, df, currency, business_name)

    def generate_pdf_optimized(self, df, business_name, currency, phone_number, user_email, progress_callback=None, use_pro_layout=True):
        """OPTIMIZED v1.2.1: Generar PDF con descarga paralela e instrumentación"""
        import time
        t_start = time.time()
        
        timing_stats = {'data_load': 0, 'image_fetch': 0, 'pdf_render': 0, 'total': 0}
        
        # 1. Image Fetching (Concurrent)
        t_img_start = time.time()
        self.business_name_for_footer = business_name
        self.phone_number_for_footer = phone_number
        self.email_for_footer = user_email
        
        start_time = time.time()
        
        # 1. Image Prefetch (Concurrent)
        if progress_callback: progress_callback(0.05, "🚀 Iniciando descarga paralela...")
        
        image_urls = df['ImagenURL'].tolist()
        total_imgs = len(image_urls)
        
        img_stats = self.image_manager.download_images_concurrently(
            image_urls, 
            max_workers=20,
            progress_callback=lambda n, total: progress_callback(0.1 + (0.4 * n/total), f"📷 Descargando imágenes: {n}/{total}") if progress_callback else None
        )
        
        fetch_time = time.time()
        
        # 2. Build PDF Story
        if progress_callback: progress_callback(0.55, "📄 Maquetando estructura del documento...")
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=30 if use_pro_layout else 50, # More space for Pro
            leftMargin=30 if use_pro_layout else 50,
            topMargin=40,
            bottomMargin=40
        )
        
        if use_pro_layout:
            story = self._build_pdf_pro(df, business_name, currency, 
                progress_callback=lambda p: progress_callback(0.55 + (0.35 * p), "🎨 Renderizando secciones y tablas...") if progress_callback else None,
                branding=st.session_state.get('branding_config')
            )
        else:
            # Legacy Flow (No Branding applied to maintain legacy behavior strictly)
            if progress_callback: progress_callback(0.7, "Renderizando diseño clásico...")
            # _build_pdf_doc builds the story, we need to extract it
            # Actually, looking at the code, _build_pdf_doc returns the story
            story = self._build_pdf_doc(doc, df, currency, business_name) 
            
        # 3. Render
        if progress_callback: progress_callback(0.95, "💾 Generando archivo PDF final...")
        
        # Use NumberedCanvas for "Page X of Y"
        doc.build(story, canvasmaker=NumberedCanvas, onFirstPage=self._add_footer_first, onLaterPages=self._add_footer_later)
        
        end_time = time.time()
        
        # Calculate File Size (MB)
        buffer.seek(0)
        file_size_mb = len(buffer.getvalue()) / (1024 * 1024)
        
        # Get Page Count (doc.page is 1-based, after build it should be total pages if not reset)
        # Note: doc.page is usually strictly increasing during build.
        page_count = doc.page 

        stats = {
            "total_time": end_time - start_time,
            "fetch_time": fetch_time - start_time,
            "render_time": end_time - fetch_time,
            "img_stats": img_stats,
            "file_size_mb": file_size_mb,
            "page_count": page_count
        }
        
        buffer.seek(0)
        return buffer.getvalue(), stats # Return bytes and stats
        
    def _add_footer_first(self, canvas, doc):
        """Footer solo para la primera página (puede variar si se desea)"""
        self._add_footer_content(canvas, doc, is_first=True)
        
    def _add_footer_later(self, canvas, doc):
        """Footer para páginas siguientes"""
        self._add_footer_content(canvas, doc, is_first=False)

    def _add_footer_content(self, canvas, doc, is_first=False):
        """Contenido común del footer"""
        canvas.saveState()
        canvas.setFont('Helvetica', 9)
        canvas.setFillColor(colors.HexColor('#7f8c8d'))
        
        # NOTE: Page numbering is handled by NumberedCanvas.draw_page_number
        
        # Contact info
        contact_info = self.business_name_for_footer
        if self.phone_number_for_footer:
            contact_info += f" | Tel: {self.phone_number_for_footer}"
        if self.email_for_footer:
            contact_info += f" | Email: {self.email_for_footer}"
        
        canvas.drawString(50, 40, contact_info)
        
        canvas.restoreState()
    def _build_pdf_doc(self, doc, df, currency, business_name):
        def first_page_template(canvas, doc):
            canvas.saveState()
            canvas.setFont('Helvetica', 9)
            canvas.setFillColor(colors.HexColor('#7f8c8d'))
            # Page number
            page_number_text = f"Página {doc.page}"
            canvas.drawRightString(A4[0] - 50, 40, page_number_text)
            # Contact info
            contact_info = self.business_name_for_footer
            if self.phone_number_for_footer:
                contact_info += f" | Tel: {self.phone_number_for_footer}"
            if self.email_for_footer:
                contact_info += f" | Email: {self.email_for_footer}"
            canvas.drawString(50, 40, contact_info)
            doc.topMargin = 30
            canvas.restoreState()

        def later_pages_template(canvas, doc):
            canvas.saveState()
            canvas.setFont('Helvetica', 9)
            canvas.setFillColor(colors.HexColor('#7f8c8d'))
            page_number_text = f"Página {doc.page}"
            canvas.drawRightString(A4[0] - 50, 40, page_number_text)
            contact_info = self.business_name_for_footer
            if self.phone_number_for_footer:
                contact_info += f" | Tel: {self.phone_number_for_footer}"
            if self.email_for_footer:
                contact_info += f" | Email: {self.email_for_footer}"
            canvas.drawString(50, 40, contact_info)
            doc.topMargin = 50
            canvas.restoreState()
        
        story = []
        story.extend(self._create_enhanced_header(business_name))
        story.extend(self._create_enhanced_catalog_info(df, currency))
        story.extend(self._create_enhanced_product_cards(df, currency))
        
        # Don't build here - just return the story
        # The caller (generate_pdf_optimized) will build it
        return story
        
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
            spaceAfter=5,
            alignment=TA_LEFT,
            textColor=colors.HexColor('#2c3e50'),
            fontName='Helvetica-Bold'
        )
        
        # Custom title or default business name
        title_text = st.session_state.get('pdf_custom_title') or business_name

        # Dynamic subtitle or custom subtitle
        if st.session_state.get('pdf_custom_subtitle'):
            subtitle_text = st.session_state.get('pdf_custom_subtitle')
        else:
            now = datetime.now()
            try:
                import locale
                locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
            except:
                pass # Fallback to default locale if Spanish is not available
            month_name = now.strftime("%B").capitalize()
            year = now.year
            subtitle_text = f"Catálogo Edición {month_name} {year}"

        subtitle_style = ParagraphStyle(
            name='EnhancedSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=10,
            alignment=TA_LEFT,
            textColor=colors.HexColor('#7f8c8d'),
            fontName='Helvetica'
        )
        
        story.append(Paragraph(title_text, title_style))
        story.append(Paragraph(subtitle_text, subtitle_style))
        story.append(Spacer(1, 5))
        
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
        <b>Fecha:</b> {datetime.now().strftime('%d/%m/%Y')}
        """
        
        story.append(Paragraph(info_text, info_style))
        story.append(Spacer(1, 20))
        
        return story
        
    def _create_enhanced_product_cards(self, df, currency):
        """Crear tarjetas de productos organizadas por jerarquía (Línea -> Familia)"""
        story = []
        columns = st.session_state.get('pdf_columns', 2)
        col_width = (A4[0] - 100) / columns

        # Estilos para encabezados de jerarquía
        line_style = ParagraphStyle(
            name='HierarchyLine',
            parent=self.styles['Heading1'],
            fontSize=22,
            spaceBefore=20,
            spaceAfter=15,
            textColor=colors.HexColor('#2c3e50'), # Dark Blue
            borderPadding=10,
            borderColor=colors.HexColor('#ecf0f1'),
            borderWidth=1,
            backColor=colors.HexColor('#f7f9f9'),
            keepWithNext=True
        )
        
        family_style = ParagraphStyle(
            name='HierarchyFamily',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceBefore=15,
            spaceAfter=10,
            textColor=colors.HexColor('#e67e22'), # Orange
            keepWithNext=True
        )

        # Iterar por Línea
        for linea_name, linea_group in df.groupby('Línea', observed=True):
            if len(linea_group) == 0: continue
            
            # Header de Línea (Nueva página si no es la primera, opcional, aquí solo separador fuerte)
            story.append(Paragraph(f"📌 {linea_name}", line_style))
            story.append(Spacer(1, 10))

            # Iterar por Familia dentro de Línea
            for familia_name, familia_group in linea_group.groupby('Familia', observed=True):
                if len(familia_group) == 0: continue
                
                # Header de Familia
                story.append(Paragraph(f"▪ {familia_name}", family_style))
                story.append(Spacer(1, 5))

                # Grid de Productos para esta Familia
                product_data = []
                row_data = []
                
                products_in_family = familia_group.to_dict('records')
                total_products = len(products_in_family)

                for i, product in enumerate(products_in_family):
                    # Pasamos el producto como Series o Dict, _create_enhanced_product_cell espera acceso dict-like
                    product_cell_flowables = self._create_enhanced_product_cell(product, currency, col_width)
                    row_data.append(product_cell_flowables)
                    
                    if (i + 1) % columns == 0:
                        product_data.append(row_data)
                        row_data = []
                
                if row_data: # Add remaining cells
                    while len(row_data) < columns:
                        row_data.append("")
                    product_data.append(row_data)

                if product_data:
                    products_table = Table(product_data, colWidths=[col_width] * columns, splitByRow=1)
                    products_table.setStyle(TableStyle([
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ('LEFTPADDING', (0, 0), (-1, -1), 10), # Reduced padding slightly
                        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                        ('TOPPADDING', (0, 0), (-1, -1), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
                        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#ecf0f1')) # Subtle grid
                    ]))
                    story.append(products_table)
                    story.append(Spacer(1, 15))
            
            story.append(PageBreak()) # Start new line on new page logic (cleaner)

        return story
        
    def _create_enhanced_product_cell(self, product, currency, col_width):
        """Crear celda de producto mejorada"""
        product_image = None
        try:
            image = self.image_manager.download_image(product['ImagenURL'], max_size=(300, 300))
            img_buffer = io.BytesIO()
            image.save(img_buffer, format='JPEG', quality=85)
            img_buffer.seek(0)
            image_width = col_width * 0.8 # Use 80% of cell width for the image
            product_image = RLImage(img_buffer, width=image_width, height=image_width)
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
            cell_data.append(product_image)
            cell_data.append(Spacer(1, 8))

        cell_data.append(Paragraph(f"<b>{product['Producto']}</b>", title_style))
        
        description = str(product['Descripción'])[:80] + ('...' if len(str(product['Descripción'])) > 80 else '')
        cell_data.append(Paragraph(f"<i>{description}</i>", desc_style))
        
        cell_data.append(Paragraph(f"{currency} {product['Precio']:.2f}", price_style))
        cell_data.append(Paragraph(f"Por {product['Unidad']}", unit_style))
        
        return cell_data

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
        
    def generate_html_catalog(self, df, business_name, currency, phone_number, branding=None):
        """Genera un archivo HTML autocontenido con el catálogo"""
        
        # Defaults
        if not branding:
             branding = {'primary': '#2c3e50', 'secondary': '#e74c3c', 'accent': '#3498db', 'text': '#2c3e50'}

        # CSS Styles injected with Branding
        css = f"""
        <style>
            :root {{
                --primary: {branding['primary']};
                --secondary: {branding['secondary']};
                --accent: {branding['accent']};
                --text: {branding['text']};
                --bg: #f8f9fa;
                --card-bg: #ffffff;
            }}
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: var(--bg); color: var(--text); padding: 20px; }}
            .header {{ text-align: center; padding: 40px 0; background-color: var(--primary); color: white; margin-bottom: 30px; border-radius: 8px; }}
            .header h1 {{ margin: 0; font-size: 2.5em; }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; }}
            .card {{ background-color: var(--card-bg); border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); overflow: hidden; transition: transform 0.2s; }}
            .card:hover {{ transform: translateY(-5px); }}
            .card-img {{ width: 100%; height: 250px; object-fit: contain; background-color: white; border-bottom: 1px solid #eee; }}
            .card-body {{ padding: 15px; }}
            .card-title {{ font-size: 1.1em; font-weight: bold; margin-bottom: 5px; color: var(--primary); }}
            .card-desc {{ font-size: 0.9em; color: #666; margin-bottom: 15px; height: 40px; overflow: hidden; }}
            .card-footer {{ display: flex; justify-content: space-between; align-items: center; margin-top: 10px; }}
            .price {{ font-size: 1.2em; font-weight: bold; color: var(--secondary); }}
            .unit {{ font-size: 0.8em; color: #888; background: #eee; padding: 2px 6px; border-radius: 4px; }}
            .whatsapp-btn {{ background-color: #25D366; color: white; text-decoration: none; padding: 8px 15px; border-radius: 20px; font-weight: bold; font-size: 0.9em; display: block; text-align: center; margin-top: 10px; }}
        </style>
        """
        
        html_template = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{business_name} - Catálogo</title>
            {css}
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
# PARTE 2: APLICACIÓN PRINCIPAL v1.2 - COPIAR DESPUÉS DE PARTE 1
# =============================================================================

# NOTA IMPORTANTE: Este código va DESPUÉS de toda la Parte 1 en main.py
# La Parte 1 contiene todas las clases auxiliares
# Esta Parte 2 contiene solo la clase EnhancedCatalogApp y el if __name__

# =============================================================================
# CLASE PRINCIPAL MEJORADA
# =============================================================================

class EnhancedCatalogApp:
    """Aplicación principal con mejoras UX/UI v1.2"""
    
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
    
    # CP-UX-003: Función centralizada para estado de plan (MVP sin BD)
    def get_user_plan_status(self, user_email):
        """
        Obtiene el estado del plan del usuario.
        MVP: Retorna valores por defecto configurables.
        FUTURO: Leerá de Postgres sin cambiar la UI.
        
        Returns:
            dict: {
                'plan_type': 'Free' | 'Cantidad' | 'Tiempo',
                'remaining': int | None,  # Catálogos restantes (si es Cantidad)
                'expiry_date': str | None  # Fecha vencimiento (si es Tiempo)
            }
        """
        # MVP: Configuración por defecto
        # TODO: Reemplazar con query a Postgres cuando esté disponible
        return {
            'plan_type': 'Free',
            'remaining': 5,  # Catálogos restantes
            'expiry_date': None  # None para Free y Cantidad
        }
        
    def run(self):
        # PRIMERO: Verificar autenticación
        auth = check_authentication()
        st.session_state.auth_manager = auth
        
        # Calcular is_admin una sola vez
        is_admin = False
        if st.session_state.get("authenticated"):
            is_admin = auth.is_admin(st.session_state.user_email)

        # DESPUÉS: Continuar normal
        self.setup_styles()
        self.render_header()
        self.render_sidebar(is_admin)
        self.render_main_content(is_admin)
        
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
        /* ROLLBACK: Original card styles restored */
        .product-card {
            background: white;
            border-radius: 15px;
            padding: 1.5rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s;
            height: 100%;
            display: flex;
            flex-direction: column;
        }
        .product-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }
        .product-image-container {
            width: 100%;
            height: 200px;
            overflow: hidden;
            border-radius: 10px;
            margin-bottom: 1rem;
            background: #f8f9fa;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .product-image-container img {
            width: 100%;
            height: 100%;
            object-fit: contain; /* CP-UX-009: Better image quality */
            object-position: center;
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
            flex-grow: 1;
        }
        .product-footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: auto;
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
        </style>
        """, unsafe_allow_html=True)
        
    def render_header(self):
        st.markdown("""
        <div class="main-header">
            <h1>CatalogPro Enhanced</h1>
            <p>Catálogos profesionales mejorados</p>
            <span class="feature-badge">v1.2</span>
            <span class="feature-badge">PDF</span>
            <span class="easy-badge">Email Fácil</span>
            <span class="ux-badge">UX Mejorada</span>
        </div>
        """, unsafe_allow_html=True)
    
    def render_sidebar(self, is_admin):
        st.sidebar.header("📊 Configuración")
        
        auth = st.session_state.auth_manager
        user_email = st.session_state.user_email
        user_info = st.session_state.user_info

        # CP-UX-003: Tarjeta Plan y uso
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 💎 Plan y uso")
        
        plan_status = self.get_user_plan_status(user_email)
        plan_type = plan_status['plan_type']
        remaining = plan_status['remaining']
        expiry_date = plan_status['expiry_date']
        
        # Mostrar tipo de plan
        if plan_type == "Free":
            st.sidebar.info(f"**Plan:** {plan_type}")
        elif plan_type == "Cantidad":
            st.sidebar.success(f"**Plan:** {plan_type}")
        elif plan_type == "Tiempo":
            st.sidebar.success(f"**Plan:** {plan_type}")
        
        # Mostrar saldo o vigencia
        if plan_type in ["Free", "Cantidad"] and remaining is not None:
            if remaining > 0:
                st.sidebar.caption(f"✅ Te quedan **{remaining}** catálogos")
            else:
                st.sidebar.warning("⚠️ No te quedan catálogos disponibles")
        elif plan_type == "Tiempo" and expiry_date:
            st.sidebar.caption(f"📅 Vence: **{expiry_date}**")
        
        # CTA WhatsApp
        whatsapp_number = "51921566036"
        whatsapp_message = f"Hola, quiero ampliar mi plan. Mi correo es {user_email}"
        whatsapp_url = f"https://wa.me/{whatsapp_number}?text={quote(whatsapp_message)}"
        
        st.sidebar.markdown(
            f'<a href="{whatsapp_url}" target="_blank" style="text-decoration: none;">'
            f'<div style="background: linear-gradient(90deg, #25D366 0%, #128C7E 100%); '
            f'color: white; padding: 0.5rem 1rem; border-radius: 8px; text-align: center; '
            f'font-weight: bold; margin-top: 0.5rem;">📱 Comprar / Ampliar plan</div></a>',
            unsafe_allow_html=True
        )
        
        st.sidebar.markdown("---")

        with st.sidebar.expander("🏢 Negocio", expanded=True):
            business_name = st.text_input(
                "Nombre", 
                user_info.get('business_name', 'Mi Empresa'), 
                key="biz",
                on_change=lambda: auth.update_user_settings(user_email, business_name=st.session_state.biz)
            )
            currency = st.selectbox(
                "Moneda", 
                ["S/", "$", "€", "£"], 
                index=["S/", "$", "€", "£"].index(user_info.get('currency', 'S/')),
                key="cur",
                on_change=lambda: auth.update_user_settings(user_email, currency=st.session_state.cur)
            )
            phone_number = st.text_input(
                "Número de WhatsApp", 
                user_info.get('phone_number', ''),
                placeholder="Ej: 51987654321", 
                key="phone",
                on_change=lambda: auth.update_user_settings(user_email, phone_number=st.session_state.phone)
            )

        with st.sidebar.expander("🎨 Diseño", expanded=False):
            columns = st.slider("Columnas", 1, 4, 3, key="col")
            uploaded_logo = st.file_uploader("Logo", type=['png','jpg','jpeg'], key="log")
            if uploaded_logo:
                st.image(uploaded_logo, width=200)
                st.session_state.logo = uploaded_logo
            else:
                st.session_state.logo = None
            
            pdf_custom_title = st.text_input(
                "Título PDF", 
                user_info.get('pdf_custom_title', ''), 
                key="pdf_title",
                on_change=lambda: auth.update_user_settings(user_email, pdf_custom_title=st.session_state.pdf_title)
            )
            pdf_custom_subtitle = st.text_input(
                "Subtítulo PDF", 
                user_info.get('pdf_custom_subtitle', ''), 
                key="pdf_subtitle",
                on_change=lambda: auth.update_user_settings(user_email, pdf_custom_subtitle=st.session_state.pdf_subtitle)
            )
            st.session_state.pdf_columns = st.slider("Columnas PDF", 1, 3, 2, key="pdf_col")
            
            # CP-UX-PDF-006: Layout Switch
            pdf_layout = st.selectbox(
                "Diseño del PDF",
                ["Profesional (v2)", "Clásico (v1)"],
                index=0, # Default to Pro
                key="pdf_layout_choice",
                help="Pro: Diseño corporativo, imágenes fijas, cero 'nan'. Clásico: Versión anterior."
            )
            st.session_state.pdf_use_pro = (pdf_layout == "Profesional (v2)")

        # CP-FEAT-007: Branding Configuration
        with st.sidebar.expander("🎨 Configuración de Marca (Nuevo)", expanded=False):
            st.caption("Personaliza los colores de tu catálogo")
            
            # Defaults
            DEFAULT_COLORS = {
                'primary': '#2c3e50',   # Dark Blue
                'secondary': '#e74c3c', # Red
                'accent': '#3498db',    # Light Blue
                'text': '#2c3e50'       # Dark Gray
            }
            
            if st.button("Restaurar colores por defecto", key="reset_brand"):
                st.session_state.brand_primary = DEFAULT_COLORS['primary']
                st.session_state.brand_secondary = DEFAULT_COLORS['secondary']
                st.session_state.brand_accent = DEFAULT_COLORS['accent']
                st.session_state.brand_text = DEFAULT_COLORS['text']
                st.rerun()

            c_b1, c_b2 = st.columns(2)
            brand_primary = c_b1.color_picker("Primario (Títulos)", st.session_state.get('brand_primary', DEFAULT_COLORS['primary']), key="brand_primary")
            brand_secondary = c_b2.color_picker("Secundario (Destacado)", st.session_state.get('brand_secondary', DEFAULT_COLORS['secondary']), key="brand_secondary")
            
            c_b3, c_b4 = st.columns(2)
            brand_accent = c_b3.color_picker("Acento (Detalles)", st.session_state.get('brand_accent', DEFAULT_COLORS['accent']), key="brand_accent")
            brand_text = c_b4.color_picker("Texto Principal", st.session_state.get('brand_text', DEFAULT_COLORS['text']), key="brand_text")
            
            # Store in session for easy access
            st.session_state.branding_config = {
                'primary': brand_primary,
                'secondary': brand_secondary,
                'accent': brand_accent,
                'text': brand_text
            }
        
        st.session_state.business_name = business_name
        st.session_state.currency = currency
        st.session_state.columns = columns
        st.session_state.phone_number = phone_number
        st.session_state.pdf_custom_title = pdf_custom_title
        st.session_state.pdf_custom_subtitle = pdf_custom_subtitle
        
        st.sidebar.markdown("---")
        st.sidebar.caption("v1.3.1 (Hotfix) - 29/12/2025")

                
    def render_main_content(self, is_admin):
        # Define Tabs
        # Base tabs
        tabs_titles = ["📊 Cargar", "🛒 Catálogo", "📲 WhatsApp", "📄 Descargar PDF", "📧 Email"]
        if is_admin:
             tabs_titles.append("👨‍💼 Admin")
        
        # Create Tabs
        tabs = st.tabs(tabs_titles)
        
        # 0. Cargar
        with tabs[0]:
            self.render_data_loading()
            
        # 1. Catálogo (Preview)
        with tabs[1]:
            if 'df' in st.session_state and st.session_state.df is not None:
                # Set defaults for view settings
                if 'items_per_page' not in st.session_state:
                    st.session_state.items_per_page = 48
                if 'show_preview_images' not in st.session_state:
                    st.session_state.show_preview_images = True

                self.render_catalog()
            else:
                self.render_empty_state('no_data', 'catalog_tab_no_df')
                
        # 2. WhatsApp
        with tabs[2]:
             if hasattr(self, 'render_whatsapp_tab'):
                 self.render_whatsapp_tab()
             else:
                 st.info("Módulo WhatsApp en construcción")
             
        # 3. Exportar
        with tabs[3]:
            # Export tab - Decoupled
            self.render_export_options()
            
        # 4. Email
        with tabs[4]:
             if hasattr(self, 'render_email_interface'):
                self.render_email_interface()
             else:
                 st.info("Módulo Email en construcción")

        # 5. Admin (Optional)
        if is_admin and len(tabs) > 5:
            with tabs[5]:
                if hasattr(self, 'render_admin_panel'):
                    self.render_admin_panel()
                else:
                    st.warning("Panel de Admin no encontrado")
    
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
        # CP-UX-010 v3: Premium Import UI - Adaptive Source Selector
        st.markdown("## Importar Datos")
        st.caption("Carga tu inventario desde Excel o Google Sheets para generar catálogos profesionales")
        
        # Initialize session state
        if 'import_stage' not in st.session_state:
            st.session_state.import_stage = 'select'
        if 'preview_data' not in st.session_state:
            st.session_state.preview_data = None
        if 'validation_status' not in st.session_state:
            st.session_state.validation_status = 'idle'
        
        # CP-UX-010 v5: Show loaded data info + reset button with modal
        if 'df' in st.session_state and st.session_state.df is not None:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.info(f"**{len(st.session_state.df)} productos** cargados")
            with col2:
                if st.button("Reiniciar importación", type="secondary", key="reset_btn"):
                    st.session_state.show_reset_modal = True
                    st.rerun()
        
        # CP-UX-010 v5: Reset confirmation modal (corporate style)
        if st.session_state.get('show_reset_modal', False):
            st.markdown("---")
            st.warning("### Confirmar reinicio")
            st.markdown("""
            Esto reiniciará la importación actual y eliminará:
            
            • Todos los datos cargados
            • Vista previa y métricas
            • Resultados de validación
            • Configuración actual
            
            ¿Deseas continuar?
            """)
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                if st.button("Cancelar", type="secondary", key="cancel_reset"):
                    st.session_state.show_reset_modal = False
                    st.rerun()
            
            with col2:
                if st.button("Reiniciar", type="primary", key="confirm_reset"):
                    # Reset COMPLETO - Limpiar AMBOS tabs
                    st.session_state.df = None
                    st.session_state.data_sources = []
                    
                    # Limpiar estado de Excel
                    st.session_state.excel_preview_data = None
                    st.session_state.excel_import_stage = 'select'
                    
                    # Limpiar estado de Sheets
                    st.session_state.sheets_preview_data = None
                    st.session_state.sheets_import_stage = 'select'
                    
                    # Limpiar variables legacy (por compatibilidad)
                    st.session_state.preview_data = None
                    st.session_state.import_stage = 'select'
                    st.session_state.validation_result = None
                    st.session_state.validation_status = 'idle'
                    
                    st.session_state.current_page = 1
                    st.session_state.show_reset_modal = False
                    
                    st.success("**Importación reiniciada exitosamente**")
                    st.rerun()
        
        st.markdown("---")
        
        # CP-UX-010 v3: Adaptive Source Selector (Tabs)
        tab_excel, tab_sheets = st.tabs(["📄 Excel", "📊 Google Sheets"])
        
        # ===== EXCEL TAB =====
        with tab_excel:
            st.markdown("### Importar desde Excel")
            st.caption("Sube tu archivo .xlsx con el inventario")
            
            # CP-UX-010 v4: FRD Schema Display
            self._render_frd_schema(method='excel')
            
            st.markdown("---")
            
            # File uploader
            file = st.file_uploader(
                "Selecciona tu archivo",
                type=['xlsx'],
                key="exc",
                help="Arrastra y suelta o haz click para seleccionar"
            )
            
            # Process Excel file
            if file:
                try:
                    # Load data
                    with st.spinner("Importando datos..."):
                        df = self.data_handler.load_excel(file)
                    
                    # Store in Excel-specific preview
                    st.session_state.excel_preview_data = df
                    st.session_state.excel_import_stage = 'preview'
                    
                    # Render preview workflow
                    self._render_preview_workflow(df, f"Excel: {file.name}", source_type='excel')
                    
                except Exception as e:
                    st.error(f"**Error al cargar archivo:** {str(e)}")
                    st.caption("Verifica que el archivo contenga las columnas requeridas")
        
        # ===== GOOGLE SHEETS TAB =====
        with tab_sheets:
            st.markdown("### Importar desde Google Sheets")
            st.caption("Conecta tu hoja de cálculo de Google")
            
            # CP-UX-010 v5: FRD Schema Display
            self._render_frd_schema(method='sheets')
            
            st.markdown("---")
            
            # URL input
            url = st.text_input(
                "URL de Google Sheets",
                key="gurl",
                placeholder="https://docs.google.com/spreadsheets/d/...",
                help="Asegúrate de que el documento sea público o compartido como lector"
            )
            
            # Botón Validar
            if st.button("Validar", type="secondary", key="validate_sheets"):
                if url:
                    try:
                        # Limpiar estado anterior de Sheets
                        st.session_state.sheets_preview_data = None
                        st.session_state.sheets_import_stage = 'select'
                        
                        # Validar y cargar datos
                        with st.spinner("Validando conexión y cargando datos..."):
                            df = self.data_handler.load_google_sheets(url)
                        
                        # Guardar en Sheets-specific preview
                        st.session_state.sheets_preview_data = df
                        st.session_state.sheets_import_stage = 'preview'
                        st.session_state.sheets_url = url
                        
                        st.success("URL válida y accesible")
                        st.rerun()
                        
                    except Exception as e:
                        st.error("No se puede acceder al documento")
                        st.caption(f"Error: {str(e)}")
                        st.caption("Verifica que sea público o compartido como lector")
                else:
                    st.warning("Por favor ingresa una URL")
            
            # Mostrar preview si existe (usando variables específicas de Sheets)
            if (st.session_state.get('sheets_import_stage') == 'preview' and 
                st.session_state.get('sheets_preview_data') is not None):
                df = st.session_state.sheets_preview_data
                source_name = f"Google Sheets: {st.session_state.get('sheets_url', 'URL')}"
                self._render_preview_workflow(df, source_name, source_type='sheets')
        
        
        # CP-UX-011: Removed _render_data_table_premium() - Not in FRD
        # Data preview is in Catalog tab (S-04), not in Load tab (S-02)
    
    def _render_frd_schema(self, method='excel'):
        """CP-UX-010 v5: Esquema FRD contraído con resumen visible y auto-expansión inteligente"""
        
        # Calcular resumen
        required_count = len(get_required_columns())
        optional_count = len(get_optional_columns())
        total_count = len(get_all_columns())
        
        # Determinar si debe estar expandido
        auto_expand = False
        
        # Auto-expandir SOLO si hay errores de estructura
        validation_result = st.session_state.get('validation_result')
        if validation_result and isinstance(validation_result, dict):
            errors = validation_result.get('errors', [])
            if errors:
                for error in errors:
                    if error.get('type') == 'MISSING_REQUIRED_COLUMN':
                        auto_expand = True
                        break
        
        # Resumen visible (siempre)
        summary = f"{total_count} columnas | {required_count} obligatorias | {optional_count} opcionales"
        
        # Expander con resumen
        with st.expander(f"Esquema de datos (FRD) — {summary}", expanded=auto_expand):
            st.caption("Tu archivo debe contener las siguientes columnas:")
            
            # Tabla de esquema (sin emojis)
            schema_data = []
            for col_name, spec in FRD_SCHEMA.items():
                estado = "Obligatorio" if spec['required'] else "Opcional"
                schema_data.append({
                    'Columna': col_name,
                    'Estado': estado,
                    'Tipo': spec['type'],
                    'Ejemplo': str(spec['example'])
                })
            
            df_schema = pd.DataFrame(schema_data)
            st.dataframe(df_schema, use_container_width=True, height=400)
        
        # Botón siempre visible (fuera del expander)
        if method == 'excel':
            template_df = pd.DataFrame({col: [spec['example']] 
                                       for col, spec in FRD_SCHEMA.items()})
            csv = template_df.to_csv(index=False)
            st.download_button(
                "Descargar plantilla",
                csv,
                "plantilla_catalogpro.csv",
                "text/csv",
                type="secondary"
            )
        else:  # sheets
            st.info("""
            **Para Google Sheets:**
            1. Crea una hoja con las columnas listadas arriba
            2. La primera fila debe contener los nombres exactos
            3. Asegúrate de que el documento sea público o compartido como lector
            """)
    
    def _render_preview_workflow(self, df, source_name, source_type='excel'):
        """CP-UX-010 v5: Vista previa con validación FRD (terminología corporativa en español)"""
        # source_type: 'excel' o 'sheets' para keys únicas
        st.markdown("---")
        st.markdown("## Vista previa de importación")
        st.caption(f"Fuente: {source_name}")
        
        # Ejecutar validación
        validator = FRDValidator(df)
        validation_result = validator.validate()
        
        # Resumen ejecutivo
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Filas detectadas", len(df))
        
        with col2:
            st.metric("Columnas detectadas", len(df.columns))
        
        with col3:
            error_count = validation_result['error_count']
            st.metric(
                "Errores", 
                error_count,
                delta="Bloquea importación" if error_count > 0 else "Sin errores",
                delta_color="inverse" if error_count > 0 else "normal"
            )
        
        with col4:
            warning_count = validation_result['warning_count']
            st.metric(
                "Observaciones", 
                warning_count,
                delta="Revisar" if warning_count > 0 else "Sin observaciones",
                delta_color="off"
            )
        
        # Mostrar errores y observaciones
        if not validation_result['is_valid']:
            st.error("**Importación bloqueada:** Se encontraron errores en campos obligatorios")
            
            with st.expander("Ver detalle de errores", expanded=True):
                for error in validation_result['errors']:
                    st.markdown(f"**{error['type']}:** {error['message']}")
                    if error.get('affected_rows'):
                        rows_str = ', '.join(map(str, error['affected_rows'][:5]))
                        if error.get('total_affected', 0) > 5:
                            rows_str += f" ... (+{error['total_affected'] - 5} más)"
                        st.caption(f"Filas afectadas: {rows_str}")
        
        if validation_result['warnings']:
            st.warning("**Observaciones encontradas:** Campos opcionales con valores vacíos")
            
            with st.expander("Ver detalle de observaciones", expanded=False):
                for warning in validation_result['warnings']:
                    st.markdown(f"**{warning['type']}:** {warning['message']}")
        
        # Vista previa de 20 filas
        st.markdown("**Primeras 20 filas:**")
        st.caption("Las columnas obligatorias son esenciales para la importación")
        
        preview_df = df.head(20).copy()
        
        # Truncate long descriptions for preview
        if 'Descripción' in preview_df.columns:
            preview_df['Descripción'] = preview_df['Descripción'].apply(
                lambda x: str(x)[:60]+'...' if len(str(x)) > 60 else str(x)
            )
        
        st.dataframe(preview_df, use_container_width=True, height=400)
        
        # Guardar resultado de validación en session state
        st.session_state.validation_result = validation_result
        
        # Botones de acción
        st.markdown("---")
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("← Cancelar", type="secondary", key=f"cancel_import_{source_type}"):
                st.session_state.import_stage = 'select'
                st.session_state.preview_data = None
                st.session_state.validation_result = None
                st.rerun()
        
        with col2:
            # Deshabilitar si hay errores
            can_import = validation_result['is_valid']
            
            button_label = "Confirmar importación" if can_import else "Importación bloqueada"
            
            # Usar un placeholder para el botón y feedback
            button_placeholder = st.empty()
            feedback_placeholder = st.empty()
            
            if button_placeholder.button(
                button_label, 
                type="primary" if can_import else "secondary",
                key=f"confirm_import_{source_type}",
                disabled=not can_import
            ):
                if can_import:
                    try:
                        # Mostrar estado "Importando..."
                        button_placeholder.button("Importando…", type="primary", disabled=True, key=f"importing_btn_{source_type}")
                        
                        with feedback_placeholder:
                            with st.spinner("Procesando datos..."):
                                cleaned = self.data_cleaner.clean_data(df)
                                self.render_data_loading_with_progress(df, cleaned, source_name)
                        
                        st.session_state.import_stage = 'confirmed'
                        
                        # Limpiar placeholders
                        button_placeholder.empty()
                        feedback_placeholder.empty()
                        
                        # Mostrar resultado de importación
                        st.markdown("---")
                        st.success("### Importación completada")
                        
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            st.metric("Productos registrados", len(st.session_state.df))
                        with col_b:
                            obs_count = len(validation_result.get('warnings', []))
                            st.metric("Observaciones", obs_count)
                        with col_c:
                            st.metric("Errores", 0)
                        
                        # Mostrar observaciones si las hay
                        if validation_result['warnings']:
                            with st.expander(f"Ver {len(validation_result['warnings'])} observaciones", expanded=False):
                                for warning in validation_result['warnings']:
                                    st.caption(f"• {warning['message']}")
                        
                        st.rerun()
                        
                    except Exception as e:
                        button_placeholder.empty()
                        feedback_placeholder.empty()
                        st.error(f"**Error durante la importación:** {str(e)}")
                        st.caption("Verifica que el archivo tenga la estructura correcta")
    

    def render_catalog(self):
        # CP-UX-009 ROLLBACK: Original header with minimal improvements
        st.header("Vista Previa del Catálogo")

        if 'df' in st.session_state and st.session_state.df is not None:
            st.session_state.viewed_catalog = True
            df = st.session_state.df
            
            # --- View Settings ---
            show_images = st.session_state.get('show_preview_images', True)
            currency = st.session_state.currency if 'currency' in st.session_state else "S/"
            columns = 3

            # CP-UX-009: Progressive filters - ONLY improvement kept
            search = st.text_input(
                "Búsqueda rápida", 
                key="srch", 
                placeholder="Buscar por nombre, código o descripción..."
            )
            
            # CP-UX-009: Advanced Filters - Collapsed by default
            with st.expander("⚙️ Filtros Avanzados", expanded=False):
                
                # --- Hierarchical Filters ---
                st.subheader("Filtros Jerárquicos")
                c1, c2, c3 = st.columns(3)
            
                # 1. Linear Filter
                unique_lines = df['Línea'].unique()
                unique_lines = [x for x in unique_lines if pd.notna(x)]
                available_lines = ['Todas'] + sorted(list(unique_lines))
                selected_line = c1.selectbox("Línea", available_lines, key="fil_line")
                
                # 2. Family Filter (Dependent on Line)
                if selected_line != 'Todas':
                    unique_families = df[df['Línea'] == selected_line]['Familia'].unique()
                else:
                    unique_families = df['Familia'].unique()
                
                unique_families = [x for x in unique_families if pd.notna(x)]
                available_families = ['Todas'] + sorted(list(unique_families))
                selected_family = c2.selectbox("Familia", available_families, key="fil_fam")
                
                # 3. Brand Filter
                unique_brands = df['Marca'].unique()
                brands = sorted([x for x in unique_brands if pd.notna(x)])
                selected_brands = c3.multiselect("Marca", brands, key="fil_brand")

                # --- Additional Filters ---
                st.markdown("**Filtros Adicionales**")
                f1, f2, f3 = st.columns(3)
                
                # 4. Group Filter (Dependent on Family)
                if selected_family != 'Todas':
                     unique_groups = df[(df['Línea'] == selected_line) & (df['Familia'] == selected_family)]['Grupo'].unique() if selected_line != 'Todas' else df[df['Familia'] == selected_family]['Grupo'].unique()
                elif selected_line != 'Todas':
                     unique_groups = df[df['Línea'] == selected_line]['Grupo'].unique()
                else:
                     unique_groups = df['Grupo'].unique() if 'Grupo' in df.columns else []

                unique_groups = [g for g in unique_groups if pd.notna(g)]
                available_groups = ['Todos'] + sorted(list(unique_groups))
                selected_group = f1.selectbox("Grupo", available_groups, key="fil_group")
                
                # 5. Stock Filter
                min_stock = f2.number_input("Stock >=", min_value=0, value=0, step=1, key="fil_stock", help="Muestra productos con stock mayor o igual a este número.")
                
                # 6. Photo Filter
                only_with_photo = f3.checkbox("📸 Solo con Foto", value=False, key="fil_photo")

                # --- Price Range ---
                st.markdown("**Rango de Precio**")
                # Handle empty price range safely
                if not df.empty and 'Precio' in df.columns:
                    minp = float(df['Precio'].min())
                    maxp = float(df['Precio'].max())
                else:
                    minp, maxp = 0.0, 0.0

                if minp == maxp:
                    prange = (minp, maxp)
                else:
                    prange = st.slider("Selecciona rango", minp, maxp, (minp, maxp), key="pr", label_visibility="collapsed")
            
            # CP-UX-009: Set defaults for filters when not using expander
            if 'fil_line' not in st.session_state:
                selected_line = 'Todas'
                selected_family = 'Todas'
                selected_group = 'Todos'
                selected_brands = []
                min_stock = 0
                only_with_photo = False
                minp = float(df['Precio'].min()) if not df.empty else 0.0
                maxp = float(df['Precio'].max()) if not df.empty else 0.0
                prange = (minp, maxp)

            # --- Apply Filters ---
            filtered = df.copy()
            
            # Hierarchy
            if selected_line != 'Todas':
                filtered = filtered[filtered['Línea'] == selected_line]
            if selected_family != 'Todas':
                filtered = filtered[filtered['Familia'] == selected_family]
            if selected_group != 'Todos':
                filtered = filtered[filtered['Grupo'] == selected_group]
            if selected_brands:
                filtered = filtered[filtered['Marca'].isin(selected_brands)]
            
            # New Filters Logic
            if min_stock > 0 and 'Stock' in filtered.columns:
                filtered = filtered[filtered['Stock'] >= min_stock]
            
            if only_with_photo:
                # Filter rows where ImagenURL is not valid/empty
                filtered = filtered[filtered['ImagenURL'].notna() & (filtered['ImagenURL'].astype(str) != 'nan') & (filtered['ImagenURL'].astype(str).str.strip() != '')]

            # Basic
            if search:
                # FIX (CP-BUG-010): Force string conversion to avoid AccessorError on numeric columns
                mask = filtered['Producto'].astype(str).str.contains(search, case=False, na=False) | \
                       filtered['Descripción'].astype(str).str.contains(search, case=False, na=False)
                if 'Código' in filtered.columns:
                     mask |= filtered['Código'].astype(str).str.contains(search, case=False, na=False)
                filtered = filtered[mask]
            
            if not filtered.empty:
                filtered = filtered[(filtered['Precio']>=prange[0]) & (filtered['Precio']<=prange[1])]

            # --- PERSISTENCE FOR EXPORT (CP-FEAT-008) ---
            st.session_state.filtered_df = filtered

            if len(filtered) == 0:
                self.render_empty_state('no_results', 'catalog_tab_no_results')
                return

            # --- Pagination Logic (Applied on Filtered Data) ---
            total_products = len(filtered)
            if 'items_per_page' not in st.session_state:
                st.session_state.items_per_page = 24
            if 'preview_page' not in st.session_state:
                st.session_state.preview_page = 1
                
            total_pages = math.ceil(total_products / st.session_state.items_per_page)
            if total_pages == 0: total_pages = 1
            
            # Reset page if filter reduces counts below current page bounds
            if st.session_state.preview_page > total_pages:
                st.session_state.preview_page = 1
                
            current_page = st.session_state.preview_page
            start_idx = (current_page - 1) * st.session_state.items_per_page
            end_idx = min(start_idx + st.session_state.items_per_page, total_products)
            
            # Select slice
            page_df = filtered.iloc[start_idx:end_idx]
            
            # --- Pagination Controls ---
            st.divider()
            kc1, kc2, kc3 = st.columns([3, 4, 3])
            with kc1:
                st.caption(f"Mostrando {start_idx + 1} - {end_idx} de {total_products}")
            with kc3:
                # CP-UX-009 v3: Compact, professional navigation buttons
                c_prev, c_page, c_next = st.columns([1, 2, 1])
                with c_prev:
                    if st.button("←", key="p_prev", disabled=current_page==1, help="Página anterior"):
                        st.session_state.preview_page -= 1
                        st.rerun()
                with c_next:
                    if st.button("→", key="p_next", disabled=current_page>=total_pages, help="Página siguiente"):
                        st.session_state.preview_page += 1
                        st.rerun()
                with c_page:
                    st.caption(f"Pág {current_page}/{total_pages}")
            
            # ROLLBACK: Original grid rendering with cards
            rows = math.ceil(len(page_df) / columns)
            for row in range(rows):
                cols = st.columns(columns)
                for col_idx in range(columns):
                    local_idx = row * columns + col_idx
                    if local_idx < len(page_df):
                        product = page_df.iloc[local_idx]
                        with cols[col_idx]:
                            self.catalog_generator._render_product_card(product, currency, start_idx + local_idx, row, show_images)
            
            st.divider()
        else:
            self.render_empty_state('no_data', 'catalog_tab_no_df')
        
    def render_export_options(self):
        # CP-UX-002: Header y microcopy simple
        st.markdown("## 📄 Paso final: descarga tu catálogo")
        
        st.info("""
        **Genera un PDF premium listo para compartir por WhatsApp y redes.**
        
        💡 Nota: cada descarga exitosa del PDF cuenta como 1 catálogo generado.
        """)
        
        if 'df' not in st.session_state or st.session_state.df is None:
            st.warning("⚠️ Primero carga datos en la pestaña '📊 Cargar'")
            return
            
        # Use Filtered Data (CP-FEAT-008)
        full_df = st.session_state.df
        df = st.session_state.get('filtered_df', full_df)
        
        # Fallback if filtered is empty but shouldn't be (sanity check)
        if df is None: df = full_df

        st.caption(f"📤 Se exportarán **{len(df)}** productos (de un total de {len(full_df)}). Los filtros aplicados en la pestaña 'Catálogo' se respetan aquí.")
        
        # --- Control Panel ---
        st.markdown("### 🎛️ Panel de Control")
        
        # CP-UX-001: Defaults Premium forzados
        use_optimized = True  # Motor Premium por defecto
        compatibility_mode = False  # Modo compatibilidad desactivado por defecto
        
        # CP-UX-001: Sección Admin/Avanzado (Solo para Admin)
        is_admin = st.session_state.get('user_info', {}).get('is_admin', False)
        
        if is_admin:
            with st.expander("⚙️ Avanzado (Solo Soporte)", expanded=False):
                st.warning("⚠️ **Uso exclusivo para soporte técnico**\n\nActivar solo si la exportación Premium presenta problemas.")
                compatibility_mode = st.checkbox(
                    "Modo compatibilidad (Motor Legacy)",
                    value=False,
                    help="Desactiva optimizaciones y usa motor clásico. Usar solo si hay errores con el motor Premium."
                )
                
                if compatibility_mode:
                    use_optimized = False
                    st.info("ℹ️ Modo compatibilidad activado: Motor Legacy sin optimizaciones")
        
        c_action, c_download = st.columns([1, 2])
            
        with c_action:
            # Disable if already generating handled by Streamlit spinner mostly, 
            # but we can use session state to show different label if needed.
            generate_btn = st.button("⚡ Descargar PDF Premium", type="primary", use_container_width=True)
            
        with c_download:
            if 'pdf_generated' in st.session_state and st.session_state['pdf_generated']:
                st.download_button(
                    label="⬇️ Descargar PDF (Último)",
                    data=st.session_state['pdf_generated'],
                    file_name=f"catalogo_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                    mime="application/pdf",
                    type="secondary",
                    use_container_width=True
                )
            else:
                st.caption("👈 Genera el PDF primero para descargar.")

        # --- Generation Logic ---
        if generate_btn:
            progress_bar = st.progress(0)
            status_container = st.empty()
            detailed_status = st.empty()
            
            try:
                status_container.info("⏳ Iniciando generación Premium...")
                
                if use_optimized:
                    # UX: Progress Handler with Time Estimation
                    start_gen_time = time.time()
                    
                    def progress_handler(percentage, msg=""):
                         elapsed = time.time() - start_gen_time
                         progress_bar.progress(percentage)
                         status_container.markdown(f"**Estado:** {msg}")
                         detailed_status.caption(f"⏱️ Tiempo transcurrido: {elapsed:.1f}s")

                    pdf_bytes, stats = self.pdf_exporter.generate_pdf_optimized(
                        df,
                        st.session_state.business_name,
                        st.session_state.currency,
                        st.session_state.get('phone_number'),
                        st.session_state.get('user_email'),
                        progress_callback=progress_handler,
                        use_pro_layout=st.session_state.get('pdf_use_pro', True)
                    )
                    st.session_state['last_pdf_stats'] = stats
                else:
                    # CP-UX-001: Modo compatibilidad (solo Admin)
                    with st.spinner("Generando PDF (Modo Compatibilidad)..."):
                        pdf_bytes = self.pdf_exporter.generate_pdf_with_images(
                            df,
                            st.session_state.business_name,
                            st.session_state.currency,
                            st.session_state.get('phone_number'),
                            st.session_state.get('user_email')
                        )
                    st.session_state['last_pdf_stats'] = None

                st.session_state['pdf_generated'] = pdf_bytes
                
                status_container.success("✅ ¡PDF Premium listo! Descárgalo usando el botón de arriba.")
                detailed_status.empty()
                time.sleep(1) # Visual feedback
                st.rerun() # Update UI
                
            except Exception as e:
                # CP-UX-001: Fallback automático con mensaje simple
                status_container.warning("⚠️ Intentando modo compatibilidad automático...")
                
                try:
                    # Fallback: intentar con motor legacy
                    with st.spinner("Generando PDF (Modo Compatibilidad)..."):
                        pdf_bytes = self.pdf_exporter.generate_pdf_with_images(
                            df,
                            st.session_state.business_name,
                            st.session_state.currency,
                            st.session_state.get('phone_number'),
                            st.session_state.get('user_email')
                        )
                    
                    st.session_state['pdf_generated'] = pdf_bytes
                    st.session_state['last_pdf_stats'] = None
                    
                    status_container.success("✅ PDF generado en modo compatibilidad. Descárgalo arriba.")
                    st.info("ℹ️ Se usó el modo compatibilidad debido a un problema temporal.")
                    detailed_status.empty()
                    time.sleep(1)
                    st.rerun()
                    
                except Exception as e2:
                    # CP-UX-001: Mensaje de error simple sin términos técnicos
                    st.error("❌ No se pudo generar el PDF. Por favor, intenta nuevamente o contacta soporte.")
                    if is_admin:
                        # Solo mostrar detalles técnicos a Admin
                        with st.expander("🔧 Detalles Técnicos (Admin)", expanded=False):
                            st.error(f"Error Premium: {str(e)}")
                            st.error(f"Error Fallback: {str(e2)}")
                    st.session_state['pdf_generated'] = None
            finally:
                time.sleep(1)
                progress_bar.empty()

        st.markdown("---")
        
        # --- Info & Metrics ---
        # --- Info & Metrics (Redesigned CP-UX-UI-009) ---
        if st.session_state.get('last_pdf_stats'):
            stats = st.session_state['last_pdf_stats']
            istats = stats.get('img_stats', {})
            
            st.markdown("### 📊 Reporte de Generación")
            
            # KPI Cards
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Productos Exportados", f"{istats.get('total', 0)}")
            k2.metric("Páginas PDF", f"{stats.get('page_count', '?')}")
            k3.metric("Peso Archivo", f"{stats.get('file_size_mb', 0):.2f} MB")
            k4.metric("Imágenes Exitosas", f"{istats.get('ok', 0)}", delta=f"-{istats.get('failed', 0)} fallos" if istats.get('failed', 0) > 0 else "100%", delta_color="normal" if istats.get('failed', 0) > 0 else "off")
            
            if istats.get('failed', 0) > 0:
                st.warning(f"⚠️ Atención: {istats['failed']} imágenes no se pudieron descargar y usan placeholder.")

            # Technical Details (Collapsed)
            with st.expander("⚙️ Detalles Técnicos (Avanzado)", expanded=False):
                 st.caption("Desglose de tiempos de procesamiento:")
                 sc1, sc2, sc3 = st.columns(3)
                 sc1.metric("Tiempo Total", f"{stats.get('total_time', 0):.2f}s")
                 sc2.metric("Descarga Imágenes", f"{stats.get('fetch_time', 0):.2f}s")
                 sc3.metric("Renderizado PDF", f"{stats.get('render_time', 0):.2f}s")
                 st.json(stats) # Full debug view
        
        # --- Secondary Exports (HTML) ---
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("PDF (Información)")
            st.info("""
            **Formato Estandarizado**:
            - Tamaño A4
            - Enlaces de WhatsApp activos
            - Optimizado para email y compartir en móvil.
            Utiliza el botón superior para generar.
            """)
                    
        with c2:
            st.subheader("Catálogo Web (HTML)")
            st.caption("Genera un archivo HTML ligero para compartir como página web.")
            if st.button("🌐 Generar HTML", key="ghml"):
                try:
                    with st.spinner("Generando HTML..."):
                        html = self.html_exporter.generate_html_catalog(
                            df, 
                            st.session_state.business_name, 
                            st.session_state.currency, 
                            st.session_state.get('phone_number'),
                            branding=st.session_state.get('branding_config')
                        )
                        st.download_button("📥 Descargar HTML", html.encode('utf-8'), f"catalogo_{datetime.now().strftime('%Y%m%d')}.html", "text/html", key="dlh")
                        st.success("¡HTML generado! Click en Descargar.")
                except Exception as e:
                    st.error(f"❌ {str(e)}")
            
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
                        pdf = self.pdf_exporter.generate_pdf_with_images(df, st.session_state.business_name, st.session_state.currency, st.session_state.get('phone_number'), st.session_state.get('user_email'))
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
            
        st.markdown("---")
        st.caption("CatalogPro v1.3.1 (Hotfix) - 29/12/2025 | Developed by Antay Perú")

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
    app = EnhancedCatalogApp()
    app.run()