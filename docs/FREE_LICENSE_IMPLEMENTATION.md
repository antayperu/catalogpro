# Implementación de Licencia FREE por Fecha

## Resumen
Se implementó la funcionalidad de **licencia FREE con expiración temporal** complementando la licencia FREE por cantidad de catálogos ya existente.

## Tipos de Licencia Implementados

### 1. **Free (Cantidad)** - Plan por Cantidad de Catálogos
- **Forma de uso**: Basado en créditos/cuota
- **Límite**: N catálogos máximo (configurable al crear usuario)
- **Expiración**: Sin vencimiento (indefinido)
- **Caso de uso**: Usuarios que necesitan acceso permanente pero con límite de generaciones

**Ejemplo**:
- Usuario creado con 5 créditos iniciales
- Puede generar 5 catálogos máximo
- Sin límite de tiempo

### 2. **Free (Fecha 30 días)** - Plan por Período Temporal
- **Forma de uso**: Basado en fecha de vencimiento
- **Límite**: Sin límite de cantidad (0 créditos configurados)
- **Expiración**: 30 días desde creación del usuario
- **Caso de uso**: Pruebas/trials con período de evaluación

**Ejemplo**:
- Usuario creado hoy
- Acceso ilimitado por 30 días
- Después de 30 días: acceso bloqueado automáticamente

### 3. **Pagado (Cantidad)** - Plan Comercial por Cantidad
- Similar a Free (Cantidad) pero para usuarios de pago
- Admin puede configurar N catálogos según plan contratado

### 4. **Pagado (Fecha)** - Plan Comercial por Período
- Similar a Free (Fecha 30 días) pero para usuarios de pago
- Admin puede configurar fecha personalizada de vencimiento

## Cambios Implementados

### En `main.py`:

#### 1. **Creación de usuarios** (línea 3142-3195)
- Selectbox actualizado con 4 opciones:
  - `Free (Cantidad)`
  - `Free (Fecha 30 días)`
  - `Pagado (Cantidad)`
  - `Pagado (Fecha)`

- **Lógica de inputs**:
  - Si selecciona plan por **Cantidad**: mostrar campo "Créditos Iniciales"
  - Si selecciona plan por **Fecha**: deshabilitar campo de créditos (automático 0)
  - Si selecciona **Free (Fecha 30 días)**: mostrar fecha de vencimiento automática (+30 días)
  - Si selecciona **Pagado**: permitir ingresar fecha personalizada

- **Mapeo a tipos internos**:
  ```python
  "Free (Cantidad)" → plan_type="Free", quota=N
  "Free (Fecha 30 días)" → plan_type="Free (Fecha)", quota=0, expires_at=hoy+30d
  "Pagado (Cantidad)" → plan_type="Premium (Cantidad)", quota=N
  "Pagado (Fecha)" → plan_type="Premium (Fecha)", quota=0, expires_at=[fecha admin]
  ```

#### 2. **Edición de usuarios existentes** (línea 3314-3355)
- Paneles de edición actualizados para mostrar/permitir cambiar plan
- Backward compatibility: mapea planes antiguos (Free/Cantidad/Tiempo) a nuevos formatos
- Lógica condicional para mostrar campos según tipo de plan seleccionado

#### 3. **Visualización en sidebar** (línea 1755-1770)
- Detecta automáticamente si plan es "Free" o "Premium" por prefijo
- Si contiene "Cantidad": muestra saldo de créditos
- Si contiene "Fecha": muestra fecha de vencimiento
- Integrado con lógica de validación existente

### En `auth.py`:

**Sin cambios requeridos** - La validación existente en `check_quota()` ya soporta:
- Validar por fecha (`expires_at`) si está presente
- Validar por saldo de créditos si no hay fecha
- Prioriza fecha sobre saldo (CP-BUG-022)

## Flujo de Validación

1. **Usuario intenta generar catálogo** → `check_quota(email)` en auth.py
2. **Si tiene `expires_at`**:
   - Valida fecha con `is_plan_expired()`
   - Si vencida → Acceso DENEGADO
   - Si vigente → Acceso PERMITIDO (sin consumir créditos)
3. **Si NO tiene `expires_at`**:
   - Valida saldo: `get_user_quota(email) > 0`
   - Si saldo > 0 → Acceso PERMITIDO y decrementa cuota

## Casos de Uso

### Caso 1: Período de Prueba (30 días)
```
Admin crea usuario → "Free (Fecha 30 días)"
→ Usuario obtiene acceso ilimitado por 30 días
→ Día 31 → Acceso automáticamente bloqueado
```

### Caso 2: Usuario Freemium
```
Admin crea usuario → "Free (Cantidad)" con 5 créditos
→ Usuario puede generar máximo 5 catálogos
→ Una vez agotados → Acceso bloqueado
```

### Caso 3: Cliente Pagado Anual
```
Admin crea usuario → "Pagado (Fecha)"
→ Admin ingresa fecha: 2027-02-09 (1 año desde hoy)
→ User tiene acceso ilimitado hasta esa fecha
→ Día siguiente al vencimiento → Acceso bloqueado
```

## Integración con Lógica Existente

| Componente | Impacto |
|-----------|--------|
| `check_quota()` | ✓ COMPATIBLE - Ya soporta comparación de fechas |
| `decrement_quota()` | ✓ COMPATIBLE - Consulta `check_quota()` primero |
| `is_plan_expired()` | ✓ COMPATIBLE - Ya existe validación de fecha |
| Dashboard de Admin | ✓ ACTUALIZADO - Muestra nuevo UI de selección |
| Sidebar | ✓ ACTUALIZADO - Detecta tipo de plan dinámicamente |

## Testing Recomendado

### Caso 1: Crear usuario Free (Cantidad)
1. Ir a Admin → Agregar Usuario
2. Seleccionar "Free (Cantidad)" con 3 créditos
3. Crear usuario
4. Verificar: sidebar muestra "3 catálogos"
5. Generar 3 catálogos
6. 4to intento → Bloqueado

### Caso 2: Crear usuario Free (Fecha 30 días)
1. Ir a Admin → Agregar Usuario
2. Seleccionar "Free (Fecha 30 días)"
3. Verificar: fecha se pre-llena automáticamente con +30 días
4. Crear usuario
5. Verificar: sidebar muestra fecha de vencimiento
6. Usuario puede generar ilimitado hasta la fecha

### Caso 3: Editar usuario existente
1. Ir a Admin → Buscar usuario anterior
2. Click en ⚙️ Ajustes
3. Cambiar plan de "Free (Cantidad)" a "Free (Fecha 30 días)"
4. Guardar
5. Verificar cambio tomó efecto

## Migraciones (Backward Compatibility)

Usuarios antiguos con `plan_type="Free"` se preservan:
- Si no tienen `expires_at`: se comportan como "Free (Cantidad)"
- Si tienen `expires_at`: se comportan como "Free (Fecha)"
- Al editar, se mapean automáticamente al nuevo formato

## Notas Importantes

1. **Sincronización de cuota**: Plans por fecha tienen `quota=0` para evitar confusión
2. **Prioridad de validación**: Fecha > Cantidad (CP-BUG-022)
3. **No requiere migración de datos**: Los campos `expires_at` y `quota` ya existen
4. **Admin puede cambiar plan en cualquier momento**: El cambio toma efecto inmediatamente

## Versión
- Implementado: 2026-02-09
- Versión de app: v1.7.0+
