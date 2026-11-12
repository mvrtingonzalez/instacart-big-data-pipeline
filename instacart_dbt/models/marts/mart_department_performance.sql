{{ config(materialized='table') }}

WITH obtener_datos AS (
    SELECT * FROM {{ref ("int_instacart__order_items")}}
),

calcular_departamentos AS(
    SELECT departamento, count(producto_id) as total_compras, count( Distinct producto_id) as productos_distintos, 
    SUM(
        CASE 
            WHEN recompra = 1 THEN 1 
            ELSE 0 
        END) as total_recompras 
    FROM obtener_datos GROUP BY departamento
)

SELECT
    departamento,
    total_compras,
    productos_distintos,
    total_recompras,

    ROUND(
        (total_recompras::NUMERIC / total_compras) * 100,
        2
    ) AS porcentaje_recompra

FROM calcular_departamentos

