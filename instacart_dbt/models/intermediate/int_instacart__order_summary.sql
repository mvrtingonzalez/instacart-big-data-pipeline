-- Modelo intermediate: resumen de productos por pedido.
-- Utiliza el modelo int_instacart__order_items como fuente de información.
-- Agrupa los registros por pedido y usuario.
-- COUNT calcula la cantidad total de productos incluidos en cada pedido.
-- SUM con CASE WHEN cuenta únicamente los productos marcados como recompra.
-- Genera una fila por cada pedido.

WITH order_items AS (

    SELECT *
    FROM {{ ref('int_instacart__order_items') }}

)

SELECT
    pedido_id,
    usuario_id,
    COUNT(producto_id) AS total_productos,
    SUM(
        CASE
            WHEN recompra = 1 THEN 1
            ELSE 0
        END
    ) AS productos_recomprados

FROM order_items

GROUP BY pedido_id, usuario_id