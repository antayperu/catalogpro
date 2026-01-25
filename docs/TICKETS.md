# 🎟️ Control de Tickets - CatalogPro (Antay Factory)

Este documento es la fuente de verdad para el correlativo de tickets y el historial de cambios detallado.

## 📌 Último Ticket Cerrado
**ID:** `CP-BUG-010`
**Título:** Crash en Búsqueda "paneton" (Str Accessor Error)
**Fecha:** 29/12/2025
**Versión:** v1.3.1 - Hotfix

---

## 🏗️ Tickets Abiertos (QA Testing - 24/01/2026)

### CP-BUG-014 - CRITICAL ⚠️
**Tipo:** BUG  
**Título:** Verificación de Contraseñas Falla  
**Severidad:** CRITICAL  
**Módulo:** AUTH  
**Descripción:** `verify_password()` no puede verificar contraseñas de usuarios recién creados  
**Impacto:** Los usuarios no pueden autenticarse después del registro  
**Estado:** 🔴 Abierto  
**Fecha Detección:** 24/01/2026  

### CP-BUG-013 - HIGH
**Tipo:** BUG  
**Título:** Gestión de Usuarios con Problemas de Persistencia  
**Severidad:** HIGH  
**Módulo:** AUTH  
**Descripción:** Usuarios creados con `add_user()` no se persisten correctamente  
**Impacto:** Afecta registro de nuevos usuarios  
**Estado:** 🟠 Abierto  
**Fecha Detección:** 24/01/2026  

### CP-UX-010 - HIGH ✅ DONE v2
**Tipo:** UX  
**Título:** Mejoras UX Tab "Cargar" (Corporate Premium)  
**Severidad:** HIGH  
**Módulo:** UI/UX - Tab Cargar  
**Descripción:** Jerarquía profesional, eliminación de emojis, progressive disclosure, feedback descriptivo, loading states, FULL DATA DISPLAY  
**Impacto:** Transforma tab de aspecto junior a corporativo premium con visualización completa de datos  
**Estado:** ✅ **DONE**  
**Fecha Detección:** 24/01/2026  
**Fecha Cierre:** 24/01/2026  
**Cambios Implementados v2:**
- ✅ Título "Importar Datos" con microcopy explicativo
- ✅ Eliminados emojis decorativos (🗑️, 👀, 📋)
- ✅ Estructura de ejemplo en expander colapsado
- ✅ Mensajes de error descriptivos con contexto
- ✅ Spinners durante carga ("Importando datos...", "Validando estructura...")
- ✅ Labels profesionales en inputs
- ✅ Feedback con formato bold y captions explicativos
- ✅ **NUEVO v2:** Visualización completa de TODOS los datos cargados (no solo 5)
- ✅ **NUEVO v2:** Altura de 600px para máxima utilización de pantalla
- ✅ **NUEVO v2:** Contador de productos importados
**Beneficios:**
- Aspecto corporativo y profesional
- Mejor guía para el usuario
- Feedback claro en caso de error
- Reducción de ruido visual
- **Visualización completa de datos** (estándar clase mundial)

### CP-UX-009 - HIGH ✅ DONE
**Tipo:** UX  
**Título:** Refactorización UX del Tab Catálogo (Rollback + Mejoras Mínimas)  
**Severidad:** HIGH  
**Módulo:** UI/UX  
**Descripción:** Rollback completo a diseño original de tarjetas + filtros progresivos + eliminación de "Configuración de Vista" redundante  
**Impacto:** Mantiene funcionalidad original, reduce ruido visual, elimina confusión  
**Estado:** ✅ **DONE**  
**Fecha Detección:** 24/01/2026  
**Fecha Cierre:** 24/01/2026  
**Cambios Implementados:**
- ✅ ROLLBACK completo a diseño de tarjetas original (3 columnas)
- ✅ Funcionalidad WhatsApp/Email restaurada al 100%
- ✅ Filtros avanzados colapsados por defecto (mejora UX)
- ✅ Eliminada sección "Configuración de Vista" (reducción de confusión)
- ✅ `object-fit: contain` para mejor calidad de imagen
- ✅ Defaults programáticos: 48 productos/página, imágenes habilitadas
- ✅ Aplicación ejecutándose sin errores
**Lecciones Aprendidas:**
- Mantener lo que funciona, mejorar solo lo necesario
- NUNCA eliminar funcionalidad existente sin aprobación
- Simplicidad > Complejidad en UX

### CP-BUG-012 - MEDIUM
**Tipo:** BUG  
**Título:** Validación de Columnas Rechaza Datos Válidos  
**Severidad:** MEDIUM  
**Módulo:** DATA  
**Descripción:** `_validate_columns()` falla con DataFrames válidos  
**Impacto:** Puede rechazar archivos Excel válidos  
**Estado:** 🟡 Abierto  
**Fecha Detección:** 24/01/2026  

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
| **CP-BUG-014** | BUG | Verificación de Contraseñas Falla | v1.3.1 | 🔴 Abierto | 24/01/2026 |
| **CP-BUG-013** | BUG | Gestión de Usuarios - Problemas de Persistencia | v1.3.1 | 🟠 Abierto | 24/01/2026 |
| **CP-BUG-012** | BUG | Validación de Columnas Rechaza Datos Válidos | v1.3.1 | 🟡 Abierto | 24/01/2026 |
| **CP-BUG-010** | BUG | Crash en Búsqueda "paneton" (Str Accessor Error) | v1.3.1 | ✅ Cerrado | 29/12/2025 |
| **CP-BUG-011** | BUG | Persistencia de Usuarios Admin (Ruta Relativa) | v1.3.1 | ✅ Cerrado | 29/12/2025 |
| **CP-UX-PDF-006** | UX | PDF Pro Layout (Diseño Corp.) | v1.2.5 | ✅ Cerrado | 21/12/2025 |
| **CP-PERF-004** | Perf | Caché de Imágenes en Disco (Best Effort) | v1.2.4 | ✅ Cerrado | 21/12/2025 |
| **CP-UX-UI-003** | UI | Limpieza UI Exportación (Unificar Botones) | v1.2.3 | ✅ Cerrado | 21/12/2025 |
| **CP-UX-PERF-002** | UX/Perf | Preview Paginado + Lazy Load | v1.2.2 | ✅ Cerrado | 21/12/2025 |
| **CP-PERF-001** | Perf | Motor PDF Optimizado (Threads) | v1.2.1 | ✅ Cerrado | 21/12/2025 |
