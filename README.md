# CatalogPro Enhanced v2 - Antay Peru

Sistema de creacion de catalogos digitales profesionales a partir de hojas de calculo.

---
**Version:** v1.7.0
**Fecha:** 14/02/2026
**Estado:** Produccion Estable

---

## Changelog

### v1.7.0 (14/02/2026) - Plan Types por Fecha + Sync Documentacion
**Nuevos tipos de plan con expiracion por fecha**
- Free (Fecha): Plan gratuito con expiracion a 30 dias
- Premium (Fecha): Plan pagado con fecha de expiracion personalizada
- Migracion de constraint `valid_plan_type` en Supabase aplicada
- Sidebar muestra fecha de vigencia con indicador visual (verde/rojo)
- Sincronizacion de version entre codigo, Notion y README

### v1.6.0 (10/02/2026) - Branding Antay + Mejoras UX
**Rediseno visual corporativo completo**
- CP-UX-023: Header corporativo con gradiente Antay (#013366 -> #01bfff)
- CP-UX-018/020/021: Mejoras de visibilidad, Change Detection, contraste
- CP-BUG-019: Fix persistencia de logo corporativo en PDF
- CP-FEAT-016: Cambio de contrasena por usuario y reseteo por admin
- HOTFIX: StreamlitDuplicateElementId (keys explicitos en widgets)
- CSS completo en `styles/antay_theme.css` (+1177 lineas)

### v1.5.1 (06/02/2026) - Bloqueo/Desbloqueo de Usuarios
- CP-FEAT-015: Metodos `block_user()` y `unblock_user()` en AuthManager
- Validacion de status en login (usuarios bloqueados no acceden)
- Indicador visual en Panel Admin
- `remove_user()` deprecado

### v1.5.0 (05/02/2026) - Migracion a Supabase
- CP-LIC-006: SupabaseBackend como backend principal de produccion
- Tabla `users` en PostgreSQL con schema completo
- Migracion exitosa desde Google Sheets
- Sistema de cuotas y licencias completo

---

## Inicio Rapido

### Instalacion
```bash
# Clonar repositorio
git clone https://github.com/antayperu/catalogpro.git
cd catalogpro

# Instalar dependencias
pip install -r requirements.txt

# Configurar base de datos (ver seccion Configuracion)

# Ejecutar aplicacion
streamlit run main.py
```

### Acceso por defecto
- **Admin:** admin@antayperu.com / `admin`
- **Portal:** https://catalogpro.streamlit.app/

---

## Descripcion del Proyecto

Permite a pequenos comerciantes crear catalogos digitales profesionales a partir de Excel o Google Sheets, con exportacion a PDF, sistema de licencias y branding corporativo.

### Flujo Principal
1. Usuario carga Excel/Google Sheets con productos
2. FRDValidator valida datos contra schema
3. Usuario configura catalogo (titulo, logo, colores, columnas)
4. Generacion PDF con ReportLab (paginacion automatica)
5. Descarga del PDF + decremento de cuota

---

## Stack Tecnologico

| Componente | Tecnologia |
|------------|------------|
| **Framework** | Python + Streamlit |
| **Base de Datos** | Supabase (PostgreSQL) |
| **Autenticacion** | bcrypt + Strategy Pattern |
| **Generacion PDF** | ReportLab (NumberedCanvas) |
| **Estilos** | CSS corporativo Antay |
| **Documentacion** | Notion (SSOT) |
| **Deployment** | Streamlit Cloud |
| **Control de Versiones** | GitHub |

---

## Arquitectura

### Patron de Diseno: Strategy Pattern (Autenticacion)

```
AuthManager
├── SupabaseBackend    (PRODUCCION - activo)
├── GoogleSheetsBackend (DEPRECADO - fallback)
└── JsonBackend         (DESARROLLO - fallback local)
```

**Seleccion automatica de backend:**
1. Si existe `[supabase]` en secrets.toml -> SupabaseBackend
2. Si existe `[gcp_service_account]` -> GoogleSheetsBackend
3. Si no hay credenciales cloud -> JsonBackend

### Schema de Base de Datos (Supabase)

```sql
CREATE TABLE users (
  email VARCHAR(255) PRIMARY KEY,
  password_hash VARCHAR(255) NOT NULL,
  name VARCHAR(255) NOT NULL,
  business_name VARCHAR(255),
  phone_number VARCHAR(50),
  currency VARCHAR(10) DEFAULT 'S/',
  pdf_custom_title VARCHAR(255),
  pdf_custom_subtitle VARCHAR(255),
  is_admin BOOLEAN DEFAULT FALSE,
  status VARCHAR(50) DEFAULT 'active',
  plan_type VARCHAR(50) DEFAULT 'Free',
  quota INTEGER DEFAULT 5,
  quota_max INTEGER DEFAULT 5,
  expires_at DATE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  last_login TIMESTAMPTZ
);
```

**Plan types permitidos:**
- `Free`, `Free (Cantidad)`, `Free (Fecha)`
- `Premium`, `Premium (Cantidad)`, `Premium (Fecha)`
- `Cantidad`, `Tiempo` (legacy)

### Validacion FRD (Schema de Productos)

**Columnas REQUIRED:** Codigo, Producto, Unidad, Precio, Stock
**Columnas OPTIONAL:** Linea, Familia, Grupo, Marca, Descripcion, ImagenURL

---

## Estructura del Proyecto

```
catalogpro/
├── .streamlit/          # Config Streamlit + secrets.toml
│   ├── config.toml      # Tema, upload size, XSRF
│   └── secrets.toml     # Credenciales (NO en git)
├── assets/              # Recursos estaticos (logos)
├── backups/             # Backups del proyecto
├── docs/                # Documentacion
├── migration/           # Scripts de migracion
├── styles/
│   └── antay_theme.css  # CSS corporativo Antay
├── tests/               # Tests unitarios
├── utils/
│   └── antay_methodology.py  # Sync con Notion
├── auth.py              # Sistema de autenticacion
├── main.py              # Aplicacion principal
├── version.py           # Control de version (1.7.0)
├── frd_schema.py        # Schema FRD de columnas
├── frd_validator.py     # Validador de datos
├── requirements.txt     # Dependencias Python
└── CLAUDE.md            # Instrucciones para Claude Code
```

---

## Sistema de Licencias

### Planes Disponibles

| Plan | Precio | Exportaciones | Vigencia |
|------|--------|---------------|----------|
| **Free (Cantidad)** | S/0 | 3-5 totales | Sin limite |
| **Free (Fecha)** | S/0 | Ilimitadas | 30 dias |
| **Basico** | S/29-49/mes | 30/mes | Mensual |
| **Pro** | S/79-99/mes | Ilimitadas | Mensual |

### Reglas de Negocio Criticas
- **BR-01:** Login obligatorio para todas las funcionalidades
- **BR-04:** 1 generacion = 1 exportacion PDF exitosa
- **BR-05:** Plan Free (Cantidad) no se resetea
- **BR-07:** Licencia pagada tiene prioridad sobre Free
- **BR-08:** Cuota agotada o vencida = bloqueo total
- **BR-09:** ImagenURL opcional (placeholder si falla)

### Gestion de Usuarios
- Bloqueo/desbloqueo reversible (no eliminacion)
- Cambio de contrasena por usuario
- Reseteo de contrasena por admin
- Proteccion del admin principal

---

## Configuracion de Base de Datos

### Supabase (Produccion)

#### 1. Crear proyecto en Supabase
1. Ve a https://supabase.com y crea un proyecto
2. Region recomendada: South America (Sao Paulo)
3. Plan Free es suficiente para empezar

#### 2. Crear tabla `users`
1. Ve a **SQL Editor** en el dashboard
2. Ejecuta el contenido de `docs/supabase_schema.sql`

#### 3. Configurar secrets
```toml
# .streamlit/secrets.toml
[supabase]
SUPABASE_URL = "https://tu-proyecto.supabase.co"
SUPABASE_KEY = "tu-service-role-key-aqui"
```

**IMPORTANTE:** Este archivo NO debe estar en git (ya esta en `.gitignore`)

#### 4. Migrar usuarios existentes
```bash
python migration/migrate_to_supabase.py
```

#### 5. Verificar conexion
```bash
streamlit run main.py
# Consola debe mostrar: [OK] Usando SupabaseBackend (PostgreSQL)
```

### Backends Alternativos

**JsonBackend (desarrollo local):** Se activa automaticamente si no hay credenciales cloud. Usa `authorized_users.json`.

**GoogleSheetsBackend (deprecado):** Se mantiene por compatibilidad. No recomendado (lento, limites de API).

---

## Metodologia Antay Fabrica de Software

Este proyecto sigue los estandares de **Antay Fabrica de Software**.

### Estructura de Ramas (GitFlow)
- **main:** Produccion estable
- **dev:** Desarrollo activo
- **feature/xxx:** Funcionalidades nuevas
- **fix/xxx:** Correcciones de errores
- **hotfix/xxx:** Correcciones urgentes en produccion

### Flujo de Trabajo
1. Crear branch desde `dev`: `feature/CP-XXX-descripcion`
2. Desarrollar y testear
3. Merge a `dev` para integracion
4. Merge a `main` para release

### Conventional Commits
```
feat(modulo): descripcion     # Nueva funcionalidad
fix(modulo): descripcion      # Correccion de bug
chore(modulo): descripcion    # Mantenimiento
hotfix(modulo): descripcion   # Fix urgente en produccion
```

### Documentacion Viva
La documentacion oficial (SSOT) vive en Notion y se sincroniza al proyecto:
```bash
python utils/antay_methodology.py  # Actualiza docs/ANTAY_METHODOLOGY.md
```

---

## Seguridad

- Contrasenas hasheadas con **bcrypt** (nunca texto plano)
- `secrets.toml` excluido de git via `.gitignore`
- XSRF Protection habilitado en Streamlit
- Validacion de entrada via FRDValidator
- Row Level Security (RLS) en Supabase
- Tokens de Notion leidos desde secrets (nunca hardcodeados)

---

## Debugging

```bash
# Ver logs detallados
streamlit run main.py --logger.level debug

# Verificar backend activo (ver consola)
# [OK] Usando SupabaseBackend (PostgreSQL)
# [WARNING] Fallo al conectar Supabase (...), probando Google Sheets...
# [INFO] No hay credenciales cloud, usando JsonBackend
```

---

## Tickets Pendientes

| Ticket | Prioridad | Descripcion |
|--------|-----------|-------------|
| CP-UX-004 | MUST | Pantalla de bloqueo total comercial (CTA WhatsApp) |
| CP-UX-008 | MUST | Placeholder premium para imagenes |
| CP-UX-005 | MUST | Tab Configuracion con politica Antay |
| CP-LIC-005 | SHOULD | Auditoria minima de consumos |
| CP-UX-006 | SHOULD | Onboarding 3 pasos |
| CP-UX-007 | SHOULD | Unificar tabs en "Compartir" |
| CP-SEC-017 | BAJA | OAuth Google Sign-In |

---

**Desarrollado por Antay Peru**
https://catalogpro.streamlit.app/
