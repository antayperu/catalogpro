"""
Suite de Pruebas QA - CatalogPro v1.3.1
Siguiendo Metodología Antay Fábrica de Software

Tipos de pruebas:
- Unit Tests: Funciones individuales
- Integration Tests: Flujos completos
- Functional Tests: Requerimientos del FRD
"""

import pytest
import pandas as pd
import os
import sys
from io import BytesIO
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import DataHandler, DataCleaner, ImageManager
from auth import AuthManager, is_valid_email

# =============================================================================
# FIXTURES - Datos de prueba reutilizables
# =============================================================================

@pytest.fixture
def sample_excel_path():
    """Path al archivo Excel de prueba"""
    return "ProductSample_Enterprise.xlsx"

@pytest.fixture
def sample_data():
    """DataFrame de prueba con datos válidos"""
    return pd.DataFrame({
        'Codigo': ['P001', 'P002', 'P003'],
        'Producto': ['Producto A', 'Producto B', 'Producto C'],
        'Precio': [10.50, 20.00, 15.75],
        'Stock': [100, 50, 75],
        'ImagenURL': [
            'https://example.com/img1.jpg',
            'https://example.com/img2.jpg',
            ''
        ],
        'Descripcion': ['Desc A', 'Desc B', 'Desc C']
    })

@pytest.fixture
def auth_manager():
    """AuthManager instance para pruebas"""
    return AuthManager()

# =============================================================================
# UNIT TESTS - DataHandler
# =============================================================================

class TestDataHandler:
    """Pruebas unitarias para la clase DataHandler"""
    
    def test_init(self):
        """Test: Inicialización correcta de DataHandler"""
        handler = DataHandler()
        assert handler is not None
        assert hasattr(handler, 'load_excel')
        assert hasattr(handler, 'load_google_sheets')
    
    def test_load_excel_valid_file(self, sample_excel_path):
        """Test: Cargar archivo Excel válido"""
        if not os.path.exists(sample_excel_path):
            pytest.skip(f"Archivo de prueba {sample_excel_path} no encontrado")
        
        handler = DataHandler()
        with open(sample_excel_path, 'rb') as f:
            df = handler.load_excel(f)
        
        assert df is not None
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        assert 'Producto' in df.columns or 'producto' in df.columns.str.lower()
    
    def test_validate_columns_valid(self, sample_data):
        """Test: Validación de columnas requeridas - caso válido"""
        handler = DataHandler()
        # Should not raise exception
        try:
            handler._validate_columns(sample_data)
            assert True
        except Exception as e:
            pytest.fail(f"Validación falló con datos válidos: {e}")
    
    def test_validate_columns_missing(self):
        """Test: Validación de columnas requeridas - caso inválido"""
        handler = DataHandler()
        invalid_df = pd.DataFrame({
            'Codigo': ['P001'],
            'Precio': [10.50]
            # Falta columna 'Producto' requerida
        })
        
        with pytest.raises(ValueError):
            handler._validate_columns(invalid_df)
    
    def test_convert_sheets_url_to_csv(self):
        """Test: Conversión de URL de Google Sheets a formato CSV"""
        handler = DataHandler()
        
        # URL de ejemplo de Google Sheets
        sheets_url = "https://docs.google.com/spreadsheets/d/1ABC123/edit#gid=0"
        csv_url = handler._convert_sheets_url_to_csv(sheets_url)
        
        assert csv_url is not None
        assert 'export?format=csv' in csv_url
        assert '1ABC123' in csv_url

# =============================================================================
# UNIT TESTS - DataCleaner
# =============================================================================

