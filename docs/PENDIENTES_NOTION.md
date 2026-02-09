# Backlog Notion - Antay

Sincronizado: 2026-02-08 01:14:43

## CP-LIC-006: Migración a Postgres (PRO): mover planes/consumo/auditoría desde Google Sheet a Postgres. Mantener m...
- **ID de Notion:** 2e67544a-512b-8054-858d-f2339f255b96
- **Estado:** Done
- **Descripción:** Migración a Postgres (PRO): mover planes/consumo/auditoría desde Google Sheet a Postgres. Mantener misma UI; cambiar solo la capa de datos.

## CP-LIC-004: Panel Admin: alta/edición de usuario (plan: Free/Cantidad/Tiempo), asignar cuota inicial, cambiar vi...
- **ID de Notion:** 2e67544a-512b-805a-a148-e532278e95d7
- **Estado:** Done
- **Descripción:** Panel Admin: alta/edición de usuario (plan: Free/Cantidad/Tiempo), asignar cuota inicial, cambiar vigencia, bloquear/desbloquear usuario. No borrar usuarios por sesión.

## CP-LIC-002: Bloqueo total del portal cuando: (a) saldo por cantidad = 0, o (b) licencia por tiempo vencida. Most...
- **ID de Notion:** 2e67544a-512b-80d7-ac23-e209ddbccf75
- **Estado:** Done
- **Descripción:** Bloqueo total del portal cuando: (a) saldo por cantidad = 0, o (b) licencia por tiempo vencida. Mostrar pantalla de bloqueo + CTA WhatsApp.

## CP-LIC-001: Consumo real por exportación: cada descarga exitosa del PDF descuenta 1 del saldo (por cantidad). Ev...
- **ID de Notion:** 2e67544a-512b-80dd-a3b4-f30da41d1a1a
- **Estado:** Done
- **Descripción:** Consumo real por exportación: cada descarga exitosa del PDF descuenta 1 del saldo (por cantidad). Evitar doble consumo por reintentos.

## CP-LIC-005: Auditoría mínima de consumos: registrar fecha/hora, email, acción (export OK), resultado, saldo fina...
- **ID de Notion:** 2e67544a-512b-80e9-a145-cd6086d3b67f
- **Estado:** Sin Estado
- **Descripción:** Auditoría mínima de consumos: registrar fecha/hora, email, acción (export OK), resultado, saldo final. (Sheet ‘Audit’ o log).

## CP-LIC-003: Persistencia temporal de licencias/consumo SIN Postgres: usar Google Sheet ‘Licencias’ administrada ...
- **ID de Notion:** 2e67544a-512b-80f2-b640-ef6de1388dda
- **Estado:** Done
- **Descripción:** Persistencia temporal de licencias/consumo SIN Postgres: usar Google Sheet ‘Licencias’ administrada por admin (o fallback JSON). Lectura/escritura por email.

## CP-UX-010: Mejoras UX corporativas en tab Cargar:

CAMBIOS IMPLEMENTADOS:
✅ Título "Importar Datos" con microco...
- **ID de Notion:** 2f27544a-512b-814e-96db-f30e7930fac5
- **Estado:** Done
- **Descripción:** Mejoras UX corporativas en tab Cargar:

CAMBIOS IMPLEMENTADOS:
✅ Título "Importar Datos" con microcopy explicativo
✅ Eliminados emojis decorativos (🗑️, 👀, 📋)
✅ Estructura de ejemplo en expander colapsado
✅ Mensajes de error descriptivos con contexto
✅ Spinners durante carga ("Importando datos...", "Validando estructura...")
✅ Labels profesionales en inputs
✅ Feedback con formato bold y captions explicativos

BENEFICIOS:
- Aspecto corporativo y profesional
- Mejor guía para el usuario
- Feedback claro en caso de error
- Reducción de ruido visual

## CP-UX-009: Refactorización UX del Tab Catálogo: Filtros progresivos, jerarquía visual mejorada, corrección de i...
- **ID de Notion:** 2f27544a-512b-81fa-b8cb-cb5a6854565b
- **Estado:** Done
- **Descripción:** Refactorización UX del Tab Catálogo: Filtros progresivos, jerarquía visual mejorada, corrección de imágenes desenfocadas/descuadradas.

## CP-BUG-013: Gestión de Usuarios con Problemas de Persistencia: Usuarios creados con add_user() no se persisten c...
- **ID de Notion:** 2f47544a-512b-8103-a690-fa5b35278e8c
- **Estado:** Done
- **Descripción:** Gestión de Usuarios con Problemas de Persistencia: Usuarios creados con add_user() no se persisten correctamente. Afecta registro de nuevos usuarios.

## CP-FIX-00X: Fix Crítico Booleans y Fechas
- **ID de Notion:** 2f47544a-512b-8105-9486-d705a8251db1
- **Estado:** Done
- **Descripción:** Fix Crítico Booleans y Fechas

