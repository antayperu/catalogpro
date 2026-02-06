# 🎟️ Control de Tickets - CatalogPro (Antay Factory)

Este documento es la fuente de verdad para el correlativo de tickets y el historial de cambios detallado.

## 📌 Último Ticket Cerrado
**ID:** `CP-FEAT-015`
**Título:** Implementar Bloqueo/Desbloqueo de Usuarios (Requerimiento FRD)
**Fecha:** 06/02/2026
**Versión:** v1.5.1

---

## 🏗️ Tickets Abiertos

### CP-FEAT-016: Cambio de Contraseña por Usuario
**Tipo**: FEAT
**Prioridad**: Media
**Estado**: 🔴 Abierto
**Descripción**: Permitir a usuarios cambiar su propia contraseña desde el perfil. Actualmente solo el admin puede asignar contraseña inicial.

**Criterios de Aceptación**:
- [ ] Crear sección "Mi Perfil" en menú de usuario
- [ ] Formulario: Contraseña actual + Nueva contraseña + Confirmar
- [ ] Validar contraseña actual antes de cambiar
- [ ] Hash con bcrypt de la nueva contraseña
- [ ] Guardar en Supabase
- [ ] Notificación de éxito/error
- [ ] Admin puede resetear contraseña de cualquier usuario

**Impacto**: Seguridad, autonomía del usuario

---

### CP-SEC-017: Integración OAuth (Google Sign-In)
**Tipo**: SEC
**Prioridad**: Baja (Futuro)
**Estado**: 🔵 Propuesto
**Descripción**: Permitir autenticación con cuenta de Google (OAuth 2.0) como alternativa premium al login tradicional.

**Criterios de Aceptación**:
- [ ] Integrar Supabase Auth con Google OAuth
- [ ] Botón "Continuar con Google" en pantalla de login
- [ ] Crear usuario automáticamente en primera autenticación
- [ ] Sincronizar email y nombre desde cuenta Google
- [ ] Mantener compatibilidad con login tradicional
- [ ] Documentar en FRD como funcionalidad PRO

**Impacto**: UX mejorada, reducción de fricción en onboarding

**Nota**: Requiere análisis de costo-beneficio y priorización vs otras features

---

## 📏 Estándar de Nomenclatura
Formato: `CP-{TIPO}-{###}`

### Tipos Permitidos:
- **PERF**: Performance y Optimización
- **UX**: Experiencia de Usuario (Flujos, Interacción)
- **UI**: Interfaz de Usuario (Estilos, Layout)
- **RES**: Robustez y Estabilidad (Error handling)
- **FEAT**: Nueva Funcionalidad (Negocio)
- **BUG**: Corrección de errores
- **SEC**: Seguridad
- **DOC**: Documentación
- **INST**: Instrumentación y Métricas

### Reglas de Cierre (DOD):
1.  Todo código mergeado debe estar asociado a un Ticket ID.
2.  Al cerrar un ticket, se debe:
    *   Actualizar la tabla de historial en este archivo.
    *   Actualizar `README.md` (Sección Changelog/Versión).

---

## 📜 Historial de Tickets

| ID | Tipo | Título | Versión | Estado | Fecha Detección |
|---|---|---|---|---|---|
| **CP-FEAT-015** | FEAT | Bloqueo/Desbloqueo de Usuarios (Requerimiento FRD) | v1.5.1 | ✅ Cerrado | 06/02/2026 |
| **CP-FEAT-014** | FEAT | Migración a Supabase PostgreSQL Backend | v1.5.0 | ✅ Cerrado | 06/02/2026 |
| **CP-BUG-014** | BUG | Verificación de Contraseñas Falla | v1.3.1 | ✅ Cerrado | 24/01/2026 |

---

### Detalle: CP-FEAT-015 - Bloqueo/Desbloqueo de Usuarios

**Contexto**: El FRD v1.1 Sección 5.1 línea 134 especifica "No existe 'Eliminar usuario' para operación normal; se usa Bloqueo". La aplicación tenía un método `remove_user()` que eliminaba permanentemente usuarios, violando el FRD.

**Solución Implementada**:
- ✅ Métodos `block_user()`, `unblock_user()`, `is_user_blocked()` en AuthManager
- ✅ Validación de status en login (usuarios bloqueados no pueden acceder)
- ✅ Indicador visual en Panel Admin (🔒 **BLOQUEADO** / ✅ *Activo*)
- ✅ Botones dinámicos 🔒/🔓 reemplazan botón de eliminación 🗑️
- ✅ Protección del admin principal (no se puede bloquear)
- ✅ `remove_user()` marcado como deprecated
- ✅ Documentación actualizada (CLAUDE.md, README.md)

**Resultados**:
- Cumplimiento total con FRD v1.1
- Gestión reversible de usuarios problemáticos
- Historial de usuarios preservado
- UX mejorada con indicadores visuales claros

