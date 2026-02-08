import streamlit as st
import json
import os
from datetime import datetime
import re
import time
import bcrypt
import pandas as pd
from abc import ABC, abstractmethod

# Intentar importar gspread, manejar error si no está instalado
try:
    import gspread
    from google.oauth2.service_account import Credentials
    HAS_GSPREAD = True
except ImportError:
    HAS_GSPREAD = False

# Intentar importar supabase, manejar error si no está instalado
try:
    from supabase import create_client, Client
    HAS_SUPABASE = True
except ImportError:
    HAS_SUPABASE = False

def is_valid_email(email: str) -> bool:
    """Validar formato de email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

class AuthBackend(ABC):
    """Interfaz abstracta para backends de autenticación"""
    @abstractmethod
    def load_users(self) -> dict:
        pass
    
    @abstractmethod
    def save_users(self, users_data: dict):
        pass

class JsonBackend(AuthBackend):
    """Backend local usando archivo JSON"""
    def __init__(self, filename="authorized_users.json"):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.filepath = os.path.join(base_dir, filename)
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        if not os.path.exists(self.filepath):
            # Admin por defecto: admin/C4m1l02012
            default_password = "C4m1l02012"
            hashed_password = bcrypt.hashpw(default_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            initial_data = {
                "users": {
                    "admin@antayperu.com": {
                        "name": "Administrador",
                        "business_name": "CatalogPro",
                        "is_admin": True,
                        "password_hash": hashed_password,
                        "created_at": datetime.now().isoformat(),
                        "last_login": None,
                        "currency": "S/",
                        "phone_number": ""
                    }
                }
            }
            with open(self.filepath, 'w') as f:
                json.dump(initial_data, f, indent=2)

    def load_users(self) -> dict:
        try:
            with open(self.filepath, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self._ensure_file_exists()
            return self.load_users()

    def save_users(self, users_data: dict):
        with open(self.filepath, 'w') as f:
            json.dump(users_data, f, indent=2)

class GoogleSheetsBackend(AuthBackend):
    """Backend en la nube usando Google Sheets"""
    def __init__(self, service_account_info: dict, sheet_url: str):
        if not HAS_GSPREAD:
            raise ImportError("gspread no está instalado")
        
        self.scope = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        self.creds = Credentials.from_service_account_info(service_account_info, scopes=self.scope)
        self.client = gspread.authorize(self.creds)
        self.sheet_url = sheet_url
        
        # Definir columnas explícitas para permitir edición manual en Sheets
        self.columns = [
            "email", "name", "business_name", "is_admin", "password_hash", 
            "created_at", "last_login", "currency", "phone_number", 
            "plan_type", "quota", "quota_max", "expires_at", "status", 
            "extra_data" # Para campos futuros o settings no estructurados
        ]
        self._ensure_sheet_structure()

    def _get_worksheet(self):
        try:
            sheet = self.client.open_by_url(self.sheet_url)
            return sheet.worksheet("Users")
        except gspread.WorksheetNotFound:
            sheet = self.client.open_by_url(self.sheet_url)
            return sheet.add_worksheet(title="Users", rows=100, cols=20)
        except Exception as e:
            st.error(f"Error conectando a Google Sheets: {str(e)}")
            raise e

    def _ensure_sheet_structure(self):
        """Verificar headers iniciales"""
        ws = self._get_worksheet()
        headers = ws.row_values(1)
        
        # Si está vacío o tiene headers antiguos (solo email, data), no limpiamos automáticamente 
        # para evitar pérdida de datos antes de la migración.
        # save_users() se encargará de migrar la estructura al guardar.
        if not headers:
            ws.append_row(self.columns)
            
            # Admin default si es hoja nueva
            default_password = "admin" # Fallback temporal
            secure_password = "C4m1l02012" # Nuevo estándar
            
            hashed = bcrypt.hashpw(secure_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            # Escribir fila de admin
            self.save_users({"users": {"admin@antayperu.com": {
                "name": "Administrador",
                "business_name": "CatalogPro",
                "is_admin": True,
                "password_hash": hashed,
                "created_at": datetime.now().isoformat(),
                "last_login": None,
                "currency": "S/",
                "phone_number": "",
                "plan_type": "Free",
                "quota": 9999,
                "quota_max": 9999
            }}})

    def load_users(self) -> dict:
        ws = self._get_worksheet()
        records = ws.get_all_records()
        users_dict = {}
        
        for row in records:
            email = row.get('email')
            if not email: continue
            
            # --- Estrategia Híbrida de Lectura ---
            user_data = {}
            
            # 1. Intentar leer de columna 'data' (Legacy/Hybrid)
            if 'data' in row and row['data']:
                try:
                    user_data.update(json.loads(row['data']))
                except:
                    pass
                    
            # 2. Intentar leer de 'extra_data' (New)
            if 'extra_data' in row and row['extra_data']:
                try:
                    user_data.update(json.loads(row['extra_data']))
                except:
                    pass

            # 3. Leer columnas explícitas (Sobreescriben JSON si existen)
            # Mapeamos columnas a claves del dict
            field_map = {
                "name": "name",
                "business_name": "business_name",
                "is_admin": "is_admin",
                "password_hash": "password_hash",
                "created_at": "created_at",
                "last_login": "last_login",
                "currency": "currency",
                "phone_number": "phone_number",
                "plan_type": "plan_type",
                "quota": "quota",
                "quota_max": "quota_max",
                "expires_at": "expires_at",
                "status": "status"
            }
            
            for col, key in field_map.items():
                if col in row:
                    val = row[col]
                    # Manejo de tipos
                    if key in ["quota", "quota_max"]:
                        # Si está vacío o es string no numérico, usar default del dict o 0
                        if val == "":
                            continue # Mantener lo que venía en JSON o default
                        try:
                            val = int(val)
                        except:
                            val = 0
                    
                    elif key == "is_admin":
                        # ROBUS PARSING: Handle all "FALSE" variants
                        # Google Sheets sometimes returns "FALSE" (str), FALSE (bool), or 0 (int)
                        s_val = str(val).strip().upper()
                        if s_val == "FALSE" or s_val == "0" or s_val == "":
                            val = False
                        elif s_val == "TRUE" or s_val == "1":
                            val = True
                        else:
                            # Fallback standard
                            val = bool(val)

                    user_data[key] = val
            
            # Defaults críticos si no existen
            if "plan_type" not in user_data: user_data["plan_type"] = "Free"
            if "quota" not in user_data: user_data["quota"] = 5
            if "quota_max" not in user_data: user_data["quota_max"] = 5
            
            users_dict[email] = user_data
        return {"users": users_dict}

    def save_users(self, users_data: dict):
        """
        Guarda usuarios usando el esquema expandido.
        Esto efectúa la migración automática de estructura.
        """
        ws = self._get_worksheet()
        ws.clear()
        ws.append_row(self.columns)
        
        rows = []
        for email, data in users_data.get("users", {}).items():
            row_data = []
            
            # Extraer data estructurada
            extra = data.copy() # Copia para sacar lo extra
            
            # Campos explícitos
            for col in self.columns:
                if col == "email":
                    row_data.append(email)
                elif col == "extra_data":
                    # Lo que queda en 'extra' va aquí
                    row_data.append(json.dumps(extra)) 
                else:
                    # Mapeo directo nombre columna -> key
                    val = data.get(col, "")
                    if val is None: val = ""
                    
                    # Limpieza del dict extra
                    if col in extra:
                        del extra[col]
                        
                    row_data.append(val)
            
            rows.append(row_data)
        
        if rows:
            ws.append_rows(rows)

class SupabaseBackend(AuthBackend):
    """Backend de autenticación con Supabase PostgreSQL"""

    def __init__(self, supabase_url: str, supabase_key: str):
        """
        Args:
            supabase_url: URL del proyecto Supabase (https://xxxxx.supabase.co)
            supabase_key: Service role key (para operaciones admin)
        """
        if not HAS_SUPABASE:
            raise ImportError("supabase no está instalado. Ejecuta: pip install supabase")

        self.client: Client = create_client(supabase_url, supabase_key)
        self.table = "users"

    def load_users(self) -> dict:
        """
        Carga todos los usuarios desde Supabase.

        Returns:
            dict: {"users": {email: user_data, ...}}
        """
        try:
            response = self.client.table(self.table).select("*").execute()

            users = {}
            for row in response.data:
                email = row["email"]

                # Convertir tipos de Supabase a tipos Python
                user_data = {
                    "name": row.get("name", "Usuario"),
                    "business_name": row.get("business_name", ""),
                    "phone_number": row.get("phone_number", ""),
                    "currency": row.get("currency", "S/"),
                    "pdf_custom_title": row.get("pdf_custom_title"),
                    "pdf_custom_subtitle": row.get("pdf_custom_subtitle"),
                    "is_admin": bool(row.get("is_admin", False)),
                    "status": row.get("status", "active"),
                    "password_hash": row.get("password_hash"),
                    "plan_type": row.get("plan_type", "Free"),

                    "quota": int(row.get("quota", 5)),
                    "quota_max": int(row.get("quota_max", 5)),
                    "expires_at": row.get("expires_at"),  # None o fecha en formato ISO
                    "created_at": row.get("created_at"),
                    "last_login": row.get("last_login"),
                    "logo_base64": row.get("logo_base64"),
                    "logo_path": row.get("logo_path"),
                    # CP-UX-020: Fields for configuration and branding (with defaults to avoid Dirty State)
                    "columns_catalog": int(row.get("columns_catalog", 3)) if row.get("columns_catalog") is not None else 3,
                    "pdf_columns": int(row.get("pdf_columns", 2)) if row.get("pdf_columns") is not None else 2,
                    "brand_primary": row.get("brand_primary", "#2c3e50"),
                    "brand_secondary": row.get("brand_secondary", "#e74c3c"),
                    "brand_accent": row.get("brand_accent", "#3498db"),
                    "brand_text": row.get("brand_text", "#2c3e50"),
                    "pdf_layout": row.get("pdf_layout", "Profesional (v2)")
                }

                users[email] = user_data

            return {"users": users}

        except Exception as e:
            print(f"[ERROR] Fallo al cargar usuarios desde Supabase: {e}")
            return {"users": {}}

    def save_users(self, users_data: dict):
        """
        Guarda usuarios en Supabase usando UPSERT.

        Args:
            users_data: dict con clave "users" que contiene {email: user_dict}
        """
        users_dict = users_data.get("users", {})

        for email, user_data in users_dict.items():
            try:

                # Preparar datos para Supabase
                supabase_data = {
                    "email": email,
                    "password_hash": user_data.get("password_hash"),
                    "name": user_data.get("name", "Usuario"),
                    "business_name": user_data.get("business_name", ""),
                    "phone_number": user_data.get("phone_number", ""),
                    "currency": user_data.get("currency", "S/"),
                    "pdf_custom_title": user_data.get("pdf_custom_title"),
                    "pdf_custom_subtitle": user_data.get("pdf_custom_subtitle"),
                    "is_admin": bool(user_data.get("is_admin", False)),
                    "status": user_data.get("status", "active"),
                    "plan_type": user_data.get("plan_type", "Free"),
                    "quota": int(user_data.get("quota", 5)),
                    "quota_max": int(user_data.get("quota_max", 5)),
                    "expires_at": user_data.get("expires_at"),
                    "created_at": user_data.get("created_at"),
                    "last_login": user_data.get("last_login"),
                    "logo_base64": user_data.get("logo_base64"),
                    "logo_path": user_data.get("logo_path"),
                    # CP-UX-020: Fields (Temporarily filtered if Supabase schema is missing them)
                    "columns_catalog": user_data.get("columns_catalog"),
                    "pdf_columns": user_data.get("pdf_columns"),
                    "brand_primary": user_data.get("brand_primary"),
                    "brand_secondary": user_data.get("brand_secondary"),
                    "brand_accent": user_data.get("brand_accent"),
                    "brand_text": user_data.get("brand_text"),
                    "pdf_layout": user_data.get("pdf_layout")
                }

                # UPSERT: Inserta si no existe, actualiza si existe
                # CP-UX-020: Full persistence enabled after migration
                response = self.client.table(self.table).upsert(supabase_data).execute()

            except Exception as e:
                print(f"[ERROR] Fallo al guardar usuario {email}: {e}")
                # Continuar con otros usuarios aunque uno falle

class AuthManager:
    """Gestor de autenticación con soporte híbrido"""
    
    def __init__(self):
        self.admin_email = "admin@antayperu.com"

        # Determinar backend (prioridad: Supabase > Google Sheets > JSON)
        # Prioridad 1: Supabase (PostgreSQL - PRODUCCIÓN)
        if "supabase" in st.secrets:
            try:
                self.backend = SupabaseBackend(
                    st.secrets["supabase"]["SUPABASE_URL"],
                    st.secrets["supabase"]["SUPABASE_KEY"]
                )
                print("[OK] Usando SupabaseBackend (PostgreSQL)")

            except Exception as e:
                print(f"[WARNING] Fallo al conectar Supabase ({e}), probando Google Sheets...")

                # Prioridad 2: Google Sheets (deprecated/fallback)
                if "gcp_service_account" in st.secrets and "auth_sheet_url" in st.secrets.get("general", {}):
                    try:
                        self.backend = GoogleSheetsBackend(
                            st.secrets["gcp_service_account"],
                            st.secrets["general"]["auth_sheet_url"]
                        )
                        print("[OK] Usando GoogleSheetsBackend (fallback)")
                    except Exception as e2:
                        print(f"[WARNING] Google Sheets también falló ({e2}), usando JsonBackend")
                        self.backend = JsonBackend()
                else:
                    print("[INFO] Sin credenciales Google Sheets, usando JsonBackend")
                    self.backend = JsonBackend()

        # Prioridad 2: Google Sheets (si no hay Supabase)
        elif "gcp_service_account" in st.secrets and "auth_sheet_url" in st.secrets.get("general", {}):
            try:
                self.backend = GoogleSheetsBackend(
                    st.secrets["gcp_service_account"],
                    st.secrets["general"]["auth_sheet_url"]
                )
                print("[OK] Usando GoogleSheetsBackend")
            except Exception as e:
                print(f"[WARNING] Fallo al conectar Sheets ({e}), usando JsonBackend")
                self.backend = JsonBackend()

        # Prioridad 3: JsonBackend (fallback final - siempre funciona)
        else:
            print("[INFO] No hay credenciales cloud, usando JsonBackend")
            self.backend = JsonBackend()

        self._load_users()
    
    @property
    def backend_name(self) -> str:
        """Retorna el nombre del backend actual"""
        if isinstance(self.backend, SupabaseBackend): return "Supabase (Postgres)"
        if isinstance(self.backend, GoogleSheetsBackend): return "Google Sheets"
        return "Local JSON"

    def _load_users(self):
        self.users = self.backend.load_users()
    
    def _save_users(self):
        self.backend.save_users(self.users)
    
    def is_authorized(self, email: str) -> bool:
        return email.lower() in [e.lower() for e in self.users["users"].keys()]
    
    def add_user(self, email: str, name: str, business: str, password: str, plan_type: str = "Free", quota: int = 5, quota_max: int = 5, expires_at: str = None) -> bool:
        """Agregar usuario nuevo con contraseña hasheada y detalles de plan"""
        if not is_valid_email(email):
            raise ValueError("Formato de email inválido")
        if not password:
            raise ValueError("La contraseña no puede estar vacía")
        
        email = email.lower().strip()
        if email in self.users["users"]:
            return False
        
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        self.users["users"][email] = {
            "name": name.strip(),
            "business_name": business.strip(),
            "is_admin": False,
            "password_hash": hashed_password,
            "created_at": datetime.now().isoformat(),
            "last_login": None,
            "quota": quota,
            "quota_max": quota_max,
            "plan_type": plan_type,
            "expires_at": expires_at,
            "currency": "S/"
        }
        
        self._save_users()
        return True

    def get_user_quota(self, email: str) -> int:
        """Obtener el saldo de cuota actual del usuario"""
        user_info = self.get_user_info(email)
        # Migración on-the-fly: si no tiene quota, asumir 5 (Free)
        if "quota" not in user_info:
            return 5
        return user_info.get("quota", 0)

    def is_plan_expired(self, email: str) -> bool:
        """Verificar si el plan ha expirado por fecha"""
        user_info = self.get_user_info(email)
        expiry_str = user_info.get("expires_at")
        
        if expiry_str:
            try:
                exp_date = datetime.strptime(expiry_str, "%Y-%m-%d").date()
                if exp_date < datetime.now().date():
                    return True
            except:
                pass # Fecha inválida no bloquea (o debería?) Por ahora permisivo
        return False

    def check_quota(self, email: str) -> bool:
        """
        Verificar si el usuario puede generar. 
        CRITICAL CP-BUG-022: Priorizar fecha de vencimiento sobre saldo de créditos.
        """
        user_info = self.get_user_info(email)
        expiry_str = user_info.get("expires_at")
        
        # 1. Si el usuario tiene una fecha de vencimiento configurada
        if expiry_str:
            if not self.is_plan_expired(email):
                return True # Tiene fecha válida en el futuro -> Acceso Ilimitado (Plan Tiempo/Hybrid)
            else:
                return False # Fecha ya venció -> Acceso denegado (aunque tenga créditos)
                
        # 2. Si no tiene fecha, validar por saldo de créditos (Plan Cantidad/Free tradicional)
        return self.get_user_quota(email) > 0

    def decrement_quota(self, email: str) -> bool:
        """Restar 1 crédito al usuario. Retorna True si fue exitoso y autorizado."""
        # Validación centralizada de acceso (Fecha + Saldo)
        if not self.check_quota(email):
            return False
        
        email = email.lower()
        if email in self.users["users"]:
            current_quota = self.get_user_quota(email)
            self.users["users"][email]["quota"] = current_quota - 1
            self._save_users()
            return True
        return False

    def remove_user(self, email: str) -> bool:
        """
        [DEPRECATED] Eliminar usuario permanentemente.

        NOTA: Este metodo esta deprecado desde v1.5.1 (CP-FEAT-015).
        Usar `block_user()` en su lugar para operaciones normales.
        Solo mantener para testing/desarrollo.

        Args:
            email: Email del usuario a eliminar

        Returns:
            bool: True si fue eliminado, False si no se pudo
        """
        print("[WARNING] remove_user() esta deprecado. Usar block_user() en su lugar.")
        email = email.lower()
        if email == self.admin_email.lower():
            return False

        if email in self.users["users"]:
            del self.users["users"][email]
            self._save_users()
            return True
        return False

    def update_user_plan_details(self, email: str, plan_type: str = None, quota: int = None, quota_max: int = None, expires_at: str = None) -> bool:
        """Actualizar detalles del plan del usuario (Admin function)"""
        email = email.lower()
        if email not in self.users["users"]:
            return False
        
        user = self.users["users"][email]
        changed = False
        
        if plan_type is not None:
            user["plan_type"] = plan_type
            changed = True
        
        if quota is not None:
             user["quota"] = int(quota)
             changed = True
             
        if quota_max is not None:
             user["quota_max"] = int(quota_max)
             changed = True
             
        if expires_at is not None:
             user["expires_at"] = expires_at
             changed = True
             
        if changed:
            self._save_users()
            return True
        return False

    def update_password(self, email: str, new_password: str) -> bool:
        if not new_password:
            raise ValueError("La nueva contraseña no puede estar vacía")
        email = email.lower()
        if email in self.users["users"]:
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            self.users["users"][email]["password_hash"] = hashed_password
            self._save_users()
            return True
        return False

    def verify_password(self, email: str, password: str) -> bool:
        user_info = self.get_user_info(email)
        if user_info and "password_hash" in user_info:
            stored_hash = user_info["password_hash"].encode('utf-8')
            return bcrypt.checkpw(password.encode('utf-8'), stored_hash)
        return False
    
    def get_user_info(self, email: str) -> dict:
        return self.users["users"].get(email.lower(), {})
    
    def is_admin(self, email: str) -> bool:
        user_info = self.get_user_info(email)
        return user_info.get("is_admin", False)
    
    def get_all_users(self) -> list:
        return [{"email": email, "info": info} for email, info in self.users["users"].items()]
    
    def update_last_login(self, email: str):
        email = email.lower()
        if email in self.users["users"]:
            self.users["users"][email]["last_login"] = datetime.now().isoformat()
            self._save_users()

    def toggle_admin_status(self, email: str) -> bool:
        email = email.lower()
        if email == self.admin_email.lower():
            return False
        if email in self.users["users"]:
            current_status = self.users["users"][email].get("is_admin", False)
            self.users["users"][email]["is_admin"] = not current_status
            self._save_users()
            return True
        return False

    def block_user(self, email: str) -> bool:
        """
        Bloquear usuario (cambiar status a 'blocked').

        Args:
            email: Email del usuario a bloquear

        Returns:
            bool: True si fue bloqueado exitosamente, False si no se pudo

        Restricciones:
            - No se puede bloquear al admin principal
            - No se puede bloquear a un usuario ya bloqueado
        """
        email = email.lower()

        # Proteccion: No bloquear al admin principal
        if email == self.admin_email.lower():
            print(f"[WARNING] Intento de bloquear admin principal bloqueado: {email}")
            return False

        # Verificar que el usuario existe
        if email not in self.users["users"]:
            print(f"[WARNING] Usuario no encontrado para bloqueo: {email}")
            return False

        # Verificar estado actual
        current_status = self.users["users"][email].get("status", "active")
        if current_status == "blocked":
            print(f"[INFO] Usuario ya estaba bloqueado: {email}")
            return False

        # Bloquear usuario
        self.users["users"][email]["status"] = "blocked"
        self._save_users()

        print(f"[OK] Usuario bloqueado exitosamente: {email}")
        return True

    def unblock_user(self, email: str) -> bool:
        """
        Desbloquear usuario (cambiar status a 'active').

        Args:
            email: Email del usuario a desbloquear

        Returns:
            bool: True si fue desbloqueado exitosamente, False si no se pudo
        """
        email = email.lower()

        # Verificar que el usuario existe
        if email not in self.users["users"]:
            print(f"[WARNING] Usuario no encontrado para desbloqueo: {email}")
            return False

        # Verificar estado actual
        current_status = self.users["users"][email].get("status", "active")
        if current_status == "active":
            print(f"[INFO] Usuario ya estaba activo: {email}")
            return False

        # Desbloquear usuario
        self.users["users"][email]["status"] = "active"
        self._save_users()

        print(f"[OK] Usuario desbloqueado exitosamente: {email}")
        return True

    def is_user_blocked(self, email: str) -> bool:
        """
        Verificar si un usuario esta bloqueado.

        Args:
            email: Email del usuario

        Returns:
            bool: True si esta bloqueado, False si esta activo o no existe
        """
        user_info = self.get_user_info(email)
        return user_info.get("status", "active") == "blocked"


    def update_user_settings(self, email: str, **settings) -> bool:
        email = email.lower()
        if email in self.users["users"]:
            for key, value in settings.items():
                if isinstance(value, str):
                    self.users["users"][email][key] = value.strip()
                else:
                    self.users["users"][email][key] = value
            self._save_users()
            return True
        return False

    def update_user_logo(self, email: str, logo_data: str, is_base64: bool = True) -> bool:
        """
        Actualiza el logo del usuario.
        Args:
            email: Email del usuario
            logo_data: Datos del logo (base64 string o path)
            is_base64: True si es base64, False si es path
        """
        key = "logo_base64" if is_base64 else "logo_path"
        return self.update_user_settings(email, **{key: logo_data})

    def change_password(self, email: str, current_password: str, new_password: str) -> dict:
        """
        Cambia la contraseña del usuario verificando la actual.
        
        Args:
            email: Email del usuario
            current_password: Contraseña actual para verificación
            new_password: Nueva contraseña a establecer
        
        Returns:
            dict: {
                "success": bool,
                "message": str,
                "error_code": str (opcional: "INVALID_CURRENT", "SAME_PASSWORD", "TOO_SHORT")
            }
        """
        try:
            email = email.lower().strip()
            
            # 1. Verificar que el usuario existe
            if email not in self.users["users"]:
                return {
                    "success": False,
                    "message": "Usuario no encontrado",
                    "error_code": "USER_NOT_FOUND"
                }
            
            user_data = self.users["users"][email]
            stored_hash = user_data.get("password_hash", "")
            
            # 2. Verificar contraseña actual
            if not bcrypt.checkpw(current_password.encode('utf-8'), stored_hash.encode('utf-8')):
                return {
                    "success": False,
                    "message": "La contraseña actual es incorrecta",
                    "error_code": "INVALID_CURRENT"
                }
            
            # 3. Validar longitud mínima
            if len(new_password) < 6:
                return {
                    "success": False,
                    "message": "La contraseña debe tener al menos 6 caracteres",
                    "error_code": "TOO_SHORT"
                }
            
            # 4. Verificar que la nueva sea diferente a la actual
            if bcrypt.checkpw(new_password.encode('utf-8'), stored_hash.encode('utf-8')):
                return {
                    "success": False,
                    "message": "La nueva contraseña debe ser diferente a la actual",
                    "error_code": "SAME_PASSWORD"
                }
            
            # 5. Generar nuevo hash
            new_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # 6. Actualizar en base de datos
            self.users["users"][email]["password_hash"] = new_hash
            self._save_users()
            
            print(f"[OK] Contraseña actualizada para: {email}")
            
            return {
                "success": True,
                "message": "Contraseña actualizada correctamente"
            }
            
        except Exception as e:
            print(f"[ERROR] change_password: {str(e)}")
            return {
                "success": False,
                "message": "Error al cambiar la contraseña. Por favor intenta de nuevo.",
                "error_code": "SYSTEM_ERROR"
            }

    def admin_reset_password(self, admin_email: str, target_email: str, new_password: str) -> dict:
        """
        Admin resetea la contraseña de otro usuario.
        
        Args:
            admin_email: Email del administrador que realiza el reseteo
            target_email: Email del usuario cuya contraseña será reseteada
            new_password: Nueva contraseña a establecer
        
        Returns:
            dict: {"success": bool, "message": str, "error_code": str (opcional)}
        """
        try:
            admin_email = admin_email.lower().strip()
            target_email = target_email.lower().strip()
            
            # 1. Verificar que quien ejecuta es admin
            if admin_email not in self.users["users"]:
                return {
                    "success": False,
                    "message": "Administrador no encontrado",
                    "error_code": "ADMIN_NOT_FOUND"
                }
            
            if not self.users["users"][admin_email].get("is_admin", False):
                return {
                    "success": False,
                    "message": "No tienes permisos de administrador",
                    "error_code": "NOT_ADMIN"
                }
            
            # 2. Verificar que el usuario objetivo existe
            if target_email not in self.users["users"]:
                return {
                    "success": False,
                    "message": f"Usuario {target_email} no encontrado",
                    "error_code": "TARGET_NOT_FOUND"
                }
            
            # 3. Validar longitud mínima
            if len(new_password) < 6:
                return {
                    "success": False,
                    "message": "La contraseña debe tener al menos 6 caracteres",
                    "error_code": "TOO_SHORT"
                }
            
            # 4. Generar nuevo hash
            new_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # 5. Actualizar en base de datos
            self.users["users"][target_email]["password_hash"] = new_hash
            self._save_users()
            
            print(f"[ADMIN] {admin_email} reseteó password de {target_email}")
            
            return {
                "success": True,
                "message": f"Contraseña de {target_email} reseteada correctamente"
            }
            
        except Exception as e:
            print(f"[ERROR] admin_reset_password: {str(e)}")
            return {
                "success": False,
                "message": "Error al resetear la contraseña. Por favor intenta de nuevo.",
                "error_code": "SYSTEM_ERROR"
            }

def check_authentication():
    """Verificar autenticación y mostrar login con contraseña"""
    auth = AuthManager()
    
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.user_email = None
        st.session_state.user_info = None
    
    if not st.session_state.authenticated:
        st.markdown('''
        <style>
        /* General body styling */
        body {
            background-color: #013366; /* Dark Blue background */
        }
        .stApp {
            background-color: #013366; /* Dark Blue background for Streamlit app */
        }
        .login-container {
            max-width: 450px;
            margin: 2rem auto; /* Centered with some top/bottom margin */
            padding: 2.5rem;
            background-color: #013366; /* Dark blue background to blend with body */
            border-radius: 12px;
            box-shadow: none; /* Remove shadow as it's blending */
        }
        .login-header {
            text-align: center;
            margin-bottom: 2rem;
            color: #013366; /* Dark blue for header text */
        }
        .login-header h1 {
            font-size: 2.5rem;
            color: white; /* Changed to white */
            margin-bottom: 0.5rem;
        }
        .login-header p {
            color: white; /* Changed to white */
            font-size: 1.1rem;
        }
        .login-header .company-branding {
            color: #fe933a; /* Orange for company branding */
            font-size: 0.9rem;
            font-weight: bold;
            margin-top: 0.5rem;
        }
        .login-footer {
            text-align: center;
            margin-top: 2rem;
            padding-top: 1rem;
            border-top: 1px solid #ecf0f1;
            color: #95a5a6;
            font-size: 0.9rem;
        }
        .login-footer a {
            color: #01bfff; /* Light blue for links */
            text-decoration: none;
        }
        .login-footer a:hover {
            text-decoration: underline;
        }
        /* Streamlit button styling */
        .stButton > button {
            background-color: #fe933a; /* Orange for buttons */
            color: white;
            border-radius: 8px;
            padding: 0.75rem 1.5rem;
            font-weight: bold;
            border: none;
            transition: background-color 0.3s ease;
        }
        .stButton > button:hover {
            background-color: #ff6f00; /* Brighter orange on hover */
            color: white;
        }
        /* Input field styling */
        .stTextInput > div > div > input {
            border-radius: 8px;
            border: 1px solid #cccccc;
            padding: 0.75rem 1rem;
        }
        .stTextInput > label {
            color: white; /* Changed to white */
            font-weight: bold;
        }
        </style>
        ''', unsafe_allow_html=True)
        
        st.markdown('''
        <div class="login-header">
            <h1>CatalogPro</h1>
            <p>Acceso Empresarial</p>
            <p class="company-branding">by Antay Perú</p>
        </div>
        ''', unsafe_allow_html=True)

        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        with st.form("login_form"):
            email = st.text_input(
                "Email Corporativo",
                placeholder="usuario@empresa.com",
                key="login_email"
            )
            
            password = st.text_input(
                "Contraseña",
                placeholder="••••••••",
                type="password",
                key="login_password"
            )
            
            st.write("") # Vertical spacing

            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                submitted = st.form_submit_button("Acceder al Sistema", use_container_width=True)

            if submitted:
                with st.spinner("Verificando credenciales..."):
                    if email and password:
                        email = email.strip()
                        if auth.is_authorized(email) and auth.verify_password(email, password):
                            # Validar que el usuario NO este bloqueado
                            if auth.is_user_blocked(email):
                                # Limpiar cualquier sesión existente
                                st.session_state.authenticated = False
                                st.session_state.user_email = None
                                st.session_state.user_info = None

                                st.error("🔒 Tu cuenta ha sido bloqueada. Por favor, contacta al administrador.")
                                print(f"[LOGIN BLOCKED] Intento de login de usuario bloqueado: {email}")
                                st.stop()  # Detener completamente la ejecución de Streamlit

                            # Login exitoso
                            st.session_state.authenticated = True
                            st.session_state.user_email = email
                            st.session_state.user_info = auth.get_user_info(email)
                            auth.update_last_login(email)
                            st.success("¡Bienvenido!")
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error("El email o la contraseña no son correctos. Por favor, verifica e intenta de nuevo.")
                    else:
                        st.warning("Por favor ingresa tu email y contraseña")
        
        st.markdown('''
        <div class="login-footer">
            ⚠️ Solo emails autorizados<br>
            <a href="mailto:cortega@antayperu.com?subject=Solicitud de reseteo de contraseña" target="_blank">¿Olvidaste tu contraseña?</a><br>
            📞 ¿Sin acceso? Contactar: cortega@antayperu.com
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.stop()
    
    with st.sidebar:
        user_info = st.session_state.user_info
        
        # Header profesional
        st.markdown(f"""
        <div style="padding: 1rem; background-color: #f0f2f6; border-radius: 8px; margin-bottom: 1rem;">
            <div style="font-size: 0.8rem; color: #555;">Bienvenido,</div>
            <div style="font-weight: bold; font-size: 1.1rem; color: #013366;">{user_info.get('name', 'Usuario')}</div>
            <div style="font-size: 0.9rem; color: #fe933a;">{user_info.get('business_name', 'N/A')}</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button(" Cerrar Sesión", use_container_width=True, type="secondary"):
            st.session_state.authenticated = False
            st.session_state.user_email = None
            st.session_state.user_info = None
            st.rerun()
    
    return auth