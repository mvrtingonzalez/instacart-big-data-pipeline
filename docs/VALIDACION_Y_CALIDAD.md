# 🧪 Validación y calidad de datos – Proyecto Instacart

## 📋 1. Validación de las tablas

Se verificó la existencia de las tablas principales y los modelos analíticos en PostgreSQL.

| Tabla | Registros |
|---|---:|
| `master_instacart` | 32.434.489 |
| `mart_product_performance` | 49.677 |
| `mart_department_performance` | 22 |
| `mart_user_behavior` | 206.209 |

## 🔍 2. Calidad de datos

Se realizaron comprobaciones sobre la tabla principal `master_instacart` para evaluar la integridad y consistencia de los datos.

Resultados obtenidos:

- No se encontraron valores nulos en `order_id`, `user_id` ni `product_id`.
- No se encontraron combinaciones duplicadas de `order_id` y `product_id`.
- La columna `reordered` contiene únicamente los valores 0 y 1.
- No se encontraron valores inválidos en `order_number`, `order_dow` ni `order_hour_of_day`.
- La columna `add_to_cart_order` presenta valores entre 1 y 145, sin posiciones inválidas.
- Se identificaron 3 registros con `aisle_id` nulo, correspondientes al producto 6816 (`Scotch Kids 5" Scissors`). Estos registros se conservaron para evitar introducir información artificial.

## 📊 3. Validación de los modelos analíticos

Se comprobó la consistencia de los resultados de los modelos Mart generados mediante dbt.

### 🛒 Mart Product Performance

- Contiene 49.677 registros, correspondientes a productos distintos.
- La suma de `cantidad_compras` coincide con los 32.434.489 registros de `master_instacart`.
- La suma de `cantidad_recompras` coincide con los 19.126.536 registros donde `reordered = 1`.

### 🏬 Mart Department Performance

- Contiene 22 departamentos distintos.
- No presenta valores nulos en la columna `departamento`.
- La suma de `total_compras` coincide con los 32.434.489 registros de `master_instacart`.
- La suma de `total_recompras` coincide con los 19.126.536 registros donde `reordered = 1`.

### 👥 Mart User Behavior

- Contiene 206.209 usuarios.
- La cantidad de usuarios coincide con los usuarios distintos de `master_instacart`.
- La suma de `cantidad_pedidos` coincide con los 3.214.874 pedidos distintos de la tabla principal.

## 🧪 4. Pruebas de dbt

Se ejecutaron las pruebas de calidad definidas en dbt, obteniendo los siguientes resultados:

- 20 pruebas exitosas (`PASS`).
- Se verificaron condiciones de unicidad y ausencia de valores nulos en los modelos correspondientes.
- Se comprobó la correcta generación de los modelos y sus dependencias mediante `ref()`.
- Se ejecutó correctamente `dbt parse`.
- Se generó la documentación mediante `dbt docs generate`.

## ⚡ 5. Rendimiento

Se realizaron pruebas de rendimiento mediante `EXPLAIN ANALYZE` sobre los modelos analíticos.

| Modelo | Operación | Tiempo de ejecución |
|---|---|---:|
| `mart_product_performance` | Consulta completa | 17,36 ms |
| `mart_product_performance` | Consulta filtrada | 8,26 ms |
| `mart_user_behavior` | Consulta completa | 25,02 ms |

Las consultas sobre los modelos analíticos presentaron tiempos de respuesta bajos.

La medición de rendimiento de la tabla principal `master_instacart` no se completó debido a un cierre inesperado de la conexión con PostgreSQL durante la ejecución de la prueba. Por este motivo, no se presenta una medición de rendimiento de dicha tabla.

## 🗂️ 6. Particionamiento de datos

Se implementó particionamiento durante la etapa de procesamiento con PySpark, utilizando el formato Parquet.

La tabla maestra se almacenó mediante el método:

`partitionBy("department_id")`

Esto generó una estructura de directorios organizada según el identificador del departamento.

**🎯 Objetivos del particionamiento:**

- Organizar los datos procesados.
- Facilitar la lectura selectiva por departamento.
- Aprovechar la optimización Partition Pruning de Spark.
- Reducir la cantidad de datos leídos en consultas que filtren por `department_id`.

El particionamiento se implementó en la capa de almacenamiento Parquet. No se implementó particionamiento nativo en PostgreSQL, ya que no se identificó una necesidad concreta que justificara agregar esa complejidad a la arquitectura actual.

## 📈 7. Validación de Power BI

Se verificó la conexión entre Power BI y PostgreSQL.

Comprobaciones realizadas:

- Las tres consultas de Power BI apuntan a sus respectivas tablas en el esquema `public`.
- Se confirmó la conexión con la base de datos `instacart`.
- Se ejecutó una actualización de los datos en Power BI.
- La actualización finalizó correctamente, sin errores.

Los dashboards utilizan los siguientes modelos:

- `mart_product_performance`: análisis del rendimiento de los productos.
- `mart_department_performance`: análisis del rendimiento por departamento.
- `mart_user_behavior`: análisis del comportamiento de los usuarios.

## 📝 8. Conclusión

Las validaciones realizadas permitieron comprobar la integridad de la tabla principal y la consistencia de los modelos analíticos generados mediante dbt.

Se obtuvieron resultados satisfactorios en las pruebas de calidad, con 20 pruebas exitosas, y se verificó que las métricas de los modelos Mart coincidieran con los registros de la tabla principal.

También se confirmó el correcto funcionamiento de la conexión entre PostgreSQL y Power BI, incluyendo la actualización de los datos.

Como observación, quedó pendiente la medición de rendimiento de master_instacart debido al cierre inesperado de la conexión con PostgreSQL. Sin embargo, fue posible completar las pruebas de rendimiento de los modelos analíticos.
