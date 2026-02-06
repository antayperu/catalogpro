import sys
from unittest.mock import MagicMock

# Mock streamlit before importing auth to prevent module-level execution errors
mock_st = MagicMock()
mock_st.secrets = {"supabase": {"SUPABASE_URL": "http://test", "SUPABASE_KEY": "test"}} 
sys.modules["streamlit"] = mock_st

import pytest
import bcrypt
# Now import auth
from auth import AuthManager

# Mock Supabase client to prevent actual connection attempts during import if any
sys.modules["supabase"] = MagicMock()

# Dummy AuthManager for testing to avoid actual DB calls or file loading
class TestAuthManager(AuthManager):
    def __init__(self):
        # Skip original init that loads files/DB
        self.users = {"users": {}}
        self.admin_email = "admin@test.com"
        # Mock backend
        self.backend = MagicMock()
        
    def _save_users(self):
        # Mock save
        pass

@pytest.fixture
def auth_manager():
    manager = TestAuthManager()
    
    # Setup initial users
    # User 1: Regular user
    pass_hash = bcrypt.hashpw("oldpassword".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    manager.users["users"]["user@test.com"] = {
        "password_hash": pass_hash,
        "is_admin": False
    }
    
    # User 2: Admin user
    admin_pass = bcrypt.hashpw("adminpass".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    manager.users["users"]["admin@test.com"] = {
        "password_hash": admin_pass,
        "is_admin": True
    }
    
    return manager

# --- Tests for change_password (User Self-Service) ---

def test_change_password_success(auth_manager):
    result = auth_manager.change_password("user@test.com", "oldpassword", "newsecurepass")
    assert result["success"] is True
    
    # Verify hash changed
    new_hash = auth_manager.users["users"]["user@test.com"]["password_hash"]
    assert bcrypt.checkpw("newsecurepass".encode('utf-8'), new_hash.encode('utf-8'))

def test_change_password_invalid_current(auth_manager):
    result = auth_manager.change_password("user@test.com", "wrongpassword", "newsecurepass")
    assert result["success"] is False
    assert result["error_code"] == "INVALID_CURRENT"

def test_change_password_same_password(auth_manager):
    result = auth_manager.change_password("user@test.com", "oldpassword", "oldpassword")
    assert result["success"] is False
    assert result["error_code"] == "SAME_PASSWORD"

def test_change_password_too_short(auth_manager):
    result = auth_manager.change_password("user@test.com", "oldpassword", "123")
    assert result["success"] is False
    assert result["error_code"] == "TOO_SHORT"

def test_change_password_user_not_found(auth_manager):
    result = auth_manager.change_password("ghost@test.com", "any", "new")
    assert result["success"] is False
    assert result["error_code"] == "USER_NOT_FOUND"

# --- Tests for admin_reset_password (Admin Function) ---

def test_admin_reset_success(auth_manager):
    result = auth_manager.admin_reset_password("admin@test.com", "user@test.com", "reset123")
    assert result["success"] is True
    
    # Verify hash changed
    new_hash = auth_manager.users["users"]["user@test.com"]["password_hash"]
    assert bcrypt.checkpw("reset123".encode('utf-8'), new_hash.encode('utf-8'))

def test_admin_reset_not_admin(auth_manager):
    # Regular user tries to reset admin
    result = auth_manager.admin_reset_password("user@test.com", "admin@test.com", "hacked")
    assert result["success"] is False
    assert result["error_code"] == "NOT_ADMIN"

def test_admin_reset_target_not_found(auth_manager):
    result = auth_manager.admin_reset_password("admin@test.com", "ghost@test.com", "reset123")
    assert result["success"] is False
    assert result["error_code"] == "TARGET_NOT_FOUND"
