import sys
from unittest.mock import MagicMock
from datetime import datetime, timedelta

# Mock streamlit before importing auth
mock_st = MagicMock()
mock_st.secrets = {"supabase": {"SUPABASE_URL": "http://test", "SUPABASE_KEY": "test"}} 
sys.modules["streamlit"] = mock_st
sys.modules["supabase"] = MagicMock()

from auth import AuthManager

class TestAuthManager(AuthManager):
    def __init__(self):
        self.users = {"users": {}}
        self.admin_email = "admin@test.com"
        self.backend = MagicMock()
        
    def _save_users(self):
        pass

def test_license_priority_date():
    manager = TestAuthManager()
    email = "free_user@test.com"
    
    # CASE 1: Free user, zero credits, but VALID future date
    future_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    manager.users["users"][email] = {
        "plan_type": "Free",
        "quota": 0,
        "expires_at": future_date
    }
    
    # Should have access because date is valid
    assert manager.check_quota(email) is True
    
    # CASE 2: Free user, many credits, but EXPIRED date
    past_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    manager.users["users"][email]["expires_at"] = past_date
    manager.users["users"][email]["quota"] = 100
    
    # Should NOT have access because date is expired
    assert manager.check_quota(email) is False
    
    # CASE 3: Free user, zero credits, NO date
    manager.users["users"][email]["expires_at"] = None
    manager.users["users"][email]["quota"] = 0
    
    # Should NOT have access
    assert manager.check_quota(email) is False

    # CASE 4: Free user, 5 credits, NO date
    manager.users["users"][email]["quota"] = 5
    
    # Should have access
    assert manager.check_quota(email) is True
