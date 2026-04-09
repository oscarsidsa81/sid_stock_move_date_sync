# sid_stock_move_date_sync

Módulo para Odoo 15 que sustituye automatizaciones creadas en base de datos (`base.automation` / `ir.actions.server`) por lógica versionada en código, con el objetivo de sincronizar la fecha programada de los movimientos de stock (`stock.move.date`) a partir de fechas informadas en líneas de compra y venta.

## Objetivo

En la base de datos existían varias automatizaciones tipo Studio / acciones automatizadas con nombres como:

- OV - Traslada fecha prevista a programada al modificar
- OV - Traslada fecha contrato a programada al confirmar
- OV - Traslada fecha contrato a programada modificarla
- OV - Traslada fecha prevista o contractual a programada del OUT al modificar

Estas automatizaciones actuaban sobre:

- `purchase.order.line`
- `sale.order.line`

y actualizaban la fecha de movimientos de stock relacionados.

El problema de ese enfoque es que la lógica queda oculta en la base de datos, no se versiona bien, es más difícil de migrar entre entornos y complica la depuración. Este módulo traslada esa lógica a código Python mantenible y controlado por Git.

## Qué hace

### Compras

Sobre `purchase.order.line`, el módulo sincroniza `stock.move.date` cuando:

- cambia `contract_date`
- cambia `estimated_date`
- la línea pasa a estado `purchase`

La fecha aplicada a los movimientos será:

1. `contract_date`, si existe
2. en su defecto, `estimated_date`

Solo se actualizan movimientos relacionados con la línea de compra que cumplan estas condiciones:

- `purchase_line_id = line.id`
- estado distinto de `done` y `cancel`
- tipo de operación `incoming` o `internal`

### Ventas

Sobre `sale.order.line`, el módulo sincroniza `stock.move.date` cuando:

- cambia `estimated_delivery_date`
- cambia `calculated_date`
- la línea pasa a estado `sale`

La fecha aplicada será la más tardía entre:

- `estimated_delivery_date`
- `calculated_date`

Solo se actualizan movimientos relacionados con la línea de venta que cumplan estas condiciones:

- `sale_line_id = line.id`
- estado distinto de `done` y `cancel`
- tipo de operación `outgoing`
- ubicación destino de uso `customer`

### Inicialización

El módulo incluye un `post_init_hook` para recorrer líneas ya existentes tras la instalación y sincronizar movimientos pendientes que deban quedar alineados con las fechas actuales.

## Motivación técnica

Este módulo existe para reemplazar lógica de automatizaciones en base de datos por lógica en módulo, lo que aporta:

- versionado en Git
- despliegue reproducible
- menor dependencia de configuraciones manuales
- trazabilidad de cambios
- mayor facilidad de depuración
- menor riesgo de duplicidades invisibles

## Dependencias

Dependencias funcionales previstas:

- `stock`
- `purchase_stock`
- `sale_stock`
- `oct_fecha_contrato_compras`
- `oct_fecha_contrato_ventas`

Estas dependencias asumen que los campos usados por la lógica están definidos en los módulos de fechas de compras y ventas.

## Campos utilizados

### En compra

Sobre `purchase.order.line`:

- `contract_date`
- `estimated_date`
- `state`

### En venta

Sobre `sale.order.line`:

- `estimated_delivery_date`
- `calculated_date`
- `state`

## Instalación

1. Copiar el módulo al directorio de addons.
2. Actualizar lista de aplicaciones.
3. Instalar `sid_stock_move_date_sync`.
4. Verificar que las dependencias de campos están instaladas previamente.

## Importante: desactivar automatizaciones antiguas

Tras instalar este módulo, se deben desactivar o eliminar las automatizaciones antiguas que hacen la misma función en `base.automation`.

Si no se hace, puede producirse:

- doble escritura sobre `stock.move`
- resultados inconsistentes
- dificultad para depurar
- comportamiento no determinista

Se recomienda revisar especialmente automatizaciones con nombres similares a:

- OV - Traslada fecha prevista a programada...
- OV - Traslada fecha contrato a programada...
- OV - Traslada fecha prevista o contractual a programada del OUT...

## Casos recomendados de prueba

### Compras

1. Modificar `estimated_date` en una línea de compra en estado `purchase`.
2. Modificar `contract_date` en una línea de compra en estado `purchase`.
3. Confirmar una compra con movimientos pendientes.
4. Verificar que no se modifican movimientos `done` o `cancel`.

### Ventas

1. Modificar `estimated_delivery_date` en una línea de venta en estado `sale`.
2. Modificar `calculated_date` en una línea de venta en estado `sale`.
3. Confirmar una venta con movimientos salientes pendientes.
4. Verificar que solo se actualizan movimientos `outgoing` hacia cliente.

## Comportamiento esperado

- La fecha del movimiento de stock queda alineada con la fecha funcional relevante de la línea comercial.
- No se actualizan movimientos cerrados.
- La lógica queda centralizada en código y no en automatizaciones ocultas en la base de datos.

## Limitaciones

- El módulo parte de la existencia real de los campos custom mencionados.
- Si en alguna base esos campos no existen o cambian de nombre, habrá que ajustar dependencias o proteger la lógica.
- Si existe otra lógica custom sobre `stock.move.date`, debe revisarse compatibilidad antes de desplegar.

## Recomendaciones de evolución

A futuro podría valorarse:

- añadir logs más explícitos para auditoría
- encapsular mejor la resolución de fechas en métodos reutilizables
- añadir tests automáticos
- parametrizar el comportamiento por tipo de operación si aparecen nuevos casos

## Autoría y mantenimiento

Módulo orientado a sustituir automatizaciones de base de datos por implementación mantenible en código para el proyecto.