**Testing**:
- ✅ Bloqueo exitoso desde Panel Admin
- ✅ Login rechazado para usuarios bloqueados
- ✅ Desbloqueo restaura acceso completo
- ✅ Admin principal protegido contra bloqueo
- ✅ Persistencia en Supabase verificada

**Archivos modificados**:
- `auth.py`: +95 líneas (nuevos métodos + validación login)
- `main.py`: +30 líneas (UI admin panel)
- `CLAUDE.md`, `README.md`, `docs/TICKETS.md`: Documentación actualizada

---

### Detalle: CP-FEAT-014 - Migración a Supabase PostgreSQL

**Contexto**: El FRD v1.1 Sección 6 especifica "Persistencia PRO (Postgres)" como backend de producción. El sistema anterior usaba Google Sheets (lento, límites de API, inseguro).

**Solución Implementada**:
- ✅ Clase `SupabaseBackend` implementada en `auth.py`
- ✅ Tabla `users` creada en Supabase con schema completo
- ✅ 9 usuarios migrados exitosamente desde `authorized_users.json`
- ✅ Prioridad automática: Supabase > Google Sheets > JSON
- ✅ Fallback automático si Supabase falla
- ✅ Script de migración: `migration/migrate_to_supabase.py`
- ✅ Documentación completa actualizada

**Resultados**:
- Performance: ~10x más rápido (login 200ms vs 2-3s)
- Seguridad: PostgreSQL + Row Level Security (RLS)
- Escalabilidad: Soporta millones de usuarios vs ~1000 con Sheets
- Plan gratuito: 500MB base de datos

**Archivos Modificados**:
- `auth.py` (agregada clase SupabaseBackend)
- `requirements.txt` (agregada dependencia supabase)
- `.streamlit/secrets.toml` (configuración Supabase)
- `CLAUDE.md`, `README.md` (documentación)

**Archivos Creados**:
- `migration/migrate_to_supabase.py`
- `migration/README.md`
- `docs/supabase_schema.sql`
- `docs/SUPABASE_SETUP_CHECKLIST.md`
- Scripts de verificación y testing

**Cumplimiento FRD**: ✅ FRD v1.1 Sección 6 (Persistencia PRO Postgres)

**Metodología Antay**: Plan completo ejecutado, testing validado, documentación actualizada

---
| **CP-ADM-002** | FEAT | Panel Admin: Edición/Gestión Completa | v1.3.2 | ✅ Cerrado | 26/01/2026 |
| **CP-ADM-003** | FEAT | Panel Admin: Edición Perfil | v1.3.2 | ✅ Cerrado | 26/01/2026 |
| **CP-ADM-004** | SEC | Auditoría Roles y Fechas | v1.3.2 | ✅ Cerrado | 26/01/2026 |
| **CP-FIX-00X** | FIX | Parsing Robusto y UX Bloqueo | v1.3.2 | ✅ Cerrado | 26/01/2026 |
| **CP-BUG-013** | BUG | Gestión de Usuarios - Problemas de Persistencia | v1.3.1 | ✅ Cerrado | 24/01/2026 |
| **CP-UX-010** | UX | Mejoras UX Tab "Cargar" (Corporate Premium) | v1.3.1 | ✅ Cerrado | 24/01/2026 |
| **CP-UX-009** | UX | Refactor UX Catálogo (Rollback) | v1.3.1 | ✅ Cerrado | 24/01/2026 |
| **CP-BUG-012** | BUG | Validación de Columnas Rechaza Datos Válidos | v1.3.2 | ✅ Cerrado | 24/01/2026 |
| **CP-BUG-010** | BUG | Crash en Búsqueda "paneton" (Str Accessor Error) | v1.3.1 | ✅ Cerrado | 29/12/2025 |
| **CP-BUG-011** | BUG | Persistencia de Usuarios Admin (Ruta Relativa) | v1.3.1 | ✅ Cerrado | 29/12/2025 |
| **CP-UX-PDF-006** | UX | PDF Pro Layout (Diseño Corp.) | v1.2.5 | ✅ Cerrado | 21/12/2025 |
| **CP-PERF-004** | Perf | Caché de Imágenes en Disco (Best Effort) | v1.2.4 | ✅ Cerrado | 21/12/2025 |
| **CP-UX-UI-003** | UI | Limpieza UI Exportación (Unificar Botones) | v1.2.3 | ✅ Cerrado | 21/12/2025 |
| **CP-UX-PERF-002** | UX/Perf | Preview Paginado + Lazy Load | v1.2.2 | ✅ Cerrado | 21/12/2025 |
| **CP-PERF-001** | Perf | Motor PDF Optimizado (Threads) | v1.2.1 | ✅ Cerrado | 21/12/2025 |
