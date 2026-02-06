"""
Script para probar login con usuario bloqueado sin Streamlit
"""
from auth import AuthManager

def test_blocked_user_login():
    print("\n=== PRUEBA: Login con Usuario Bloqueado ===\n")

    auth = AuthManager()
    email = 'acamacho@antayperu.com'
    password = 'Amazonas*2026'

    print(f"Email: {email}")
    print(f"Password: {password}")
    print()

    # Paso 1: Verificar estado
    print("1. Verificando estado del usuario...")
    info = auth.get_user_info(email)
    print(f"   - Usuario existe: {bool(info)}")
    print(f"   - Estado: {info.get('status', 'active')}")
    print(f"   - Bloqueado: {auth.is_user_blocked(email)}")
    print()

    # Paso 2: Verificar credenciales
    print("2. Verificando credenciales...")
    is_authorized = auth.is_authorized(email)
    password_ok = auth.verify_password(email, password)
    print(f"   - Autorizado: {is_authorized}")
    print(f"   - Password correcta: {password_ok}")
    print()

    # Paso 3: Simular flujo de login
    print("3. Simulando flujo de login...")
    if is_authorized and password_ok:
        print("   - Credenciales validas")

        if auth.is_user_blocked(email):
            print("   - Usuario BLOQUEADO")
            print("   - RESULTADO: Login rechazado (CORRECTO)")
            print()
            print("[OK] El usuario bloqueado NO puede hacer login")
            return True
        else:
            print("   - Usuario NO bloqueado")
            print("   - RESULTADO: Login permitido")
            print()
            print("[ERROR] El usuario deberia estar bloqueado")
            return False
    else:
        print("   - Credenciales invalidas")
        print()
        print("[ERROR] Las credenciales deberian ser validas")
        return False

if __name__ == "__main__":
    try:
        result = test_blocked_user_login()
        if result:
            print("\n[SUCCESS] Test paso correctamente\n")
        else:
            print("\n[FAILED] Test fallo\n")
    except Exception as e:
        print(f"\n[ERROR] Excepcion capturada: {e}\n")
        import traceback
        traceback.print_exc()
