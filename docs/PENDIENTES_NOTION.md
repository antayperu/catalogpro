# Licencias_CatalogPro - Tareas Pendientes

**Última sincronización:** corte
**Total de entradas:** 6

---

## 1. CP-LIC-006

- **AC (Criterios de aceptación):** AC-01: get_user_plan_status() lee de Postgres.
AC-02: Consumo y auditoría persisten en Postgres.
AC-03: No cambia UI (sidebar, bloqueo, admin).
AC-04: Migración incluye script de carga inicial desde Sheet.
- **Dependencias:** CP-LIC-001..005
- **Tipo:** Arquitectura
- **Prioridad:** COULD
- **Notas:** Fase PRO; no bloquear MVP.
- **Estado:** Sin Estado
- **Owner:** Antigravity
- **Evidencia:** Documento de migración + pruebas de lectura/escritura en Postgres.
- **Módulo:** Licencias
- **Descripción:** Migración a Postgres (PRO): mover planes/consumo/auditoría desde Google Sheet a Postgres. Mantener misma UI; cambiar solo la capa de datos.

## 2. CP-LIC-004

- **AC (Criterios de aceptación):** AC-01: Admin puede crear usuario y asignar plan/cuota/vigencia.
AC-02: Opción bloquear usuario (bloqueo total portal).
AC-03: Cambios persisten (Sheet) y aplican al login.
AC-04: No existe borrado automático de usuarios al cerrar sesión.
- **Dependencias:** CP-LIC-003
- **Tipo:** Funcional
- **Prioridad:** MUST
- **Notas:** Alinear con FRD v1.1 sección admin.
- **Estado:** Sin Estado
- **Owner:** Antigravity
- **Evidencia:** Video: crear usuario + asignar cuota + login usuario.
Video: bloquear usuario y ver bloqueo.
- **Módulo:** Licencias
- **Descripción:** Panel Admin: alta/edición de usuario (plan: Free/Cantidad/Tiempo), asignar cuota inicial, cambiar vigencia, bloquear/desbloquear usuario. No borrar usuarios por sesión.

## 3. CP-LIC-002

- **AC (Criterios de aceptación):** AC-01: Usuario bloqueado no accede a tabs internas.
AC-02: Se muestra pantalla única con CTA WhatsApp (+51921566036) y mensaje prearmado con email.
AC-03: Admin NO queda bloqueado.
AC-04: Mensaje sin jerga técnica.
- **Dependencias:** CP-LIC-001, CP-LIC-003
- **Tipo:** Funcional
- **Prioridad:** MUST
- **Notas:** Debe bloquear ‘de todo el portal’ según FRD.
- **Estado:** Sin Estado
- **Owner:** Antigravity
- **Evidencia:** Captura pantalla bloqueo + WhatsApp.
Prueba: usuario con saldo 0 queda bloqueado.
- **Módulo:** Licencias
- **Descripción:** Bloqueo total del portal cuando: (a) saldo por cantidad = 0, o (b) licencia por tiempo vencida. Mostrar pantalla de bloqueo + CTA WhatsApp.

## 4. CP-LIC-001

- **AC (Criterios de aceptación):** AC-01: Si exportación PDF termina OK, se registra 1 consumo.
AC-02: Si exportación falla, NO descuenta.
AC-03: No descuenta doble por recargar página o reintentar el mismo PDF.
AC-04: Sidebar refleja nuevo saldo inmediatamente.
- **Dependencias:** CP-UX-003 (sidebar plan) ✅
- **Tipo:** Funcional
- **Prioridad:** MUST
- **Notas:** MVP: persistencia temporal (ver CP-LIC-003).
- **Estado:** Sin Estado
- **Owner:** Antigravity
- **Evidencia:** Video: export OK descuenta 1.
Video: export falla no descuenta.
Captura sidebar antes/después.
- **Módulo:** Licencias
- **Descripción:** Consumo real por exportación: cada descarga exitosa del PDF descuenta 1 del saldo (por cantidad). Evitar doble consumo por reintentos.

## 5. CP-LIC-005

- **AC (Criterios de aceptación):** AC-01: Cada consumo exitoso genera un registro auditable.
AC-02: Admin puede revisar histórico por email.
AC-03: No se guarda información sensible adicional.
- **Dependencias:** CP-LIC-001, CP-LIC-003
- **Tipo:** Funcional
- **Prioridad:** SHOULD
- **Notas:** Útil para soporte y disputas de cuota.
- **Estado:** Sin Estado
- **Owner:** Antigravity
- **Evidencia:** Captura de registros en Audit + export OK genera fila.
- **Módulo:** Licencias
- **Descripción:** Auditoría mínima de consumos: registrar fecha/hora, email, acción (export OK), resultado, saldo final. (Sheet ‘Audit’ o log).

## 6. CP-LIC-003

- **AC (Criterios de aceptación):** AC-01: Existe fuente única de verdad (Sheet) para plan/saldo/vigencia por email.
AC-02: Actualización de saldo al exportar (CP-LIC-001) persiste.
AC-03: Admin puede editar cuota/vigencia en la Sheet y se refleja en app.
AC-04: Manejo de error de Sheet (mensaje simple).
- **Dependencias:** Acceso Google Sheets ya implementado ✅
- **Tipo:** Arquitectura
- **Prioridad:** MUST
- **Notas:** Preparar función única get_user_plan_status() para leer de Sheet.
- **Estado:** Ready
- **Owner:** Antigravity
- **Evidencia:** Capturas de Sheet + prueba persistencia (cerrar sesión y reingresar).
- **Módulo:** Licencias
- **Descripción:** Persistencia temporal de licencias/consumo SIN Postgres: usar Google Sheet ‘Licencias’ administrada por admin (o fallback JSON). Lectura/escritura por email.

