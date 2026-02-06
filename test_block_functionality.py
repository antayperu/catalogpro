"""
Script de testing para CP-FEAT-015: Bloqueo/Desbloqueo de Usuarios
Ejecutar: python test_block_functionality.py
"""
from auth import AuthManager

def test_block_unblock():
    print("\n=== TEST: Bloqueo/Desbloqueo de Usuarios ===\n")

    auth = AuthManager()

    # Buscar usuario de prueba (no admin)
    users = auth.get_all_users()
    test_user = None
    for user in users:
        if user['email'] != auth.admin_email and not user['info'].get('is_admin'):
            test_user = user['email']
            break

    if not test_user:
        print("[ERROR] No hay usuarios de prueba disponibles")
        print("[INFO] Ejecuta el script para crear un usuario de prueba:")
        print("  python -c \"from auth import AuthManager; auth = AuthManager(); auth.add_user('test@test.com', 'Test User', 'password123')\"")
        return

    print(f"[TEST] Usuario de prueba: {test_user}")

    # TEST 1: Bloquear usuario
    print("\n1. Probando bloqueo...")
    result = auth.block_user(test_user)
    assert result == True, "Bloqueo deberia retornar True"
    assert auth.is_user_blocked(test_user) == True, "Usuario deberia estar bloqueado"
    print("   ✅ Bloqueo exitoso")

    # TEST 2: Bloqueo duplicado (debe fallar)
    print("\n2. Probando bloqueo duplicado...")
    result = auth.block_user(test_user)
    assert result == False, "Bloqueo duplicado deberia retornar False"
    print("   ✅ Bloqueo duplicado rechazado")

    # TEST 3: Desbloquear usuario
    print("\n3. Probando desbloqueo...")
    result = auth.unblock_user(test_user)
    assert result == True, "Desbloqueo deberia retornar True"
    assert auth.is_user_blocked(test_user) == False, "Usuario deberia estar activo"
    print("   ✅ Desbloqueo exitoso")

    # TEST 4: Desbloqueo duplicado (debe fallar)
    print("\n4. Probando desbloqueo duplicado...")
    result = auth.unblock_user(test_user)
    assert result == False, "Desbloqueo duplicado deberia retornar False"
    print("   ✅ Desbloqueo duplicado rechazado")

    # TEST 5: Proteccion admin
    print("\n5. Probando proteccion de admin...")
    result = auth.block_user(auth.admin_email)
    assert result == False, "Bloqueo de admin deberia ser rechazado"
    print("   ✅ Admin protegido")

    # TEST 6: Usuario inexistente
    print("\n6. Probando usuario inexistente...")
    result = auth.block_user("noexiste@test.com")
    assert result == False, "Bloqueo de usuario inexistente deberia fallar"
    print("   ✅ Usuario inexistente manejado correctamente")

    print("\n[SUCCESS] Todos los tests pasaron ✅\n")

if __name__ == "__main__":
    try:
        test_block_unblock()
    except AssertionError as e:
        print(f"\n[FAILED] Test fallo: {e}\n")
    except Exception as e:
        print(f"\n[ERROR] Error inesperado: {e}\n")
