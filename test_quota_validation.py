"""
Test de validacion de cuota para CP-LIC-002
Verifica que check_quota funcione correctamente
"""
from auth import AuthManager

def test_quota_scenarios():
    print("\n=== TEST: Validacion de Cuota ===\n")

    auth = AuthManager()

    # Buscar usuarios con diferentes cuotas
    users = auth.get_all_users()

    print("Usuarios encontrados y sus cuotas:")
    print("-" * 60)

    test_cases = []

    for user in users:
        email = user['email']
        info = user['info']
        quota = info.get('quota', 0)
        plan_type = info.get('plan_type', 'Free')
        expires_at = info.get('expires_at', 'N/A')
        is_admin = info.get('is_admin', False)

        has_quota = auth.check_quota(email)
        is_expired = auth.is_plan_expired(email)

        print(f"\nEmail: {email}")
        print(f"  Plan: {plan_type}")
        print(f"  Quota: {quota}")
        print(f"  Expira: {expires_at}")
        print(f"  Es Admin: {is_admin}")
        print(f"  check_quota(): {has_quota}")
        print(f"  is_plan_expired(): {is_expired}")

        # Guardar casos de prueba
        test_cases.append({
            'email': email,
            'quota': quota,
            'has_quota': has_quota,
            'is_expired': is_expired,
            'is_admin': is_admin
        })

    print("\n" + "=" * 60)
    print("VALIDACIONES:")
    print("=" * 60)

    # Test 1: Usuario con quota > 0 debe poder generar
    users_with_quota = [t for t in test_cases if t['quota'] > 0 and not t['is_expired']]
    if users_with_quota:
        print(f"\n1. Usuarios con quota > 0: {len(users_with_quota)}")
        for t in users_with_quota:
            if t['has_quota']:
                print(f"   OK: {t['email']} - quota={t['quota']} - check_quota=True")
            else:
                print(f"   ERROR: {t['email']} - quota={t['quota']} pero check_quota=False")

    # Test 2: Usuario con quota = 0 NO debe poder generar
    users_without_quota = [t for t in test_cases if t['quota'] == 0 and not t['is_admin']]
    if users_without_quota:
        print(f"\n2. Usuarios con quota = 0: {len(users_without_quota)}")
        for t in users_without_quota:
            if not t['has_quota']:
                print(f"   OK: {t['email']} - quota=0 - check_quota=False (BLOQUEADO)")
            else:
                print(f"   ERROR: {t['email']} - quota=0 pero check_quota=True (DEBERIA ESTAR BLOQUEADO)")

    # Test 3: Usuario vencido NO debe poder generar
    expired_users = [t for t in test_cases if t['is_expired']]
    if expired_users:
        print(f"\n3. Usuarios vencidos: {len(expired_users)}")
        for t in expired_users:
            if not t['has_quota']:
                print(f"   OK: {t['email']} - Vencido - check_quota=False (BLOQUEADO)")
            else:
                print(f"   ERROR: {t['email']} - Vencido pero check_quota=True (DEBERIA ESTAR BLOQUEADO)")

    # Test 4: Admin siempre debe poder generar
    admin_users = [t for t in test_cases if t['is_admin']]
    if admin_users:
        print(f"\n4. Usuarios Admin: {len(admin_users)}")
        for t in admin_users:
            if t['has_quota']:
                print(f"   OK: {t['email']} - Admin - check_quota=True (siempre puede generar)")
            else:
                print(f"   WARNING: {t['email']} - Admin pero check_quota=False")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    try:
        test_quota_scenarios()
        print("\n[SUCCESS] Test completado\n")
    except Exception as e:
        print(f"\n[ERROR] Excepcion: {e}\n")
        import traceback
        traceback.print_exc()
