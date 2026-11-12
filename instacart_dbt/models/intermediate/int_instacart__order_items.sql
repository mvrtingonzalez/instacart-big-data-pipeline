-- Modelo intermediate: detalle de productos por pedido.
-- Combina los modelos staging de pedidos, productos y relaciones pedido-producto.
-- Utiliza INNER JOIN para relacionar los registros mediante sus identificadores.
-- Enriquece cada producto comprado con información del pedido y del producto.
-- Genera una fila por cada producto asociado a un pedido.

WITH orders AS (

    SELECT *
    FROM {{ ref('stg_instacart__orders') }}

),

order_products AS (

    SELECT *
    FROM {{ ref('stg_instacart__order_products') }}

),

products AS (

    SELECT *
    FROM {{ ref('stg_instacart__products') }}

)

SELECT
    o.pedido_id,
    o.usuario_id,
    o.numero_pedido,
    o.dia_semana,
    o.hora_pedido,
    op.producto_id,
    op.orden_agregado_carrito,
    op.recompra,
    p.nombre_producto,
    p.departamento

FROM orders AS o

INNER JOIN order_products AS op
    ON o.pedido_id = op.pedido_id

INNER JOIN products AS p
    ON op.producto_id = p.producto_id