class TestDataCleaner:
    """Pruebas unitarias para la clase DataCleaner"""
    
    def test_init(self):
        """Test: Inicialización correcta de DataCleaner"""
        cleaner = DataCleaner()
        assert cleaner is not None
    
    def test_clean_data_basic(self, sample_data):
        """Test: Limpieza básica de datos"""
        cleaner = DataCleaner()
        cleaned_df = cleaner.clean_data(sample_data.copy())
        
        assert cleaned_df is not None
        assert isinstance(cleaned_df, pd.DataFrame)
        assert len(cleaned_df) > 0
    
    def test_clean_prices_valid(self):
        """Test: Limpieza de precios - valores válidos"""
        cleaner = DataCleaner()
        df = pd.DataFrame({
            'Codigo': ['P001'],
            'Producto': ['Test'],
            'Precio': ['S/ 10.50'],
            'Stock': [100]
        })
        
        cleaned_df = cleaner._clean_prices_and_stock(df.copy())
        
        # Verificar que el precio se convirtió a numérico
        assert pd.api.types.is_numeric_dtype(cleaned_df['Precio'])
        assert cleaned_df['Precio'].iloc[0] == 10.50
    
    def test_clean_prices_invalid(self):
        """Test: Limpieza de precios - valores inválidos se convierten a 0"""
        cleaner = DataCleaner()
        df = pd.DataFrame({
            'Codigo': ['P001'],
            'Producto': ['Test'],
            'Precio': ['INVALID'],
            'Stock': [100]
        })
        
        cleaned_df = cleaner._clean_prices_and_stock(df.copy())
        
        # Precio inválido debe convertirse a 0
        assert cleaned_df['Precio'].iloc[0] == 0.0
    
    def test_clean_text_fields(self):
        """Test: Limpieza de campos de texto"""
        cleaner = DataCleaner()
        df = pd.DataFrame({
            'Codigo': ['P001'],
            'Producto': ['  Test Product  '],
            'Descripcion': ['  Description with spaces  ']
        })
        
        cleaned_df = cleaner._clean_text_fields(df.copy())
        
        # Verificar que se eliminaron espacios
        assert cleaned_df['Producto'].iloc[0] == 'Test Product'
        assert cleaned_df['Descripcion'].iloc[0] == 'Description with spaces'
    
    def test_remove_invalid_rows(self):
        """Test: Eliminación de filas con datos críticos faltantes"""
        cleaner = DataCleaner()
        df = pd.DataFrame({
            'Codigo': ['P001', 'P002', None],
            'Producto': ['Product A', None, 'Product C'],
            'Precio': [10.0, 20.0, 30.0]
        })
        
        cleaned_df = cleaner._remove_invalid_rows(df.copy())
        
        # Solo debe quedar la primera fila (P001)
        assert len(cleaned_df) == 1
        assert cleaned_df['Codigo'].iloc[0] == 'P001'

# =============================================================================
# UNIT TESTS - AuthManager
# =============================================================================

class TestAuthManager:
    """Pruebas unitarias para el sistema de autenticación"""
    
    def test_init(self, auth_manager):
        """Test: Inicialización correcta de AuthManager"""
        assert auth_manager is not None
        assert os.path.exists(auth_manager.auth_file)
    
    def test_is_valid_email_valid(self):
        """Test: Validación de email - casos válidos"""
        assert is_valid_email("test@example.com") == True
        assert is_valid_email("user.name@domain.co") == True
        assert is_valid_email("admin@antayperu.com") == True
    
    def test_is_valid_email_invalid(self):
        """Test: Validación de email - casos inválidos"""
        assert is_valid_email("invalid") == False
        assert is_valid_email("@example.com") == False
        assert is_valid_email("test@") == False
        assert is_valid_email("") == False
    
    def test_add_user_valid(self, auth_manager):
        """Test: Agregar usuario válido"""
        test_email = "test_qa@example.com"
        
        # Limpiar usuario de prueba si existe
        if test_email in auth_manager.users:
            del auth_manager.users[test_email]
            auth_manager._save_users()
        
        result = auth_manager.add_user(
            email=test_email,
            name="Test User",
            business="Test Business",
            password="test123"
        )
        
        assert result == True
        assert test_email in auth_manager.users
        
        # Limpiar después de la prueba
        del auth_manager.users[test_email]
        auth_manager._save_users()
    
    def test_add_user_duplicate(self, auth_manager):
        """Test: Agregar usuario duplicado debe fallar"""
        test_email = "duplicate@example.com"
        
        # Agregar usuario primera vez
        auth_manager.add_user(test_email, "User 1", "Business 1", "pass123")
        
        # Intentar agregar de nuevo
        result = auth_manager.add_user(test_email, "User 2", "Business 2", "pass456")
        
        assert result == False
        
        # Limpiar
        if test_email in auth_manager.users:
            del auth_manager.users[test_email]
            auth_manager._save_users()
    
    def test_verify_password_correct(self, auth_manager):
        """Test: Verificación de contraseña correcta"""
        test_email = "password_test@example.com"
        test_password = "secure123"
        
        # Crear usuario de prueba
        auth_manager.add_user(test_email, "Test", "Business", test_password)
        
        # Verificar contraseña correcta
        assert auth_manager.verify_password(test_email, test_password) == True
        
        # Limpiar
        del auth_manager.users[test_email]
        auth_manager._save_users()
    
    def test_verify_password_incorrect(self, auth_manager):
        """Test: Verificación de contraseña incorrecta"""
        test_email = "password_test2@example.com"
        
        # Crear usuario de prueba
        auth_manager.add_user(test_email, "Test", "Business", "correct_pass")
        
        # Verificar contraseña incorrecta
        assert auth_manager.verify_password(test_email, "wrong_pass") == False
        
        # Limpiar
        del auth_manager.users[test_email]
        auth_manager._save_users()
    
    def test_is_authorized(self, auth_manager):
        """Test: Verificar si usuario está autorizado"""
        # Admin siempre debe estar autorizado
        assert auth_manager.is_authorized("admin@antayperu.com") == True
        
        # Usuario no existente no debe estar autorizado
        assert auth_manager.is_authorized("nonexistent@example.com") == False

