-- Modelo staging: información de los pedidos.
-- Obtiene los datos de cada pedido desde la tabla maestra.
-- Utiliza DISTINCT para conservar registros únicos según las columnas seleccionadas.

SELECT DISTINCT
    order_id AS pedido_id,
    user_id AS usuario_id,
    eval_set AS conjunto_evaluacion,
    order_number AS numero_pedido,
    order_dow AS dia_semana,
    order_hour_of_day AS hora_pedido,
    days_since_prior_order AS dias_desde_pedido_anterior

FROM {{ source('instacart', 'master_instacart') }}