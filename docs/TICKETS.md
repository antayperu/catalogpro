# 🎟️ Control de Tickets - CatalogPro (Antay Factory)

Este documento es la fuente de verdad para el correlativo de tickets y el historial de cambios detallado.

## 📌 Último Ticket Cerrado
**ID:** `CP-BUG-012`
**Título:** Validación de Columnas Rechaza Datos Válidos
**Fecha:** 27/01/2026
**Versión:** v1.3.2 - Patch

---

## 🏗️ Tickets Abiertos (QA Testing - 24/01/2026)


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
| **CP-BUG-014** | BUG | Verificación de Contraseñas Falla | v1.3.1 | ✅ Cerrado | 24/01/2026 |
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
