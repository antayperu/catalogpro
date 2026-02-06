import sys
from unittest.mock import MagicMock

# Mock dependencies BEFORE importing auth
mock_st = MagicMock()
mock_st.secrets = {"supabase": {"SUPABASE_URL": "http://test", "SUPABASE_KEY": "test"}} 
sys.modules["streamlit"] = mock_st
sys.modules["supabase"] = MagicMock()
sys.modules["gspread"] = MagicMock()
sys.modules["google.oauth2.service_account"] = MagicMock()

import bcrypt
from auth import AuthManager

# Dummy AuthManager for testing
class TestAuthManager(AuthManager):
    def __init__(self):
        self.users = {"users": {}}
        self.admin_email = "admin@test.com"
        self.backend = MagicMock()
        
    def _save_users(self):
        pass

def run_tests():
    print("Running tests...")
    
    # Setup
    manager = TestAuthManager()
    
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
    
    # Test 1: Change Password Success
    print("Test 1: change_password success...", end="")
    result = manager.change_password("user@test.com", "oldpassword", "newsecurepass")
    if result["success"] and bcrypt.checkpw("newsecurepass".encode('utf-8'), manager.users["users"]["user@test.com"]["password_hash"].encode('utf-8')):
        print("PASS")
    else:
        print(f"FAIL: {result}")

    # Test 2: Invalid Current
    print("Test 2: invalid current password...", end="")
    result = manager.change_password("user@test.com", "wrong", "new")
    if not result["success"] and result["error_code"] == "INVALID_CURRENT":
        print("PASS")
    else:
        print(f"FAIL: {result}")

    # Reset user password to known state for Test 3
    pass_hash = bcrypt.hashpw("oldpassword".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    manager.users["users"]["user@test.com"]["password_hash"] = pass_hash

    # Test 3: Same Password
    print("Test 3: same password...", end="")
    result = manager.change_password("user@test.com", "oldpassword", "oldpassword")
    if not result["success"] and result["error_code"] == "SAME_PASSWORD":
        print("PASS")
    else:
        print(f"FAIL: {result}")
        
    # Test 4: Too Short
    print("Test 4: too short...", end="")
    result = manager.change_password("user@test.com", "oldpassword", "123")
    if not result["success"] and result["error_code"] == "TOO_SHORT":
        print("PASS")
    else:
        print(f"FAIL: {result}")

    # Test 5: Admin Reset Success
    print("Test 5: admin_reset success...", end="")
    result = manager.admin_reset_password("admin@test.com", "user@test.com", "reset123")
    if result["success"] and bcrypt.checkpw("reset123".encode('utf-8'), manager.users["users"]["user@test.com"]["password_hash"].encode('utf-8')):
        print("PASS")
    else:
        print(f"FAIL: {result}")

    # Test 6: Non-Admin Reset
    print("Test 6: non-admin reset...", end="")
    result = manager.admin_reset_password("user@test.com", "admin@test.com", "hack")
    if not result["success"] and result["error_code"] == "NOT_ADMIN":
        print("PASS")
    else:
        print(f"FAIL: {result}")

if __name__ == "__main__":
    run_tests()
