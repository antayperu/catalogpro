# CLAUDE.md

Este archivo proporciona orientación a Claude Code (claude.ai/code) cuando trabaja con código en este repositorio.

## Comandos Esenciales

### Ejecutar la aplicación
```bash
streamlit run main.py
```

### Instalar dependencias
```bash
pip install -r requirements.txt
```

### Ejecutar la aplicación con puerto específico
```bash
streamlit run main.py --server.port 8501
```

## Arquitectura del Proyecto

### Visión General
CatalogPro es una aplicación **Streamlit** que permite a pequeños comerciantes crear catálogos digitales profesionales desde Excel o Google Sheets, con exportación a PDF y sistema de licencias.

### Stack Principal
- **Framework**: Streamlit (aplicación web interactiva)
- **Generación PDF**: ReportLab (con canvas personalizado `NumberedCanvas` para paginación)
- **Autenticación**: Sistema híbrido (JSON local / Google Sheets remoto)
- **Validación**: Schema FRD personalizado
- **Gestión de imágenes**: PIL/Pillow

### Componentes Clave

#### 1. Sistema de Autenticación Híbrido (`auth.py`)
El sistema soporta **dos backends** de autenticación intercambiables:

- **JsonBackend**: Almacenamiento local en `authorized_users.json` (desarrollo/fallback)
- **GoogleSheetsBackend**: Almacenamiento en Google Sheets (producción/cloud)

**Patrón de diseño**: Strategy Pattern con interface `AuthBackend`

**Selección automática de backend**:
```python
# En auth.py, línea 261-277
# Si existen credenciales GCP en secrets.toml -> GoogleSheetsBackend
# Si no -> JsonBackend (fallback)
```

**Características importantes**:
- Contraseñas hasheadas con bcrypt
- Sistema de cuotas (Free vs Licencias pagadas)
- Validación de fecha de expiración
- Usuario admin por defecto: `admin@antayperu.com` / `C4m1l02012`

##### Backends Disponibles (v1.5.0+)

**1. SupabaseBackend (PRODUCCIÓN - Recomendado)**
- PostgreSQL managed por Supabase
- ~10x más rápido que Google Sheets
- Seguro con Row Level Security (RLS)
- Plan gratuito: 500MB de base de datos

**Configuración en .streamlit/secrets.toml**:
```toml
[supabase]
SUPABASE_URL = "https://xxxxx.supabase.co"
SUPABASE_KEY = "service_role_key_aqui"
```

**Migración desde JSON**:
```bash
python migration/migrate_to_supabase.py
```

**Características**:
- Velocidad: Login en ~200ms (vs ~2s con Google Sheets)
- Escalabilidad: Soporta millones de usuarios
- Dashboard web para visualizar datos
- Backups automáticos
- API REST nativa

**2. GoogleSheetsBackend (DEPRECATED - Fallback)**
- Almacenamiento en Google Sheets
- Lento (~2s por operación)
- Límites de API (100 req/100s)
- No recomendado para producción
- Se mantiene solo para backward compatibility

**3. JsonBackend (Desarrollo/Fallback)**
- Almacenamiento local en `authorized_users.json`
- Siempre funciona (no depende de servicios externos)
- Usado automáticamente si otros backends fallan

##### Sistema de Bloqueo/Desbloqueo de Usuarios (v1.5.1+)

**Gestión de usuarios problemáticos** sin perder historial:

**Métodos disponibles**:
- `block_user(email)`: Cambia status a 'blocked', impide login
- `unblock_user(email)`: Cambia status a 'active', restaura acceso
- `is_user_blocked(email)`: Verifica si usuario está bloqueado

**Características**:
- **Login validation**: Usuarios bloqueados no pueden iniciar sesión
- **Admin protection**: No se puede bloquear al admin principal
- **UI indicators**: Panel Admin muestra 🔒 **BLOQUEADO** o ✅ *Activo*
- **Reversible**: El bloqueo es temporal y reversible (vs eliminación permanente)
- **FRD compliance**: Cumple con FRD v1.1 §5.1 línea 134 (no eliminar usuarios)

**Importante**: `remove_user()` está deprecado desde v1.5.1. Usar `block_user()` para operaciones normales.

#### 2. Sistema de Validación FRD (`frd_schema.py` + `frd_validator.py`)

**FRD_SCHEMA** define las columnas requeridas y opcionales del catálogo:

**Columnas REQUIRED**:
- `Código`: SKU único del producto
- `Producto`: Nombre comercial
- `Unidad`: Unidad de medida (UND, KG, etc.)
- `Precio`: Precio unitario (float)
- `Stock`: Cantidad en inventario (int)

**Columnas OPTIONAL**:
- `Línea`, `Familia`, `Grupo`, `Marca`: Agrupaciones jerárquicas
- `Descripción`: Descripción detallada
- `ImagenURL`: URL de imagen (con placeholder si falla)

**FRDValidator** valida el DataFrame cargado y genera:
- **Errores**: Bloquean la generación (ej: columnas requeridas faltantes, valores nulos en campos obligatorios)
- **Warnings**: No bloquean (ej: valores nulos en campos opcionales)

#### 3. Flujo Principal de Datos

```
1. Usuario carga Excel/Google Sheets
   ↓
2. Pandas lee y normaliza datos
   ↓
3. FRDValidator valida contra schema
   ↓
4. Usuario configura opciones del catálogo
   - Título, logo, colores
   - Columnas a mostrar en PDF
   - Filtros de agrupación
   ↓
5. Generación PDF con ReportLab
   - NumberedCanvas para "Página X de Y"
   - Tablas con estilos personalizados
   - Imágenes con fallback a placeholder
   ↓
6. Descarga del PDF + Decremento de cuota
```

