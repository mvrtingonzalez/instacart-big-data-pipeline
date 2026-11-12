--Modelo staging: relación entre pedidos y productos
--Obitene los productos asociados a cada pedido desde la tabla maestra
--Utiliza distict para conservar combinaciones únicas de sus columnas

SELECT DISTINCT
    order_id AS pedido_id,
    product_id AS producto_id,
    add_to_cart_order AS orden_agregado_carrito,
    reordered AS recompra

FROM {{ source('instacart', 'master_instacart') }}