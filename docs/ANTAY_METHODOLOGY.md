# Metodología Antay Fábrica de Software
# Última sincronización: corte - [LIVE NOTION FETCH]

### [Base de Documentación Profesional]
  [BLOCK: divider]
### [    Documentación Oficial (SSOT)]
  Esta documentación define la metodología oficial para diseñar, construir, probar, versionar y operar software en Antay bajo estándares enterprise.
  [BLOCK: paragraph]
  ### [Parte I - Principios y Estándares Enterprise]
    ## 1. Filosofía Antay (No negociable)
    - Trabajamos bajo estándares enterprise internacionales.
    - El código debe escalar a millones de registros (performance y memoria como requisito, no como extra).
    - Optimización es estándar base, no opcional.
    - Diseño premium y altos estándares AU/UX al nivel de empresas top mundiales.
    - No sorpresas: cambios puntuales, controlados y con evidencia de no-regresión.
    ## 2. Roles y responsabilidades (modelo mínimo)
    - Owner: prioriza negocio, aprueba planes, valida entregas.
    - Tech Lead (IA/Dev Senior): diseña solución, implementa sin romper, entrega pruebas y evidencia.
    - QA Lead: define smoke/regresión, valida escenarios críticos, audita logs.
    - UX Lead: define flujos, textos, estados y coherencia (habilitar/inhabilitar, staging, previews).
    - Release Manager: versionado, tags, backups, changelog, rollback.
    ## 3. Ciclo de vida estándar (de idea a producción)
    1. Intake: requerimiento claro + criterios de aceptación + no-go (lo que NO se debe tocar).
    1. Diseño: plan técnico + impacto + riesgos + test plan (smoke y regresión).
    1. Build: cambio mínimo viable, modular, con logging y feature flags cuando aplique.
    1. QA: pruebas automatizables + smoke manual reproducible + evidencias (screens/logs).
    1. Release: backup/tag, bump versión, changelog, despliegue controlado.
    1. Operate: monitoreo, gestión de incidencias, mejoras iterativas.
    ## 4. Quality Gates (obligatorio antes de decir 'terminado')
    - Compilación / arranque: python -m py_compile PASS + streamlit run PASS.
    - No-regresión: smoke tests claves ejecutados y documentados.
    - Logs limpios: sin NameError/AttributeError, sin variables no definidas.
    - UX coherente: botones deshabilitados hasta cambios; staging + guardar; feedback visual.
    - Seguridad: credenciales fuera de código (env/secret), no hardcode.
    - Versionado: commit claro, tag, backup previo si el cambio es sensible.
    ## 5. Estándares AU/UX (reglas operativas)
  ### [Parte II - Manual Operativo Oficial (MODO ENTERPRISE)]
    Este documento manda. Si algo contradice prácticas anteriores, prevalece este manual.
    # 1) Reglas de Oro (No Sorpresas)
    1. **No-regresión**: no se rompe nada existente.
    1. **Cambios acotados**: solo tocar lo solicitado + lo mínimo indispensable para que compile y pase gates.
    1. **Sin supuestos**: si falta un dato, se implementa de forma segura con default reversible.
    1. **Observabilidad**: logs legibles para negocio + logs técnicos en modo “Avanzado”.
    1. **Rollback siempre posible**: tag/branch de backup antes de cambios.
    # 2) Flujo Estándar End-to-End
    ## 2.1 Intake
    - Ticket con: objetivo, alcance, NO-alcance, criterios de aceptación, riesgos, dependencias.
    ## 2.2 Plan
    - Propuesta de plan en 5-10 bullets:
    - Archivos a tocar
    - Funciones/paths exactos
    - Tests a crear/actualizar
    - Riesgos de regresión
    - Estrategia de rollback
    - **Se aprueba el plan** y luego se ejecuta sin pedir permiso paso a paso.
    ## 2.3 Implementación (con Quality Gates)
    - Gate 0: `python -m py_compile` (o equivalente)
    - Gate 1: unit tests / tests críticos
    - Gate 2: smoke test manual guiado (pasos + evidencia)
    - Gate 3: revisión de UX (consistencia, claridad, estados, feedback)
    - Gate 4: documentación mínima actualizada (tickets + estado + smoke)
    ## 2.4 Release
    - Commit con mensaje estándar.
    - Tag versionado semántico + notas de release.
    - Checklist de producción.
    # 3) Estándar de Configuración (UX)
    - Toda configuración sensible debe ser:
    - **Staging** (cambios pendientes) + botón **Guardar/Aplicar** + **Cancelar**
    - Botón “Guardar” **deshabilitado** hasta que detecte cambios
    - Vista previa clara del resultado final (“Así se verá en producción”)
    # 4) Estándar de Correo Masivo (Seguridad)
    - Modo Producción y Modo Marcha Blanca (QA) deben ser **mutuamente excluyentes**.
    - En QA:
    - To/CC/BCC se redirigen a listas QA explícitas (separadas).
    - Asunto y banner deben marcar PRUEBA, solo cuando QA esté ON.
    - Nunca se debe inyectar “Marcha Blanca” si el toggle está OFF.
    # 5) Definición de Done (DoD)
  ### [ Parte III - Protocolo de Trabajo con IA (Antigravity / Agentes)]
    # Objetivo
    Asegurar entregables estables y sin regresiones, evitando “errores junior” (indentación, variables no definidas, APIs inexistentes, etc.).
    # Reglas
    - No introducir APIs inventadas (ej. `st.permissions` si no existe).
    - No dejar variables sin definir (`supervisor_copy_target`, `supervisor_log_info`).
    - No romper imports (ej. `components`).
    - No usar `st.rerun()` en loops sin guardas (hash, session_state, flags).
    # Formato de entrega obligatorio
    1. **Plan** (bullets + archivos + funciones).
    1. **Diff mental**: “Qué cambia” / “Qué NO cambia”.
    1. **Gates ejecutados** (comandos + PASS).
    1. **Smoke test** (pasos numerados).
    1. **Notas de riesgo** + rollback.
    # Prompt estándar (plantilla)
    - “Solo modificar lo solicitado, sin refactors adicionales”.
    - “Crear tag backup antes del cambio”.
  ### [Parte IV - Quality Gates – Estándar Antay]
    # Gate 0 – Compilación
    - `python -m py_compile app.py` (o paquete completo)
    - Falla = no se continúa.
    # Gate 1 – Tests Automatizados
    - Unit tests / tests de integración ligeros
    - Tests de no-regresión: rutas críticas del negocio
    # Gate 2 – Preflight (antes de enviar a clientes)
    - Validar configuración activa (Producción vs QA)
    - Validar destinatarios (To/CC/BCC)
    - Vista previa HTML
    # Gate 3 – Smoke Manual (evidencia)
    - Caso feliz
    - Caso sin logo / sin config
    - Caso QA ON
    - Caso QA OFF
    - Caso CC/BCC con múltiples emails
    # Gate 4 – Documentación
    - Ticket actualizado
    - md actualizado
    - SMOKE_TEST actualizado con nuevos casos
  ### [Parte V - Estándares AU/UX (Streamlit / Apps internas)]
    # Claridad
    - Estados visibles: ON/OFF, activo/inactivo.
    - Textos explicativos cortos.
    - “Vista previa” de lo que saldrá en producción.
    # Prevención de errores
    - Botones deshabilitados hasta que existan cambios.
    - Confirmaciones (“Guardado con éxito”, “Cambios pendientes”).
    - Staging + Guardar/Cancelar para operaciones críticas.
    # Consistencia
    - Terminología única (ej. CC/CCO, QA/Marcha Blanca).
    - Evitar duplicar conceptos (“Supervisor” si ya migró a “Copias Internas”).
    # Accesibilidad y estética
    - Tipografías y jerarquía
    - Espaciado y alineación
    - Mensajes de error accionables (qué hacer, dónde, cómo)
  ### [Parte VI - Caso de Estudio – ReporteCobranzas (Logo + Email + QA)]
    [BLOCK: paragraph]
    # Lecciones capturadas (para no repetir)
    1. **Cambios sin staging** provocan loops/”parpadeos” y desconfianza del usuario.
    1. **Variables no definidas** aparecen cuando se hace hotfix sin volver a correr gates.
    1. **QA debe controlar To/CC/BCC completos**; no mezclar “copias de producción” dentro de QA.
    1. El banner/asunto de QA solo debe aparecer cuando el toggle QA está ON.
    # Reglas derivadas
    - QA tiene sus propias listas: `qa_to_list`, `qa_cc_list`, `qa_bcc_list`.
    - Producción tiene sus listas: `prod_cc_list`, `prod_bcc_list`.
    - Al enviar:
  ### [Parte VII - Reglas de Comunicación]
    - Idioma obligatorio: Español
    - Prohibido inglés
    - Glosario en paréntesis cuando haya términos técnicos
    [BLOCK: paragraph]
  ### [Parte VIII - Continuidad, Trazabilidad y Control de versiones (Notion + Github)]
    # 1) Continuidad del Proyecto (Notion como SSOT)
    Regla:
    Objetivo:
    Debe existir SIEMPRE (obligatorio) dentro de cada proyecto en Notion:
    1. FRD
      - Documento oficial del “qué debe hacer la app” + criterios de aceptación 
    1. Estado Actual
      Debe incluir:
      - Versión/tag estable actual (ej: 
      - DONE / IN PROGRESS / BLOCKED 
      - Riesgos conocidos
      - Próximo paso exacto
    1. Log del Proyecto
      Cada sesión de trabajo debe registrar en 5 líneas:
      - Fecha/hora
      - Qué se cambió
      - Resultado Gate 3 (PASS/FAIL)
      - Bugs abiertos (IDs)
      - Próximo paso
    1. Gate 3 Checklist E2E
      - Casos CA-1, CA-2… con pasos + resultado esperado
      - Evidencia (capturas o video)
      - Resultado por versión/tag
    Regla de aceptación:
    [BLOCK: quote]
    # 2) Control de Versiones y Respaldo (GitHub)
    Rol de GitHub en Antay Fábrica de Software (3 roles):
    1. Codebase
    1. Versioning/Rollback
    1. Evidencia técnica
    Reglas obligatorias de trabajo en GitHub:
    1. Trabajar por ramas (Branch = línea de trabajo separada)
      - Toda mejora se hace en una rama, NO directo en 
      - Nombre estándar: 
    1. Commit discipline (commit = registro de cambio)
      - Commits pequeños, descriptivos y relacionados a un objetivo.
      - Cada commit debe permitir entender: “qué se cambió y por qué”.
    1. Tag estable antes de cambios grandes
      - Crear un 
        Ejemplo: 
      - Este tag es el punto seguro para volver atrás.
    1. Rollback (volver atrás) si falla Gate 3
      - Si Gate 3 FAIL, se revierte a último tag estable y se corrige desde ahí.
    1. Push obligatorio + sincronización
      - Todo cambio relevante debe quedar en remoto (GitHub).
      - Prohibido dejar cambios solo en local.
    Definición clave (para evitar confusión):
    [BLOCK: quote]
    # C) Regla específica para IA (Antigravity)
    Política para agentes IA (Antigravity):
    - Antes de codificar, debe leer el 
    - Debe confirmar entendimiento y NO inventar flujos.
    - Debe ejecutar Quality Gates:
      - Gate 0
      - Gate 1
      - Gate 3
    - Al finalizar, debe actualizar:
      - Notion: Estado Actual + Log + resultado Gate 3
      - GitHub: rama + commits + tag si corresponde
    # D) Protocolo de Trabajo con IA (Antigravity / Agentes)
    “Regla de comunicación”
    [BLOCK: quote]
    Ejemplo:
    - “branch (rama: copia paralela del código para trabajar sin afectar lo estable)”
    - “commit (registro: guardado de cambios en GitHub)”
    - “rollback (volver atrás: regresar a una versión estable)”
    - “E2E (fin a fin: prueba completa como lo usa un usuario)”
  ### [Parte IX - Política de Documentación y Cierre de Sesión (DOCOPS Notion)]
    # Política obligatoria de Cierre de Sesión (No Negociable)
    Objetivo:
    Regla:
    1. Backlog (tablero de tareas = Kanban)
      - La sesión debe estar asociada a una tarjeta con ID (ej: QA-E2E-001).
      - Solo se trabaja tareas en columna 
      - Al iniciar sesión: mover a 
    1. GitHub (repositorio de código y versiones)
      - Si hubo cambios: commit (registro de cambios) obligatorio con mensaje claro.
      - Si aplica: tag (etiqueta de versión) creado al cerrar una versión estable.
      - Si no hubo cambios: registrar explícitamente “Sin cambios de código”.
    1. Quality Gates (compuertas de calidad)
      - Gate 0 (arranque/sintaxis): PASS/FAIL registrado.
      - Gate 3 (E2E = fin-a-fin + regresión): PASS/FAIL registrado con evidencia (capturas/video/artefactos).
    1. DOCOPS-NOTION (Documentación Operativa en Notion = actualización automática)
      Antigravity debe actualizar SSOT en Notion (sin copy/paste manual del PO) con:
      - Log del Proyecto — ReporteCobranzas:
      - Estado Actual — ReporteCobranzas:
      - Handoff Automático — para IA:
    1. Cierre formal
      - Marcar la tarjeta del Backlog según resultado:
        - Si PASS: mover a 
        - Si FAIL: mover a 
      - Registrar el “próximo paso exacto” siempre como una tarjeta del Backlog.
    Resultado esperado:
    # Checklist de Cierre — ReporteCobranzas (OBLIGATORIO)
    [BLOCK: to_do]
    [BLOCK: to_do]
    [BLOCK: to_do]
    [BLOCK: to_do]
    [BLOCK: to_do]
    [BLOCK: to_do]
      [BLOCK: to_do]
      [BLOCK: to_do]
      [BLOCK: to_do]
    [BLOCK: to_do]
  ### [Parte X - Prompt estándar para Antigravity]
    ______________________________________________________________________________________________________
    ## Prompt de arranque (OBLIGATORIO)
    Antigravity: SSOT está en Notion.
    1. Abre “Estado Actual — [PROYECTO]” y lee “Handoff Automático — para IA”.
    1. Confirma textualmente: tag (etiqueta), commit (código corto), gates (calidad), bugs abiertos y próximo paso (desde Backlog Ready).
    1. Antes de ejecutar cualquier trabajo, lee “Parte XI — DOCOPS-NOTION — Estándar de Cierre”.
    Regla: todo término técnico debe incluir explicación (entre paréntesis).
    ## Prompt de cierre (OBLIGATORIO)
    Antigravity: ejecuta DOCOPS DONE según Parte XI.
    1. Backlog actualizado (tarjeta y estado).
    1. Log del Proyecto actualizado (entrada + evidencia Gate 3).
    1. Verificación (readback = re-lectura): pega en el chat:
      - texto final del Handoff
      - última entrada del Log
      - tarjeta en Ready como próximo paso
    Sin readback no hay cierre.
  ### [Parte XI - DOCOPS-NOTION — Estándar de Cierre]
    [BLOCK: divider]
    # 1) Objetivo
    Garantizar trazabilidad (registro verificable) y continuidad entre sesiones (sin pérdida de contexto), evitando duplicidades y contradicciones en Notion.
    ## 2) Principio “Handoff Único” (OBLIGATORIO)
    Para evitar información repetida y contradictoria:
    El único bloque “vivo” (que se actualiza en cada sesión) es:
    Datos que viven SOLO ahí (no se repiten en otras secciones):
    - Versión estable actual (tag = etiqueta)
    - Commit relevante (hash = código corto)
    - Gates (compuertas de calidad)
    - Bugs abiertos
    - Próximo paso exacto (siempre desde Backlog en columna Ready)
    Regla anti-duplicidad (OBLIGATORIO):
    Se escribe una sola línea: 
    ## 3) DOCOPS DONE = 3 páginas + verificación (OBLIGATORIO)
    Antigravity solo puede declarar 
    ### A) Backlog (tablero Kanban = tablero por columnas)
    - Identificar la tarjeta activa (ID).
### [Proyectos (Hub)]
  ### [ReporteCobranzas]
    ### [FRD v0.2 — ReporteCobranzas (Antay)]
      # FRD (Functional Requirements Document: Documento de Requisitos Funcionales)
      Proyecto:
      Repositorio (código):
      Tag estable (freeze):
      Fecha:
      Dueño del producto (Product Owner: dueño del requerimiento):
      Objetivo:
      [BLOCK: divider]
      ## 0) Glosario mínimo (para operar sin confusión)
      - SSOT (Single Source of Truth: “fuente única de la verdad”)
      - Vista filtrada
      - Tracking (trazabilidad)
      - Fresh Load (ciclo nuevo)
      - Gate (Quality Gate: “puerta de calidad”)
      - E2E (End-to-End: “de punta a punta”)
      - Rollback (reversión)
      [BLOCK: divider]
      ## 1) Problema a resolver (definición)
      Necesitamos 
      2) Cobranzas
      3) Cartera de clientes
      La app debe:
- Generar el Reporte General (cliente + documentos por pagar).
- Permitir enviar notificaciones.
- Mantener trazabilidad de envíos (qué cliente ya fue notificado y cuándo).
- Permitir reiniciar el ciclo o reiniciar solo la trazabilidad (sin recargar excels).
      [BLOCK: divider]
      ## 2) Alcance (Scope) v0.2
      ### 2.1 Incluye (IN)
      - Carga de 3 Excel y generación de Reporte General.
      - Tab “Notificaciones Email”: selección de clientes con correo, vista previa HTML, envío y reporte post-envío.
      - Trazabilidad de envío en Reporte General:
        - Estado Notificación (Email)
        - Último Envío (fecha/hora)
      - Persistencia de sesión (al día siguiente se ve lo mismo).
      - “Nuevo Ciclo” (cargar nuevos excels con advertencia) y “Nuevo Ciclo de Envíos” (reset de tracking).
      ### 2.2 No incluye (OUT)
      - Rediseñar lógica financiera de deuda/detracción.
      - Cambiar nombres de columnas clave (prohibido).
      - Cambiar motor de PDF / exportación (si existe).
      - Rehacer el envío WhatsApp desde cero (ya existe; solo documentar/estabilizar).
      [BLOCK: divider]
      ## 3) Reglas NO negociables (Anti-regresión)
      1. NO romper el flujo funcional existente.
      1. NO inventar nuevos procesos
      1. NO renombrar columnas clave
        - COD CLIENTE, EMPRESA, SALDO REAL, CORREO, MATCH_KEY (se mantienen tal cual).
      1. Mejoras AU/UX solamente
      1. Todo cambio debe pasar Gates
      [BLOCK: divider]
      ## 4) Modelo de datos (mínimo)
      ### 4.1 Entradas (Excel)
      - Archivo A: Cuentas por Cobrar
      - Archivo B: Cobranzas
      - Archivo C: Cartera de clientes
      ### 4.2 SSOT (datos maestros)
      - SSOT:
      - Vista filtrada:
      ### 4.3 Columnas de envío
      - CORREO
      - EMAIL_FINAL
        - La app trabaja por 
        - Pero 
          - 1 email por cliente
          - múltiples emails por cliente (ej: contabilidad@…, tesoreria@…)
          - un email compartido por varios clientes (ej: cortega28@hotmail.com)
      [BLOCK: quote]
      [BLOCK: divider]
      ## 5) Tracking (técnico) — trazabilidad de envíos (Email)
      Estas columnas NO vienen del Excel: se crean en la app.
      ### 5.1 Columnas tracking requeridas
      - ESTADO_EMAIL (estado técnico)
        - Valores: PENDIENTE | ENVIADO | ERROR | SIN_CORREO
        - Inicial al cargar excels: PENDIENTE (si hay email) o SIN_CORREO (si no hay).
      - FECHA_ULTIMO_ENVIO (timestamp: fecha/hora real)
        - Inicial: vacío
        - Se llena solo si envío confirmado.
      - ESTADO_ENVIO_TEXTO (texto UX)
        - Inicial: PENDIENTE
        - Después: “ENVIADO (HH:MM)” o “ERROR (…)”
      ### 5.2 Regla crítica: conteos por CLIENTE (no por email)
      - “Enviados Hoy” y “Pendientes” se miden por 
      - Motivo: un mismo EMAIL_FINAL puede representar varios clientes.
      [BLOCK: divider]
      ## 6) Flujo correcto del usuario (User Flow) — Email
      ### 6.1 Ciclo completo
      1. Usuario carga 3 Excel (Fresh Load = ciclo nuevo).
      1. Se genera Reporte General.
      1. Tracking inicial:
        - Estado Notificación = PENDIENTE (si aplica)
        - Último Envío = vacío
      1. Usuario va a “Notificaciones Email”, selecciona cliente(s), revisa vista previa HTML, envía.
      1. Si envío exitoso:
        - Se actualiza tracking en SSOT (
        - “Enviados Hoy” incrementa.
        - Se muestra “Reporte Post-Envío (obligatorio)”.
      1. La sesión se persiste (al día siguiente se ve igual).
      ### 6.2 Nuevo ciclo (reemplaza todo)
    ### [Estado Actual — ReporteCobranzas]
      [BLOCK: divider]
      DOCOPS_ANCHOR_HANDOFF
      ## 1) Handoff Automático — ReporteCobranzas (para IA) — Único BLOQUE "VIVO"
      Uso:
    ### [Log del Proyecto — ReporteCobranzas]
      ### Log del Proyecto — ReporteCobranzas (Bitácora)
      Formato de registro (usar siempre):
      [Fecha AAAA-MM-DD | Hora] — Título corto del cambio
      - Objetivo (qué se buscaba)
      - Cambio aplicado (archivo/rama/tag si aplica)
      - Gate 0: PASS/FAIL
      - Gate 3: PASS/FAIL + evidencia (link/video)
      - Bugs abiertos (IDs o lista)
      - Próximo paso
      [BLOCK: divider]
      ## Ejemplo (plantilla)
      [2026-01-03 | 10:30] — Limpieza UI Tab Reporte General
      - Objetivo:
      - Cambio aplicado:
      - Gate 0:
      - Gate 3:
      - Bugs abiertos:
      - Próximo paso:
      [BLOCK: divider]
      ## Registros
      [2026-01-03 | 17:25] — Gate 3 E2E (End-to-End / Fin-a-Fin) — EJECUCIÓN COMPLETA
      - Objetivo:
      - Cambio aplicado:
      - Servidor (app corriendo local):
      - Gate 0 (compilación/arranque):
      - Gate 3 (E2E):
        - CA-1 (Fresh Load):
        - CA-2 (Persistencia entre tabs):
        - CA-3 (Cliente deuda 0):
        - CA-4 (Email compartido):
        - CA-5 (Post-envío):
      - Evidencia:
      - Bugs abiertos:
      - Próximo paso:
      [BLOCK: divider]
      [2026-01-03 | 22:35] — BUG-TRACKING-001 Fix Tracking + Gate 3 Regresión + Release v1.5.1
      - Objetivo:
      - Cambio aplicado:
        - Evitar overwrite de 
        - Refresh controlado post-envío + persistencia visual del “Resumen del Proceso”.
      - Gate 0:
      - Gate 3 (E2E + Regresión):
        - AC1/AC2/AC6 validados:
        - Regresión adicional con múltiples clientes:
      - Evidencia:
      - Bugs abiertos:
      - Release:
        - Commit:
        - Tag:
      - Próximo paso:
      [BLOCK: divider]
      [2026-01-03 | 22:45] — Cierre de sesión (servidor + artifacts)
      - Objetivo:
      - Acción:
      - Entregables:
      - Próximo paso:
    ### [Gate 3 Checklist E2E — ReporteCobranzas]
      ### Gate 3 — Checklist E2E (End-to-End = fin a fin)
      Versión evaluada (tag):
      Fecha de ejecución:
      Ejecutado por:
      ### CA-1: Nuevo ciclo (Fresh Load = carga nueva)
      - Pasos: cargar 3 excels
      - Esperado: tracking inicia en PENDIENTE / vacío; “Enviados Hoy” = 0
      - Resultado: PASS/FAIL
      - Evidencia: __
    ### [Backlog / Bugs — ReporteCobranzas]
      ### [DATABASE: backlog_reporte_cobranzas.csv]
    [BLOCK: paragraph]
  ### [CatalogPro Enhanced v2]
    ### [FRD - CatalogPro Enhanced v2]
      # Documento de Requerimientos Funcionales (Definitivo)
      - Proyecto:
      - Versión:
      - Fecha:
      - Portal:
      - Administrador:
      - Persistencia:
      [BLOCK: divider]
      ## 1. Control del documento
      ### 1.1 Propósito
      Este documento define los requerimientos funcionales de CatalogPro Enhanced v2, orientado a emprendedores y pymes sin conocimientos técnicos para crear catálogos digitales premium desde Excel o Google Sheets, con exportación a PDF, control de licencias y acceso mediante login.
      ### 1.2 Cambio v1.1
      Esta versión incorpora decisión PRO: persistencia en base de datos Postgres para usuarios, licencias, consumo, auditoría y configuración; y actualiza requerimientos relacionados a seguridad, almacenamiento y trazabilidad.
      ### 1.3 Audiencia
      Product Owner, Administración (Antay), Desarrollo, QA y stakeholders comerciales.
      ### 1.4 Definiciones
      [BLOCK: table]
        [BLOCK: table_row]
        [BLOCK: table_row]
        [BLOCK: table_row]
        [BLOCK: table_row]
        [BLOCK: table_row]
        [BLOCK: table_row]
        [BLOCK: table_row]
        [BLOCK: table_row]
      ## 2. Visión del producto y objetivos
      ### 2.1 Público objetivo
      Pequeños y medianos emprendedores (no técnicos) que necesitan generar catálogos de alto impacto en minutos, desde una hoja de cálculo.
      ### 2.2 Objetivos de negocio
      Monetizar mediante licencias; vender por RRSS y asignar credenciales; experiencia premium por defecto; soporte a crecimiento sin pérdida de datos.
      ### 2.3 Objetivos de usuario
      Cargar productos, configurar identidad del catálogo, previsualizar, exportar PDF Premium y compartir.
      ## 3. Roles y permisos
      ### 3.1 Administrador
      Crea usuarios, asigna contraseñas, define licencias y límites, bloquea/desbloquea usuarios, revisa consumo y auditoría. Cerrar sesión NO elimina usuarios.
      ### 3.2 Usuario Emprendedor
      Configura su catálogo (tienda, título, logo, colores, columnas PDF, etc.), carga data y exporta PDFs mientras su licencia esté activa.
      ## 4. Reglas de negocio
      ### BR-01 Login obligatorio
      Nadie accede a funcionalidades sin iniciar sesión.
      ### BR-02 Usuario = correo
      El identificador del usuario es su correo.
      ### BR-03 Persistencia
      Cerrar sesión NO borra usuarios, licencias, consumo, auditoría ni configuraciones. Todo persiste en Postgres.
      ### BR-04 Generación = exportación PDF
      1 generación equivale a 1 exportación exitosa de PDF.
      ### BR-05 Free (N total)
      Free otorga N exportaciones PDF totales (no se resetea mensual).
      ### BR-06 Licencias pagadas
      Existen 2 tipos: por tiempo (rango de fechas) y por cantidad (N exportaciones PDF).
      ### BR-07 Prioridad
      Licencia pagada activa tiene prioridad sobre Free.
      ### BR-08 Bloqueo total
      Cuota agotada o licencia vencida => bloqueo total del portal.
      ### BR-09 Placeholder
      ImagenURL opcional. Si falta o falla => placeholder; el PDF se genera igual.
      ### BR-10 Agrupaciones opcionales
      Línea/Familia/Grupo/Marca opcionales.
      ## 5. Estructura de datos
      ### 5.1 Fuentes soportadas
      Excel (XLSX) y Google Sheets (implementado).
      ### 5.2 Columnas requeridas y opcionales
      [BLOCK: table]
        [BLOCK: table_row]
        [BLOCK: table_row]
        [BLOCK: table_row]
        [BLOCK: table_row]
        [BLOCK: table_row]
        [BLOCK: table_row]
        [BLOCK: table_row]
        [BLOCK: table_row]
        [BLOCK: table_row]
        [BLOCK: table_row]
        [BLOCK: table_row]
        [BLOCK: table_row]
      ### 5.3 Validación
      Errores de estructura deben mostrarse en lenguaje simple. Campos opcionales no bloquean la generación.
      ## 6. Persistencia PRO (Postgres)
      ### 6.1 Principio
      Usuarios, licencias, consumo, auditoría y configuración deben persistir en Postgres para evitar pérdida de información y soportar monetización a escala.
      ### 6.2 Modelo lógico mínimo
      [BLOCK: table]
        [BLOCK: table_row]
        [BLOCK: table_row]
        [BLOCK: table_row]
        [BLOCK: table_row]
        [BLOCK: table_row]
        [BLOCK: table_row]
      ### 6.3 Seguridad de credenciales
      Las contraseñas se almacenan como hash seguro (p.ej., bcrypt/argon2). Nunca se guarda contraseña en texto plano.
      ### 6.4 Variables y secretos
      El acceso a Postgres se configura por variables de entorno (DATABASE_URL) y secretos del entorno de despliegue.
      ## 7. Inventario de pantallas
      ### S-01 Login
      Ingreso con correo y contraseña.
      ### S-02 Home / Cargar data
      Carga desde Excel o Google Sheets, con vista previa.
      ### S-03 Configuración del catálogo
      Branding y preferencias; incluye botón Guardar con control de cambios.
      ### S-04 Previsualización
      Vista del catálogo con filtros (si existen columnas de agrupación).
      ### S-05 Exportar PDF
      Exportación PDF Premium por defecto; consume cuota solo si es exitosa; resumen final.
      ### S-06 Bloqueo
      Pantalla de bloqueo total cuando no hay licencia activa o cuota agotada.
      ### S-07 Panel Admin
      Usuarios, licencias, cuotas, vigencias, bloqueos y auditoría.
      ## 8. Requerimientos funcionales
      ### 8.1 Detalle por módulo
      Los requerimientos se agrupan por módulos: AUTH, ADMIN, LIC, CFG, DATA, PDF, STORE.
      ### Detalle por módulo
      ### AUTH - Autenticación y sesión
      FR-AUTH-01 (Must)
      Criterios de aceptación:
- Sin sesión: solo Login.
- Credenciales válidas: acceso.
- Credenciales inválidas: error genérico sin filtrar existencia.
      FR-AUTH-02 (Must)
      Criterios de aceptación:
- Cerrar sesión no borra usuarios/licencias/consumo/configuración.
- Vuelve a pantalla Login.
      ### ADMIN - Administración
      FR-ADM-01 (Must)
      Criterios de aceptación:
- Solo rol admin accede.
- Acciones registradas en audit_log.
      FR-ADM-02 (Must)
      Criterios de aceptación:
- Usuario puede loguear inmediatamente.
- No existe ‘Eliminar usuario’ para operación normal; se usa Bloqueo.
      FR-ADM-03 (Must)
      Criterios de aceptación:
- Usuario bloqueado queda sin acceso a TODO el portal.
- Desbloqueo restituye acceso según licencia activa.
      ### LIC - Licencias y consumo
      FR-LIC-01 (Must)
      Criterios de aceptación:
- Por tiempo: acceso entre start_date y end_date.
- Por cantidad: consume por exportación PDF exitosa.
- Free no se resetea mensual.
    ### [Backlog/Bugs_CatalogPro]
      ### [Backlog - CatalogPro]
        ### [DATABASE: New database]
    ### [Licencias / Monetización]
      ### [DATABASE: Licencias_CatalogPro]
    ### [Incidente: Código Perdido por Tokens Hardcodeados (25/01/2026)]
      # Lecciones Aprendidas - Incidente de Código Perdido
      [BLOCK: callout]
    ### [Changelog v1.4.0 - 2026-02-05]
      # Historial de Cambios - CatalogPro v1.4.0
      Fecha de sincronizacion: 2026-02-05 13:54:36
      [BLOCK: divider]
      ## v1.4.0 - Sincronizacion con GitHub (2026-02-05)
      ### Cambios en Documentacion
      - Actualizada version del FRD a v1.4.0
      - Documentada arquitectura real: Sistema hibrido JSON + Google Sheets
      - Clarificado que Postgres es ROADMAP (no implementado)
      ### Estado del Repositorio GitHub
      - Ultimo commit en main: 2f652bb (CP-UX-011, 25/01/2026)
      - Branch dev adelantado: a885a86
      ### Discrepancias Resueltas
      - Version sincronizada: v1.4.0 (antes: inconsistencia v1.3.1/v1.3.2)
      - Arquitectura clarificada: JSON+Sheets (actual) vs Postgres (futuro)
      [BLOCK: callout]
    [BLOCK: paragraph]
  ### [Antay Reports System]
    [BLOCK: paragraph]
    ### [FRD - Antay Report System]
    ### [Backlog/Bugs_Antay Report System]
    [BLOCK: paragraph]
    [BLOCK: paragraph]
  ### [Sistema de Pricing Inteligente con Claude MCP]
  ### [Sistema de Punto de Venta - POS]
    # Antecedentes:
### [Guías y manuales de desarrollo]
  [BLOCK: paragraph]
  [BLOCK: bookmark]
  [BLOCK: bookmark]
  [BLOCK: bookmark]
  [BLOCK: bookmark]
  [BLOCK: bookmark]
[BLOCK: paragraph]
