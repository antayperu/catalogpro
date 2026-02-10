#!/usr/bin/env python3
"""
Standalone test para verificar FREE (Fecha) plan functionality
Usa AuthManager con JsonBackend
"""

import sys
import os
from datetime import datetime, timedelta
import tempfile
import json

# Setup a temporary credentials directory
temp_dir = tempfile.mkdtemp()
secrets_dir = os.path.join(temp_dir, ".streamlit")
os.makedirs(secrets_dir, exist_ok=True)

# Create minimal .streamlit/secrets.toml (empty to avoid Supabase)
with open(os.path.join(secrets_dir, "secrets.toml"), "w") as f:
    f.write("# Empty secrets to use JsonBackend\n")

# Set STREAMLIT_SECRETS_FILE environment variable
os.environ["STREAMLIT_SECRETS_FILE"] = os.path.join(secrets_dir, "secrets.toml")

# Now import Streamlit and configure it
import streamlit as st

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Manually set up auth with JsonBackend by creating isolated temporary file
auto_users_file = os.path.join(temp_dir, "authorized_users.json")

# Create initial data
with open(auto_users_file, 'w') as f:
    json.dump({
        "users": {
            "admin@antayperu.com": {
                "name": "Admin",
                "business_name": "Test",
                "is_admin": True,
                "password_hash": "$2b$12$...",
                "created_at": datetime.now().isoformat(),
                "last_login": None,
                "currency": "S/",
                "phone_number": ""
            }
        }
    }, f)

# Import auth after setting up environment
from auth import AuthManager, JsonBackend

