import streamlit as st
import json
import os
from datetime import datetime
import re
import time
import bcrypt

def is_valid_email(email: str) -> bool:
    """Validar formato de email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

class AuthManager:
    """Gestor de autenticación y usuarios"""
    
    def __init__(self):
        self.auth_file = "authorized_users.json"
        self.admin_email = "admin@antayperu.com"
        self._ensure_auth_file_exists()
        self._load_users()
    
    def _ensure_auth_file_exists(self):
        """Crear archivo JSON si no existe con un admin y contraseña por defecto"""
        if not os.path.exists(self.auth_file):
            # Contraseña por defecto para el admin es 'admin'
            default_password = "admin"
            hashed_password = bcrypt.hashpw(default_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            initial_data = {
                "users": {
                    self.admin_email: {
                        "name": "Administrador",
                        "business_name": "CatalogPro",
                        "is_admin": True,
                        "password_hash": hashed_password,
                        "created_at": datetime.now().isoformat(),
                        "last_login": None
                    }
                }
            }
            with open(self.auth_file, 'w') as f:
                json.dump(initial_data, f, indent=2)
    
    def _load_users(self):
        """Cargar usuarios desde JSON"""
        try:
            with open(self.auth_file, 'r') as f:
                self.users = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self._ensure_auth_file_exists()
            with open(self.auth_file, 'r') as f:
                self.users = json.load(f)
    
    def _save_users(self):
        """Guardar usuarios a JSON"""
        with open(self.auth_file, 'w') as f:
            json.dump(self.users, f, indent=2)
    
    def is_authorized(self, email: str) -> bool:
        """Verificar si email está autorizado"""
        return email.lower() in [e.lower() for e in self.users["users"].keys()]
    
    def add_user(self, email: str, name: str, business: str, password: str) -> bool:
        """Agregar usuario nuevo con contraseña hasheada"""
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
            "last_login": None
        }
        
        self._save_users()
        return True

    def remove_user(self, email: str) -> bool:
        """Eliminar usuario (excepto admin)"""
        email = email.lower()
        
        if email == self.admin_email.lower():
            return False
        
        if email in self.users["users"]:
            del self.users["users"][email]
            self._save_users()
            return True
        
        return False

    def update_password(self, email: str, new_password: str) -> bool:
        """Actualizar la contraseña de un usuario."""
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
        """Verificar la contraseña de un email."""
        user_info = self.get_user_info(email)
        if user_info and "password_hash" in user_info:
            stored_hash = user_info["password_hash"].encode('utf-8')
            return bcrypt.checkpw(password.encode('utf-8'), stored_hash)
        return False
    
    def get_user_info(self, email: str) -> dict:
        """Obtener información del usuario"""
        return self.users["users"].get(email.lower(), {})
    
    def is_admin(self, email: str) -> bool:
        """Verificar si es administrador"""
        user_info = self.get_user_info(email)
        return user_info.get("is_admin", False)
    
    def get_all_users(self) -> list:
        """Obtener todos los usuarios"""
        return [{"email": email, "info": info} for email, info in self.users["users"].items()]
    
    def update_last_login(self, email: str):
        """Actualizar último login"""
        email = email.lower()
        if email in self.users["users"]:
            self.users["users"][email]["last_login"] = datetime.now().isoformat()
            self._save_users()

    def toggle_admin_status(self, email: str) -> bool:
        """Cambiar el estado de administrador de un usuario."""
        email = email.lower()
        if email == self.admin_email.lower():
            return False # No se puede cambiar el estado del admin principal
        
        if email in self.users["users"]:
            current_status = self.users["users"][email].get("is_admin", False)
            self.users["users"][email]["is_admin"] = not current_status
            self._save_users()
            return True
        
        return False

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
        .login-container {
            max-width: 450px;
            margin: 0 auto; /* This keeps the form centered and constrained */
        }
        .login-header {
            text-align: center;
            margin-bottom: 2rem; /* This will now create space between title and card */
        }
        .login-header h1 {
            font-size: 2.2rem;
            color: #2c3e50;
            margin-bottom: 0.5rem;
        }
        .login-header p {
            color: #7f8c8d;
            font-size: 1.1rem;
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
            color: #3498db;
            text-decoration: none;
        }
        .login-footer a:hover {
            text-decoration: underline;
        }
        </style>
        ''', unsafe_allow_html=True)
        
        st.markdown('''
        <div class="login-header">
            <h1>CatalogPro Enhanced</h1>
            <p>Acceso Empresarial</p>
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
        st.success("Sesión activa")
        user_info = st.session_state.user_info
        st.write(f"👤 **{user_info.get('name', 'Usuario')}**")
        st.write(f"🏢 {user_info.get('business_name', 'N/A')}")
        
        if st.button("Cerrar Sesión", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user_email = None
            st.session_state.user_info = None
            st.rerun()
    
    return auth