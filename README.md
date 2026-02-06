# CatalogPro Enhanced v2 - Antay Peru

Sistema de creacion de catalogos digitales profesionales a partir de hojas de calculo.

---
**Version:** v1.5.1
**Fecha:** 06/02/2026

---

## 📋 Changelog

### v1.5.1 (06/02/2026) - CP-FEAT-015
**Bloqueo/Desbloqueo de Usuarios**
- ✅ Agregar métodos `block_user()` y `unblock_user()` en AuthManager
- ✅ Validación de status en login (usuarios bloqueados no pueden acceder)
- ✅ Indicador visual en Panel Admin (🔒 **BLOQUEADO** / ✅ *Activo*)
- ✅ Botones dinámicos 🔒/🔓 reemplazan botón de eliminación
- ✅ Protección del admin principal (no se puede bloquear)
- ⚠️ `remove_user()` deprecado (usar `block_user()` en su lugar)
- 📖 Cumple con FRD v1.1 §5.1 línea 134 (no eliminar usuarios)

### v1.5.0 (05/02/2026)
- ✅ Migración a Supabase como backend principal
- ✅ Sistema de cuotas y licencias completo

---

## 🚀 Inicio Rápido

### Instalación
```bash
# Clonar repositorio
git clone https://github.com/antayperu/catalogpro.git
cd catalogpro

# Instalar dependencias
pip install -r requirements.txt

# Configurar base de datos (ver sección abajo)

# Ejecutar aplicación
streamlit run main.py
```

---

##  Metodologia Antay Fabrica de Software

Este proyecto sigue los estandares de **Antay Fabrica de Software**.
La documentación oficial se encuentra sincronizada en [docs/ANTAY_METHODOLOGY.md](docs/ANTAY_METHODOLOGY.md).

###  Para el Usuario (Nuevas Sesiones)

Esta metodología está **viva en Notion** y se actualiza constantemente.
Al iniciar un nuevo chat o sesión con Antigravity, SIEMPRE di:

> **"Conéctate a la metodología Antay"**

Esto forzará a la IA a descargar la última versión de los estándares Enterprise antes de escribir código.
**NO uses conocimiento obsoleto.** La verdad está en Notion.

---

###  Instrucciones Tecnicas para Antigravity

Cuando el usuario diga "Conéctate a la metodología Antay", debes:

1. **Instalar la librería:** `pip install notion-client`
2. **Ejecutar el script:** `python utils/antay_methodology.py`
3. **Leer y Aplicar:** Leer [docs/ANTAY_METHODOLOGY.md](docs/ANTAY_METHODOLOGY.md) y usarlo como la única fuente de verdad (SSOT).

---

##  Descripcion del Proyecto

Permite a pequenos comerciantes crear catalogos digitales profesionales a partir de Excel o Google Sheets, con vista web, filtros, exportacion a HTML/PDF y envio por WhatsApp o correo.

##  Stack Tecnologico

- **Framework**: Python + Streamlit
- **Base de Datos**: Supabase (PostgreSQL)
- **Autenticación**: Sistema híbrido (Supabase / Google Sheets / JSON)
- **Generación PDF**: ReportLab
- **Documentación**: Notion (SSOT)
- **Control de Versiones**: GitHub

## 🗄️ Configuración de Base de Datos (Producción)

CatalogPro v1.5.0+ usa **Supabase (PostgreSQL)** como base de datos de producción para autenticación y gestión de usuarios.

### Setup Rápido

#### 1. Crear proyecto en Supabase
1. Ve a https://supabase.com
2. Crea una cuenta o inicia sesión
3. Haz clic en **New Project**
4. Configura:
   - **Name**: `catalogpro-prod`
   - **Database Password**: (genera uno fuerte)
   - **Region**: South America (São Paulo) o el más cercano
   - **Pricing Plan**: Free (suficiente para empezar)
5. Espera ~2 minutos mientras provisiona

#### 2. Crear tabla `users`
1. Ve a **SQL Editor** en el dashboard de Supabase
2. Copia y pega el contenido de `docs/supabase_schema.sql`
3. Ejecuta el script (crea tabla + índices + políticas RLS)

#### 3. Obtener credenciales
1. Ve a **Settings** → **API** en Supabase
2. Copia:
   - **Project URL**: `https://xxxxx.supabase.co`
   - **Service Role Key** (secret key, no la compartas)

#### 4. Configurar secrets
Crea/edita `.streamlit/secrets.toml` en la raíz del proyecto:

```toml
[supabase]
SUPABASE_URL = "https://tu-proyecto.supabase.co"
SUPABASE_KEY = "tu-service-role-key-aqui"
```

**IMPORTANTE**: Este archivo NO debe estar en git (ya está en `.gitignore`)

#### 5. Migrar usuarios existentes
Si ya tienes usuarios en `authorized_users.json`:

```bash
python migration/migrate_to_supabase.py
```

Este script:
- Lee usuarios de `authorized_users.json`
- Los migra a Supabase (con UPSERT, no duplica)
- Muestra reporte de éxito/errores
- Verifica conteo final

### Backends Alternativos

#### Desarrollo Local (sin Supabase)
Si no configuras Supabase, la aplicación automáticamente usa **JsonBackend** (archivo `authorized_users.json`). Funciona perfectamente para desarrollo local.

#### Google Sheets (Deprecated)
El backend de Google Sheets se mantiene por compatibilidad pero **no se recomienda** (lento, límites de API). Si necesitas usarlo, configura:

```toml
[general]
auth_sheet_url = "URL_DE_TU_GOOGLE_SHEET"

[gcp_service_account]
# ... credenciales JSON de GCP
```

### Verificar Configuración

Ejecuta la aplicación y verifica el log en consola:
```bash
streamlit run main.py
```

Deberías ver:
```
[OK] Usando SupabaseBackend (PostgreSQL)
```

Si ves otro backend, revisa tu configuración de `secrets.toml`.

##  Estructura de Ramas (Metodología Antay)

- **main**: Rama estable y publicada (producción)
- **dev**: Rama de desarrollo activo
- **feature/xxx**: Funcionalidades específicas
- **fix/xxx**: Correcciones de errores

### Flujo de Trabajo
1. Desarrollo en `feature/xxx` o `fix/xxx`
2. Merge a `dev` para integración
3. Merge a `main` para release

---

**Desarrollado por Antay Peru** 
