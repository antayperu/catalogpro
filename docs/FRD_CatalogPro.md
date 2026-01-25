# FRD - CatalogPro Enhanced v2
# Última sincronización: corte - [LIVE NOTION FETCH]
# Fuente: https://exciting-guitar-bc0.notion.site/FRD-CatalogPro-Enhanced-v2-9e20b04a516e4fa2a8bedb0fb18e4b7f

# Documento de Requerimientos Funcionales (Definitivo)
- Proyecto: CatalogPro Enhanced v2
- Versión: v1.1
- Fecha: 2026-01-11
- Portal: https://catalogpro.streamlit.app/
- Administrador: admin@antayperu.com
- Persistencia: Postgres (PRO)
---
## 1. Control del documento
### 1.1 Propósito
Este documento define los requerimientos funcionales de CatalogPro Enhanced v2, orientado a emprendedores y pymes sin conocimientos técnicos para crear catálogos digitales premium desde Excel o Google Sheets, con exportación a PDF, control de licencias y acceso mediante login.
### 1.2 Cambio v1.1
Esta versión incorpora decisión PRO: persistencia en base de datos Postgres para usuarios, licencias, consumo, auditoría y configuración; y actualiza requerimientos relacionados a seguridad, almacenamiento y trazabilidad.
### 1.3 Audiencia
Product Owner, Administración (Antay), Desarrollo, QA y stakeholders comerciales.
### 1.4 Definiciones
[TABLA]
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
[TABLA]
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
[TABLA]
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
FR-AUTH-01 (Must): Login obligatorio previo a cualquier pantalla funcional.
Criterios de aceptación:
- Sin sesión: solo Login.
- Credenciales válidas: acceso.
- Credenciales inválidas: error genérico sin filtrar existencia.
FR-AUTH-02 (Must): Cierre de sesión sin pérdida de datos persistidos.
Criterios de aceptación:
- Cerrar sesión no borra usuarios/licencias/consumo/configuración.
- Vuelve a pantalla Login.
### ADMIN - Administración
FR-ADM-01 (Must): Panel Admin exclusivo para gestionar usuarios, licencias y bloqueos.
Criterios de aceptación:
- Solo rol admin accede.
- Acciones registradas en audit_log.
FR-ADM-02 (Must): Alta de usuario: crear con correo, contraseña inicial y licencia.
Criterios de aceptación:
- Usuario puede loguear inmediatamente.
- No existe ‘Eliminar usuario’ para operación normal; se usa Bloqueo.
FR-ADM-03 (Must): Bloquear/desbloquear usuarios.
Criterios de aceptación:
- Usuario bloqueado queda sin acceso a TODO el portal.
- Desbloqueo restituye acceso según licencia activa.
### LIC - Licencias y consumo
FR-LIC-01 (Must): Licencias por TIEMPO y por CANTIDAD (incluye Free como cantidad N total).
Criterios de aceptación:
- Por tiempo: acceso entre start_date y end_date.
- Por cantidad: consume por exportación PDF exitosa.
- Free no se resetea mensual.