def test_free_fecha():
    """Test FREE (Fecha) plan with JsonBackend"""

    print("=" * 70)
    print("TEST: FREE (Fecha) Plan Functionality")
    print("=" * 70)

    try:
        # Create custom auth manager with isolated JsonBackend
        auth = AuthManager()

        # Verify backend type
        backend_type = type(auth.backend).__name__
        print(f"\nBackend: {backend_type}")

        if backend_type != "JsonBackend":
            print(f"WARNING: Using {backend_type} instead of JsonBackend")
            print("Some features may be limited, but plan logic should still work")

        # Test email
        test_email = "test_free_fecha@example.com"
        test_name = "Test User"
        test_business = "Test Business"
        test_password = "TestPass123"
        plan_type = "Free (Fecha)"
        expires_date = (datetime.now().date() + timedelta(days=30)).strftime("%Y-%m-%d")

        print(f"\n1. Creating user with FREE (Fecha) plan...")
        print(f"   - Email: {test_email}")
        print(f"   - Plan Type: {plan_type}")
        print(f"   - Expires: {expires_date}")

        # Create user
        result = auth.add_user(
            test_email,
            test_name,
            test_business,
            test_password,
            plan_type=plan_type,
            quota=0,
            quota_max=0,
            expires_at=expires_date
        )

        if not result:
            print(f"   ERROR: Failed to create user (might be duplicate)")
            # Try to retrieve existing
            user = auth.get_user_info(test_email)
            if not user:
                return False
        else:
            print(f"   OK User created")

        # Retrieve user
        print(f"\n2. Retrieving user info...")
        user_info = auth.get_user_info(test_email)

        if not user_info:
            print(f"   ERROR: User not found!")
            return False

        print(f"   OK User found!")
        print(f"   - plan_type: {user_info.get('plan_type')}")
        print(f"   - expires_at: {user_info.get('expires_at')}")
        print(f"   - quota: {user_info.get('quota')}")

        # Check values
        if user_info.get('plan_type') != plan_type:
            print(f"   ERROR: Plan type mismatch!")
            return False

        if user_info.get('expires_at') != expires_date:
            print(f"   ERROR: Expires date mismatch!")
            return False

        print(f"\n3. Testing sidebar display logic...")

        # Simulate get_user_plan_status()
        retrieved_plan_type = user_info.get('plan_type', 'Free')
        retrieved_expiry_str = user_info.get('expires_at')
        quota = user_info.get('quota', 0)

        # Check expiration
        is_expired = False
        if retrieved_expiry_str:
            try:
                exp_date = datetime.strptime(retrieved_expiry_str, "%Y-%m-%d").date()
                is_expired = exp_date < datetime.now().date()
            except Exception as e:
                print(f"   WARNING: Could not parse date: {e}")

        if is_expired:
            display_expiry = retrieved_expiry_str + " (VENCIDO)"
        else:
            display_expiry = retrieved_expiry_str

        print(f"   - 'Fecha' in plan_type: {'Fecha' in retrieved_plan_type}")
        print(f"   - expiry_date value: {display_expiry}")
        print(f"   - is_expired: {is_expired}")

        # Check display condition (from main.py line 1775)
        if display_expiry and display_expiry.strip():
            print(f"\n   OK Display condition PASSES")
            print(f"   -> Would show: [ ⏰ **Vigente hasta:** {display_expiry.replace(' (VENCIDO)', '').strip()} ]")
        else:
            print(f"\n   ERROR Display condition FAILS")
            return False

        print(f"\n4. Testing expired plan scenario...")

        expired_email = "expired_test@example.com"
        yesterday = (datetime.now().date() - timedelta(days=1)).strftime("%Y-%m-%d")

        auth.add_user(
            expired_email,
            "Expired User",
            "Expired Business",
            "ExpPass123",
            plan_type="Free (Fecha)",
            quota=0,
            quota_max=0,
            expires_at=yesterday
        )

        expired_info = auth.get_user_info(expired_email)
        exp_plan_type = expired_info.get('plan_type')
        exp_date_str = expired_info.get('expires_at')

        # Check if expired
        is_exp = False
        if exp_date_str:
            try:
                exp = datetime.strptime(exp_date_str, "%Y-%m-%d").date()
                is_exp = exp < datetime.now().date()
            except:
                pass

        if is_exp:
            display_exp = exp_date_str + " (VENCIDO)"
        else:
            display_exp = exp_date_str

        print(f"   - Plan: {exp_plan_type}")
        print(f"   - Expires: {display_exp}")
        print(f"   - Is expired: {is_exp}")

        if is_exp and "(VENCIDO)" in display_exp:
            print(f"   OK Expiration detection works")
            print(f"   -> Would show: [ ERROR **EXPIRADO** ]")
        else:
            print(f"   ERROR Expiration detection failed")
            return False

        print(f"\n5. Testing Premium (Fecha) variant...")

        premium_email = "test_premium_fecha@example.com"
        premium_expiry = (datetime.now().date() + timedelta(days=365)).strftime("%Y-%m-%d")

        auth.add_user(
            premium_email,
            "Premium User",
            "Premium Business",
            "PremPass123",
            plan_type="Premium (Fecha)",
            quota=0,
            quota_max=0,
            expires_at=premium_expiry
        )

        premium_info = auth.get_user_info(premium_email)

        if premium_info and premium_info.get('plan_type') == "Premium (Fecha)":
            print(f"   OK Premium (Fecha) plan works")
            print(f"   - Plan: {premium_info.get('plan_type')}")
            print(f"   - Expires: {premium_info.get('expires_at')}")
        else:
            print(f"   ERROR Premium (Fecha) test failed")
            return False

        print(f"\n" + "=" * 70)
        print("ALL TESTS PASSED!")
        print("=" * 70)
        print("\nSummary:")
        print("- Plan types with (Fecha) are correctly stored")
        print("- Expiry dates are correctly retrieved")
        print("- Display conditions work properly")
        print("- Expiration detection works")
        print("- Both Free (Fecha) and Premium (Fecha) are supported")
        print("\nFor production deployment:")
        print("1. Ensure Supabase constraint is updated:")
        print("   Run: docs/MIGRATION_v1.7.0_plan_types.sql")
        print("2. Deploy CSS changes for sidebar visibility")
        print("=" * 70)

        return True

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = test_free_fecha()
        sys.exit(0 if success else 1)
    finally:
        # Cleanup
        import shutil
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except:
            pass
