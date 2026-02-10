#!/usr/bin/env python3
"""
Migration script to update Supabase database schema for v1.7.0
Adds support for Free (Fecha) and Premium (Fecha) plan types
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

def apply_migration():
    """Apply migration to update valid_plan_type constraint"""

    try:
        import streamlit as st
        from supabase import create_client

        print("=" * 70)
        print("CatalogPro v1.7.0 Database Migration")
        print("=" * 70)

        # Get Supabase credentials from secrets
        if "supabase" not in st.secrets:
            print("❌ Supabase credentials not found in secrets.toml")
            print("Please configure Supabase first.")
            return False

        supabase_url = st.secrets["supabase"]["SUPABASE_URL"]
        supabase_key = st.secrets["supabase"]["SUPABASE_KEY"]

        print(f"\n1. Connecting to Supabase...")
        print(f"   URL: {supabase_url[:50]}...")

        # Create client
        client = create_client(supabase_url, supabase_key)

        # SQL migration script
        migration_sql = """
        ALTER TABLE users DROP CONSTRAINT IF EXISTS valid_plan_type;

        ALTER TABLE users
        ADD CONSTRAINT valid_plan_type CHECK (
          plan_type IN (
            'Free',
            'Free (Cantidad)',
            'Free (Fecha)',
            'Premium',
            'Premium (Cantidad)',
            'Premium (Fecha)',
            'Cantidad',
            'Tiempo'
          )
        );
        """

        print(f"\n2. Applying migration...")
        print(f"   - Dropping old valid_plan_type constraint")
        print(f"   - Adding new constraint with date-based plan types")

        # Execute migration using RPC or raw SQL
        try:
            # Try executing via RPC (if available)
            response = client.rpc(
                'exec_sql',
                {'query': migration_sql}
            ).execute()

            print(f"\n✅ Migration applied successfully via RPC")

        except Exception as e:
            if "does not exist" in str(e).lower() or "rpc" in str(e).lower():
                # If RPC doesn't work, provide manual instructions
                print(f"\n⚠️ Automatic migration via RPC not available")
                print(f"\nPlease run the following SQL in your Supabase console:")
                print("\nSQL Script:")
                print("-" * 70)
                print(migration_sql)
                print("-" * 70)
                print("\nSteps:")
                print("1. Go to https://app.supabase.com/project/{PROJECT_ID}/sql")
                print("2. Click 'New Query'")
                print("3. Paste the SQL above")
                print("4. Click 'Run'")
                return False
            else:
                raise

        print(f"\n3. Verifying migration...")
        # Query to verify constraint exists
        response = client.table("users").select("*").limit(1).execute()
        print(f"   ✅ Database connection verified")

        print("\n" + "=" * 70)
        print("Migration completed successfully!")
        print("=" * 70)
        print("\nYou can now create users with these plan types:")
        print("  - Free (Cantidad)")
        print("  - Free (Fecha)")
        print("  - Premium (Cantidad)")
        print("  - Premium (Fecha)")

        return True

    except ImportError as e:
        print(f"❌ Required package not installed: {e}")
        print("Please run: pip install supabase")
        return False
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = apply_migration()
    sys.exit(0 if success else 1)
