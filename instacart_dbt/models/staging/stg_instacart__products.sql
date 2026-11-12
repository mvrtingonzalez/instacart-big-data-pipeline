-- Modelo staging: información de los productos.
-- Obtiene los datos de productos, pasillos y departamentos desde la tabla maestra.
-- Utiliza DISTINCT para conservar registros únicos según las columnas seleccionadas.
-- TRIM elimina espacios al inicio y al final de los textos.
-- NULLIF convierte las cadenas vacías en valores NULL.

SELECT DISTINCT
    product_id AS producto_id,
    NULLIF(TRIM(product_name), '') AS nombre_producto,
    aisle_id AS pasillo_id,
    NULLIF(TRIM(aisle), '') AS pasillo,
    COALESCE(NULLIF(TRIM(department), ''), 'Sin Departamento') AS departamento,
    department_id AS departamento_id

FROM {{ source('instacart', 'master_instacart') }}