## CP-ADM-004: Auditoría de Roles y Seguridad
- **ID de Notion:** 2f47544a-512b-8128-b6ae-fed5b78f7197
- **Estado:** Done
- **Descripción:** Auditoría de Roles y Seguridad

## CP-ADM-003: Permitir Edición de Perfil Admin
- **ID de Notion:** 2f47544a-512b-81b1-9701-daf12589fb77
- **Estado:** Done
- **Descripción:** Permitir Edición de Perfil Admin

## CP-BUG-014: Verificación de Contraseñas Falla: verify_password() no puede verificar contraseñas de usuarios reci...
- **ID de Notion:** 2f47544a-512b-81d0-82cc-fdae7b9b7264
- **Estado:** Done
- **Descripción:** Verificación de Contraseñas Falla: verify_password() no puede verificar contraseñas de usuarios recién creados. Los usuarios no pueden autenticarse después del registro.

## CP-ADM-002: Implementar Edición Completa de Usuarios
- **ID de Notion:** 2f47544a-512b-81d6-9dd6-eb4c18ebfdaa
- **Estado:** Done
- **Descripción:** Implementar Edición Completa de Usuarios

## CP-BUG-012: Validación de Columnas Rechaza Datos Válidos. _validate_columns() falla con DataFrames válidos.
- **ID de Notion:** 2f67544a-512b-81bc-a2d3-e52ad29e7168
- **Estado:** Done
- **Descripción:** Validación de Columnas Rechaza Datos Válidos. _validate_columns() falla con DataFrames válidos.

## N/A: 
- **ID de Notion:** 2ff7544a-512b-80dc-9259-cfc949e67db3
- **Estado:** Sin Estado

## CP-UX-003: Sidebar fijo con estado de plan: Plan actual + ‘Te quedan X PDFs’ o ‘Vence dd/mm’ + botón ‘Comprar /...
- **ID de Notion:** 2ff7544a-512b-810e-b37d-c7a19f8da3bb
- **Estado:** Done
- **Descripción:** Sidebar fijo con estado de plan: Plan actual + ‘Te quedan X PDFs’ o ‘Vence dd/mm’ + botón ‘Comprar / Ampliar plan’.

## CP-UX-004: Pantalla de bloqueo total (comercial): cuando cuota=0 o licencia vencida, bloquear TODO el portal y ...
- **ID de Notion:** 2ff7544a-512b-8111-aa4a-d5237c3d557a
- **Estado:** Sin Estado
- **Descripción:** Pantalla de bloqueo total (comercial): cuando cuota=0 o licencia vencida, bloquear TODO el portal y mostrar CTA WhatsApp con mensaje prearmado.

## CP-FEAT-016: Cambio de Contraseña por Usuario

Permitir a usuarios cambiar su propia contraseña desde perfil. For...
- **ID de Notion:** 2ff7544a-512b-811e-b9df-e0b0558a6639
- **Estado:** Done
- **Descripción:** Cambio de Contraseña por Usuario

Permitir a usuarios cambiar su propia contraseña desde perfil. Formulario: password actual + nueva + confirmar. Admin puede resetear passwords.

## CP-FEAT-015: Implementar Bloqueo/Desbloqueo de Usuarios

Según FRD Sección 5.1: No existe 'Eliminar usuario', se ...
- **ID de Notion:** 2ff7544a-512b-8155-96e6-f8fceddf4418
- **Estado:** Done
- **Descripción:** Implementar Bloqueo/Desbloqueo de Usuarios

Según FRD Sección 5.1: No existe 'Eliminar usuario', se usa Bloqueo. Implementar block_user() y unblock_user() usando campo status en Supabase. Reemplazar botón eliminar por bloquear/desbloquear.

## CP-UX-008: Placeholder premium: cuando ImageURL falta/falla, usar imagen placeholder consistente (no texto ‘Sin...
- **ID de Notion:** 2ff7544a-512b-8157-b70b-c4590f9ac947
- **Estado:** Sin Estado
- **Descripción:** Placeholder premium: cuando ImageURL falta/falla, usar imagen placeholder consistente (no texto ‘Sin Imagen’).

## CP-UX-006: Onboarding 3 pasos (arriba): 1) Cargar productos 2) Configurar 3) Descargar PDF. En ‘Cargar’: botón ...
- **ID de Notion:** 2ff7544a-512b-815f-a901-d9f15e2d49ef
- **Estado:** Sin Estado
- **Descripción:** Onboarding 3 pasos (arriba): 1) Cargar productos 2) Configurar 3) Descargar PDF. En ‘Cargar’: botón ‘Descargar plantilla Excel’ + ejemplo.

## CP-SEC-017: Integración OAuth (Google Sign-In)

Autenticación con cuenta de Google como alternativa premium. Bot...
- **ID de Notion:** 2ff7544a-512b-816a-b187-ff0f63d03f73
- **Estado:** Sin Estado
- **Descripción:** Integración OAuth (Google Sign-In)