#### 4. Archivo Principal (`main.py`)

**Estructura** (archivo muy grande, ~39K tokens):
- Autenticación al inicio (`check_authentication()`)
- UI Streamlit con tabs/sections
- Funciones de generación PDF
- Gestión de sesión (`st.session_state`)
- Panel de administración (si usuario es admin)

**Clases importantes**:
- `NumberedCanvas` (línea 29): Canvas personalizado para paginación avanzada en PDF

### Configuración Importante

#### `.streamlit/config.toml`
```toml
[server]
maxUploadSize = 200  # Permite archivos Excel grandes
enableXsrfProtection = true

[theme]
primaryColor = "#667eea"  # Colores corporativos Antay
```

#### `.streamlit/secrets.toml` (NO commitear)
```toml
[general]
auth_sheet_url = "URL_GOOGLE_SHEET"

[gcp_service_account]
# Credenciales JSON de Google Cloud Platform
# Para acceso a Google Sheets Backend
```

### Metodología Antay

Este proyecto sigue la **Metodología Antay Fábrica de Software**:

- **Branches**: `main` (producción) ← `dev` (desarrollo) ← `feature/xxx` o `fix/xxx`
- **Documentación viva**: FRD y metodología se sincronizan desde Notion
- **Tickets**: Gestionados en `docs/TICKETS.md` con formato Notion

**Comando importante**: Al iniciar una nueva sesión, ejecutar:
```bash
python utils/antay_methodology.py  # Actualiza docs/ANTAY_METHODOLOGY.md desde Notion
```

### Patrones de Código

#### 1. Autenticación requerida
Todas las funcionalidades requieren autenticación:
```python
auth = check_authentication()  # En main.py, línea 21
# Si no autenticado -> st.stop()
```

#### 2. Verificación de cuota antes de generar
```python
if not auth.check_quota(user_email):
    st.error("Cuota agotada o licencia vencida")
    return

# Generar PDF...
auth.decrement_quota(user_email)  # Restar 1 crédito
```

#### 3. Validación FRD
```python
from frd_validator import FRDValidator

validator = FRDValidator(df)
result = validator.validate()

if not result['is_valid']:
    st.error("Errores de validación")
    st.dataframe(validator.get_validation_report())
    return
```

#### 4. Manejo de imágenes con fallback
```python
# Si ImagenURL falla o está vacía -> usar placeholder
# El PDF SIEMPRE se genera (BR-09)
```

### Archivos de Utilidad

- `generate_sample.py`: Genera Excel de ejemplo para testing
- `setup_secrets.py`: Configura credenciales Google Sheets
- `test_auth_*.py`: Tests del sistema de autenticación
- `read_pending_tasks.py`: Lee tareas desde Notion

### Reglas de Negocio Críticas (del FRD)

- **BR-01**: Login obligatorio para todas las funcionalidades
- **BR-03**: Cerrar sesión NO borra datos (persistencia real)
- **BR-04**: 1 generación = 1 exportación PDF exitosa
- **BR-05**: Plan Free tiene N exportaciones totales (no se resetea)
- **BR-07**: Licencia pagada tiene prioridad sobre Free
- **BR-08**: Cuota agotada o vencida = bloqueo total
- **BR-09**: ImagenURL opcional (placeholder si falla)
- **BR-10**: Agrupaciones opcionales (Línea/Familia/Grupo/Marca)

### Debugging

#### Ver logs de Streamlit
```bash
streamlit run main.py --logger.level debug
```

#### Verificar backend de autenticación activo
Los prints en consola indican qué backend se está usando:
```
✅ [OK] Usando SupabaseBackend (PostgreSQL)
✅ [OK] Usando GoogleSheetsBackend
⚠️ [WARNING] Fallo al conectar Supabase (...), probando Google Sheets...
ℹ️ [INFO] No hay credenciales cloud, usando JsonBackend
```

**Prioridad de backends** (v1.5.0+):
1. Supabase (si existe `[supabase]` en secrets.toml)
2. Google Sheets (si existe `[gcp_service_account]`)
3. JsonBackend (fallback siempre disponible)

#### Verificar conexión a Supabase
```python
# En Python REPL o script temporal
import streamlit as st
from supabase import create_client

client = create_client(
    st.secrets["supabase"]["SUPABASE_URL"],
    st.secrets["supabase"]["SUPABASE_KEY"]
)

# Probar query
response = client.table("users").select("email, plan_type, quota").execute()
print(f"Usuarios en Supabase: {len(response.data)}")
for user in response.data:
    print(f"  - {user['email']}: {user['plan_type']} ({user['quota']} créditos)")
```

#### Inspeccionar datos de usuario
```python
auth = AuthManager()
user_info = auth.get_user_info("email@ejemplo.com")
print(user_info)  # Ver cuota, plan, fecha de expiración, etc.
```

### Consideraciones de Seguridad

1. **Contraseñas**: SIEMPRE hasheadas con bcrypt (nunca texto plano)
2. **Secretos**: `secrets.toml` NO debe estar en git (añadido a `.gitignore`)
3. **Validación de entrada**: FRDValidator previene inyección de datos maliciosos
4. **XSRF Protection**: Habilitado en config.toml

### Testing

No hay suite de tests automatizados actualmente. Los tests manuales se hacen con:
- `test_auth_local.py`: Prueba JsonBackend
- `test_auth_cloud.py`: Prueba GoogleSheetsBackend
- `test_validation.py`: Prueba FRDValidator

### Deployment

La aplicación se despliega en **Streamlit Cloud**:
- URL: https://catalogpro.streamlit.app/
- Configurar secretos en el dashboard de Streamlit Cloud
- Branch principal: `main`
