{{ config(materialized='table') }}

WITH obtener_datos AS(
    SELECT * FROM {{ref("int_instacart__order_items")}}
),

calcular_compras AS(
    SELECT producto_id, nombre_producto, count(producto_id) as cantidad_compras, 
    SUM(
        CASE 
            WHEN recompra = 1 THEN 1 
            ELSE 0 
        END
        ) as cantidad_recompras 
    FROM obtener_datos GROUP BY producto_id, nombre_producto
)

SELECT
    producto_id,
    nombre_producto,
    cantidad_compras,
    cantidad_recompras,

    ROUND (
        (cantidad_recompras::NUMERIC / cantidad_compras) * 100, 2
    )AS porcentaje_recompra

FROM calcular_compras