# =============================================================================
# INTEGRATION TESTS - Flujos completos
# =============================================================================

class TestIntegrationFlows:
    """Pruebas de integración para flujos completos"""
    
    def test_full_data_pipeline(self, sample_excel_path):
        """Test: Pipeline completo de carga y limpieza de datos"""
        if not os.path.exists(sample_excel_path):
            pytest.skip(f"Archivo de prueba {sample_excel_path} no encontrado")
        
        # 1. Cargar datos
        handler = DataHandler()
        with open(sample_excel_path, 'rb') as f:
            df = handler.load_excel(f)
        
        assert df is not None
        assert len(df) > 0
        
        # 2. Limpiar datos
        cleaner = DataCleaner()
        cleaned_df = cleaner.clean_data(df)
        
        assert cleaned_df is not None
        assert len(cleaned_df) > 0
        
        # 3. Validar que los datos están limpios
        assert cleaned_df['Precio'].dtype in ['float64', 'int64']
        assert cleaned_df['Stock'].dtype in ['float64', 'int64']
    
    def test_auth_flow(self, auth_manager):
        """Test: Flujo completo de autenticación"""
        test_email = "flow_test@example.com"
        test_password = "flow123"
        
        # 1. Crear usuario
        result = auth_manager.add_user(test_email, "Flow Test", "Business", test_password)
        assert result == True
        
        # 2. Verificar que está autorizado
        assert auth_manager.is_authorized(test_email) == True
        
        # 3. Verificar contraseña
        assert auth_manager.verify_password(test_email, test_password) == True
        
        # 4. Obtener info del usuario
        user_info = auth_manager.get_user_info(test_email)
        assert user_info is not None
        assert user_info['name'] == "Flow Test"
        
        # Limpiar
        del auth_manager.users[test_email]
        auth_manager._save_users()

# =============================================================================
# FUNCTIONAL TESTS - Basados en FRD
# =============================================================================

class TestFunctionalRequirements:
    """Pruebas funcionales basadas en el FRD"""
    
    def test_FR_AUTH_01_login_required(self, auth_manager):
        """Test FR-AUTH-01: Login obligatorio"""
        # Usuario no autorizado no debe tener acceso
        assert auth_manager.is_authorized("unauthorized@example.com") == False
        
        # Usuario autorizado debe tener acceso
        assert auth_manager.is_authorized("admin@antayperu.com") == True
    
    def test_FR_DATA_01_excel_loading(self, sample_excel_path):
        """Test FR-DATA-01: Carga de datos desde Excel"""
        if not os.path.exists(sample_excel_path):
            pytest.skip(f"Archivo de prueba {sample_excel_path} no encontrado")
        
        handler = DataHandler()
        with open(sample_excel_path, 'rb') as f:
            df = handler.load_excel(f)
        
        # Debe cargar datos exitosamente
        assert df is not None
        assert len(df) > 0
        
        # Debe tener columnas requeridas
        columns_lower = [col.lower() for col in df.columns]
        assert 'producto' in columns_lower
        assert 'precio' in columns_lower

# =============================================================================
# MAIN - Ejecutar pruebas
# =============================================================================

if __name__ == "__main__":
    # Ejecutar todas las pruebas con pytest
    pytest.main([__file__, "-v", "--tb=short"])
