# � CatalogPro Enterprise (Antay Factory)

**Versión Actual:** v1.2.5
**Fecha:** 21 de Diciembre, 2025
**Estado:** 🟢 Estable (Production Ready)
> **Ticket Control:** El correlativo oficial y detalle histórico vive en [`docs/TICKETS.md`](docs/TICKETS.md).

---

## 📋 Resumen del Proyecto
CatalogPro es una aplicación de generación de catálogos empresariales optimizada para manejar grandes volúmenes de datos (800+ SKUs) con estándares de rendimiento y UX corporativos.

**Principios de Fábrica:**
- **Escalabilidad:** Renderizado paginado y lazy loading.
- **Optimización:** Motores concurrentes para PDF e imágenes.
- **Robustez:** Tolerancia a fallos de red y datos corruptos.

---

## 🤖 Reglas Operativas del Agente (Strict Mode)
1.  **Cero Bucles UI:** Máximo 2 intentos de validación por URL. Si falla, reportar y esperar.
2.  **No Login:** El agente **NUNCA** intentará adivinar credenciales ni esquivar logins.
3.  **Procesos Limpios:** Se evitará dejar múltiples puertos abiertos (8501-8510).
4.  **Validación Asistida:** Se priorizará el análisis de código estático y la ejecución de scripts `verify_*.py`, delegando la validación visual final al Humano.

---

## 🎟️ Historial de Cambios (Changelog)

| Versión | Ticket ID | Descripción | Estado |
|---|---|---|---|
| **v1.2.5** | **CP-UX-PDF-006** | **PDF Pro Layout:** Diseño corporativo, imágenes fijas, cero 'nan', secciones unificadas. | ✅ Desplegado |
| **v1.2.4** | **CP-PERF-004** | **Caché Híbrido (Best Effort):** Persistencia en disco de thumbnails para acelerar F5. Fallback automático a RAM si falla escritura. | ✅ Desplegado |
| **v1.2.3** | **CP-UX-UI-003** | **Limpieza UI Exportación:** Unificación de botones, feedback de descarga condicional y estadísticas visibles. | ✅ Desplegado |
| **v1.2.2** | **CP-UX-PERF-002** | **Preview Ultra-Rápido:** Paginación (24 items), Lazy Load de imágenes y Toggle ON/OFF. Preview < 3s. | ✅ Desplegado |
| **v1.2.1** | **CP-PERF-001** | **Motor PDF Optimizado:** Descarga paralela (ThreadPool), Cache de sesión y Rollback legacy. | ✅ Desplegado |
| v1.0.0 | - | Versión inicial funcional. | 📦 Legacy |

---

## 🚦 Decisiones de Arquitectura Vigentes

### 1. Performance & UX
- **Preview:** Siempre paginada (Default: 24 items). Carga de imágenes diferida (Lazy). Opción "Solo Texto" para velocidad máxima.
- **Exportación PDF:** 
    - **Motor:** Concurrente (`ThreadPoolExecutor` max_workers=20).
    - **UX:** Botón único "Generar". Descarga disponible solo post-generación.
    - **Desacople:** La exportación no depende de que el preview haya cargado las imágenes.
- **Caché Híbrido:** 
    - **L1 Memoria:** `st.session_state` (Rápido, se borra al cerrar tab).
    - **L2 Disco (Best Effort):** `.img_cache/` guardando thumbnails. (Persiste tras F5).
    - **Límite:** Max 1000 archivos con limpieza automática. Limitado a thumbnails (no originales).

### 2. Manejo de Datos
- **Imágenes:** No se almacenan blobs gigantes en Session State innecesariamente, solo lo visible o lo exportado.
- **Cache:** `st.session_state` persistente para imágenes descargadas (Warm Cache).

---

## 🧪 Cómo Probar (Test Plan Básico)

### Requisitos
- Dataset de prueba: `ProductSample_Large.xlsx` (800 productos).

### Pasos
1.  **Iniciar App:** `streamlit run main.py`
2.  **Validar Performance:**
    - Cargar excel de 800 items.
    - Verificar que el **Preview** carga en < 3 segundos (Página 1).
    - Navegar a Página 2 (inmediato).
3.  **Validar Exportación:**
    - Ir a pestaña "Exportar".
    - Clic en **"⚙️ Generar Nuevo PDF"** (Motor Optimizado activado).
    - Tiempo esperado (Cold): < 90s.
    - Tiempo esperado (Warm - 2da vez): < 10s.
    - Verificar botón de descarga y estadísticas.

---

## 📊 Métricas de Rendimiento (Benchmark v1.2.2/3)

| Escenario | Dataset | Tiempo Objetivo | Tiempo Real (Promedio) |
|---|---|---|---|
| **Carga Dataset** | 800 items | < 5s | ~2s |
| **Preview (Pg 1)** | 800 items | < 3s | ~0.5s (Texto) / ~3s (Img) |
| **PDF (Cold)** | 800 items | < 90s | ~65s (Varía según red) |
| **PDF (Warm)** | 800 items | < 10s | ~4s |

---

## � Known Issues & Deuda Técnica
1.  **Placeholders:** Las imágenes rotas se manejan, pero el placeholder visual podría ser más estético (CP-RES-005).
2.  **Cache Disco:** Al reiniciar el servidor (F5), se pierde el cache de imágenes. Se requiere persistencia en disco (CP-PERF-004).

---

## 📅 Próximos Pasos (Backlog Recomendado)
- **CP-PERF-004:** Cache de Imágenes en Disco (Persistencia entre sesiones).
- **CP-RES-005:** Robustez avanzada y Placeholders estéticos.