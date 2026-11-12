{{ config(materialized='table') }}

WITH obtener_datos AS (

    SELECT *
    FROM {{ ref('int_instacart__order_items') }}

),

obtener_datos2 AS (

    SELECT *
    FROM {{ ref('int_instacart__order_summary') }}

),

metricas_usuario AS (

    SELECT
        usuario_id,
        COUNT(DISTINCT pedido_id) AS cantidad_pedidos,
        COUNT(producto_id) AS productos_comprados,

        SUM(
            CASE
                WHEN recompra = 1 THEN 1
                ELSE 0
            END
        ) AS productos_recomprados

    FROM obtener_datos

    GROUP BY usuario_id

),

promedio_usuario AS (

    SELECT
        usuario_id,
        AVG(total_productos) AS promedio_productos_por_pedido

    FROM obtener_datos2

    GROUP BY usuario_id

)

SELECT
    m.usuario_id,
    m.cantidad_pedidos,
    m.productos_comprados,
    m.productos_recomprados,
    ROUND(p.promedio_productos_por_pedido, 2) AS promedio_productos_por_pedido

FROM metricas_usuario AS m

INNER JOIN promedio_usuario AS p
    ON m.usuario_id = p.usuario_id