Autenticación con cuenta de Google como alternativa premium. Botón 'Continuar con Google' en login. Mantener compatibilidad con login tradicional. Usar Supabase Auth.

## CP-FEAT-014: Migración a Supabase PostgreSQL Backend

Implementar SupabaseBackend según FRD v1.1 Sección 6. Migra...
- **ID de Notion:** 2ff7544a-512b-817f-92eb-d4061407d651
- **Estado:** Done
- **Descripción:** Migración a Supabase PostgreSQL Backend

Implementar SupabaseBackend según FRD v1.1 Sección 6. Migración completa de Google Sheets a PostgreSQL. Performance mejorado 10x. 9 usuarios migrados exitosamente.

## CP-UX-001: Ocultar opciones técnicas al emprendedor: eliminar de UI ‘Motor Optimizado (Beta)’ y selector ‘Clási...
- **ID de Notion:** 2ff7544a-512b-819c-b135-c13035baf9a1
- **Estado:** Done
- **Descripción:** Ocultar opciones técnicas al emprendedor: eliminar de UI ‘Motor Optimizado (Beta)’ y selector ‘Clásico (v1)’. Dejar Premium por defecto.

## CP-UX-005: Crear tab ‘⚙️ Configuración’ (branding) y aplicar política Antay: botón Guardar deshabilitado por de...
- **ID de Notion:** 2ff7544a-512b-81a0-8ab5-e01254dea7c3
- **Estado:** Sin Estado
- **Descripción:** Crear tab ‘⚙️ Configuración’ (branding) y aplicar política Antay: botón Guardar deshabilitado por defecto y se habilita solo con cambios.

## CP-UX-002: Renombrar y reforzar tab de exportación: ‘Exportar’ → ‘📄 Descargar PDF’. Colocar CTA grande arriba c...
- **ID de Notion:** 2ff7544a-512b-81e7-9fa4-cf33e17fa5ab
- **Estado:** Done
- **Descripción:** Renombrar y reforzar tab de exportación: ‘Exportar’ → ‘📄 Descargar PDF’. Colocar CTA grande arriba con microcopy de 1 paso.

## CP-UX-007: Unificar tabs ‘WhatsApp’ y ‘Email’ en una sola: ‘📤 Compartir’ con 2 bloques. Reutiliza ‘Último PDF’ ...
- **ID de Notion:** 2ff7544a-512b-81f0-93f2-d427091bbd12
- **Estado:** Sin Estado
- **Descripción:** Unificar tabs ‘WhatsApp’ y ‘Email’ en una sola: ‘📤 Compartir’ con 2 bloques. Reutiliza ‘Último PDF’ sin regenerar (no consume).

## CP-BUG-019: El PDF generado NO muestra el logo corporativo del usuario aunque esté configurado. Tampoco aparecen...
- **ID de Notion:** 3007544a-512b-8189-9c59-c5642182632c
- **Estado:** Ready
- **Descripción:** El PDF generado NO muestra el logo corporativo del usuario aunque esté configurado. Tampoco aparecen el Título PDF ni Subtítulo PDF. Debe restaurarse la funcionalidad para que se muestren estos 3 elementos tal como aparecían antes (imagen de referencia adjunta).

## CP-UX-018: El logo corporativo que el usuario sube en la sección 'Configuración' se pierde al cerrar sesión. De...
- **ID de Notion:** 3007544a-512b-8195-8e4e-d87407825d71
- **Estado:** Ready
- **Descripción:** El logo corporativo que el usuario sube en la sección 'Configuración' se pierde al cerrar sesión. Debe guardarse en Supabase y recuperarse automáticamente.

## CP-UX-020: La sección Configuración necesita botón Guardar explícito con estados (habilitado/deshabilitado) y f...
- **ID de Notion:** 3007544a-512b-81cb-bc75-d3ba15a401fc
- **Estado:** Ready
- **Descripción:** La sección Configuración necesita botón Guardar explícito con estados (habilitado/deshabilitado) y feedback visual claro.

## CP-UX-021: Header principal necesita aspecto corporativo premium con versión visible, badges de características...
- **ID de Notion:** 3007544a-512b-81f5-8e60-d158246cec1e
- **Estado:** Ready
- **Descripción:** Header principal necesita aspecto corporativo premium con versión visible, badges de características y gradientes modernos.

## CP-BUG-022: Priorizar fecha de vencimiento sobre saldo de créditos (Fix Prioridad). Los usuarios con fecha válid...
- **ID de Notion:** 3017544a-512b-81c7-8e90-e12fd0c5edae
- **Estado:** Done
- **Descripción:** Priorizar fecha de vencimiento sobre saldo de créditos (Fix Prioridad). Los usuarios con fecha válida deben poder generar aunque tengan 0 créditos.

