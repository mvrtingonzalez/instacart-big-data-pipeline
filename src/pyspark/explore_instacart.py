
import os

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, expr, count, avg, round, countDistinct

# Ruta absoluta para almacenar el Spark Warehouse
warehouse_location = os.path.abspath("spark-warehouse")


# ==========================================
# 1. INICIALIZACIÓN DE SPARK
# ==========================================

# Creación de la sesión de Spark y configuración de recursos
spark = SparkSession.builder \
    .appName("Instacart Big Data Pipeline") \
    .config("spark.driver.memory", "4g") \
    .config("spark.sql.shuffle.partitions", "400") \
    .config("spark.sql.adaptive.enabled", "true") \
    .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
    .config("spark.sql.adaptive.advisoryPartitionSizeInBytes", "64m") \
    .config("spark.sql.autoBroadcastJoinThreshold", "-1") \
    .config("spark.sql.warehouse.dir", warehouse_location) \
    .getOrCreate()

# Reducir la cantidad de mensajes informativos de Spark en consola
spark.sparkContext.setLogLevel("WARN")

print("Spark iniciado correctamente", spark.version)

# ==========================================
# 2. INGESTA DE DATOS (LECTURA DE CSVs)
# ==========================================

# Lectura de los archivos CSV del dataset Instacart
# header=True: utiliza la primera fila como nombres de columnas
# inferSchema=True: permite a Spark inferir automáticamente los tipos de datos

df_orders = spark.read.csv("data/raw/orders.csv", header=True, inferSchema=True)
df_products = spark.read.csv("data/raw/products.csv", header=True, inferSchema=True)
df_order_products_train = spark.read.csv( "data/raw/order_products__train.csv", header=True, inferSchema=True)
df_order_products_prior = spark.read.csv( "data/raw/order_products__prior.csv", header=True, inferSchema=True)
df_departments = spark.read.csv("data/raw/departments.csv", header=True, inferSchema=True)
df_aisles = spark.read.csv( "data/raw/aisles.csv", header=True, inferSchema=True)

# ==========================================
# 3. VALIDACIÓN DE CALIDAD DE DATOS (NULOS)
# ==========================================

# Identificación de valores nulos en las columnas clave
# Esto permite comprobar la calidad de los datos antes de procesarlos

print("-" * 50)
print("AUDITORÍA DE NULOS EN LLAVES CLAVE:")

print("Nulos en order_id (orders): ", df_orders.filter(col("order_id").isNull()).count())
print("Nulos en user_id (orders): ", df_orders.filter(col("user_id").isNull()).count())
print("Nulos en product_id (products): ", df_products.filter(col("product_id").isNull()).count())
print("Nulos en order_id (prior): ", df_order_products_prior.filter(col("order_id").isNull()).count())
print("Nulos en product_id (prior): ", df_order_products_prior.filter(col("product_id").isNull()).count())
print("Nulos en department_id (departments): ", df_departments.filter(col("department_id").isNull()).count())
print("Nulos en aisle_id (aisles): ", df_aisles.filter(col("aisle_id").isNull()).count())
print("Nulos en order_id (train): ", df_order_products_train.filter(col("order_id").isNull()).count())
print("Nulos en product_id (train): ", df_order_products_train.filter(col("product_id").isNull()).count())

# ==========================================
# 4. LIMPIEZA Y TRANSFORMACIÓN DE TIPOS DE DATOS
# ==========================================

# Conversión de columnas identificadoras a tipo entero (INT)
# try_cast permite convertir valores válidos y devuelve NULL
# cuando encuentra valores que no pueden convertirse

df_products_clean = df_products \
    .withColumn("aisle_id", expr("try_cast(aisle_id as int)")) \
    .withColumn("department_id", expr("try_cast(department_id as int)")) \
    .withColumn("product_id", expr("try_cast(product_id as int)"))

# Conversión del identificador de pasillo
df_aisles_clean = df_aisles \
    .withColumn("aisle_id", expr("try_cast(aisle_id as int)"))

# Conversión del identificador de departamento
df_departments_clean = df_departments \
    .withColumn("department_id", expr("try_cast(department_id as int)"))

# ==========================================
# 5. ENRIQUECIMIENTO DE LA DIMENSIÓN DE PRODUCTOS
# ==========================================

# Unión de productos con sus respectivos pasillos y departamentos
# LEFT JOIN permite conservar todos los productos de la tabla principal,
# incluso cuando no existe una coincidencia en las tablas relacionadas

df_products_enriched = df_products_clean \
    .join(df_aisles_clean, "aisle_id", "left") \
    .join(df_departments_clean, "department_id", "left")

# Visualización de los primeros cinco productos enriquecidos
print("-" * 50)
print("Muestra de productos enriquecidos:")

df_products_enriched.show(5, truncate=False)

# Conteo total de productos después de realizar los JOIN
print("Total de productos enriquecidos: ", df_products_enriched.count())

# ==========================================
# 6. JOIN DE PEDIDOS Y PRODUCTOS PRIOR
# ==========================================

# Unión de los pedidos con el historial de productos comprados
# INNER JOIN conserva únicamente los registros que tienen coincidencias
# entre ambas tablas utilizando order_id

df_orders_prior_joined = df_orders \
    .join(df_order_products_prior, "order_id", "inner")

# Visualización de los primeros cinco registros combinados
print("-" * 50)
print("Muestra de pedidos con su historial cruzado:")

df_orders_prior_joined.show(5, truncate=False)

# Conteo de registros resultantes después del JOIN
print("Total de registros en el dataset combinado (orders + prior):",df_orders_prior_joined.count())

# ==========================================
# 7. CONSTRUCCIÓN DE LA TABLA MAESTRA
# ==========================================

# Unión del historial de pedidos con la dimensión de productos enriquecida
# INNER JOIN utiliza product_id para relacionar las compras con
# la información descriptiva de cada producto

df_master_pipeline = df_orders_prior_joined \
    .join(df_products_enriched, "product_id", "inner")

print("-" * 50)
print("Tabla maestra construida correctamente")

# ==========================================
# 8. PERSISTENCIA EN CAPA PROCESADA (PARQUET)
# ==========================================

# Escritura de la tabla maestra en formato Parquet
# overwrite reemplaza los datos existentes en la ruta de destino
# partitionBy organiza físicamente los archivos según department_id
# Esto facilita consultas posteriores que filtren por departamento

print("Escribiendo la tabla maestra en formato Parquet...")

df_master_pipeline.write \
    .mode("overwrite") \
    .partitionBy("department_id") \
    .parquet("data/processed/master_instacart.parquet")

print(
    "¡Pipeline ETL ejecutado y guardado con éxito en data/processed/!"
)

# ==========================================
# 9. VALIDACIÓN DEL PARQUET GENERADO
# ==========================================

# Lectura de los datos procesados desde Parquet
# De esta manera comprobamos que los datos fueron almacenados correctamente

df_master_pipeline = spark.read.parquet(
    "data/processed/master_instacart.parquet"
)

# Visualización de los primeros cinco registros del resultado procesado
print("-" * 50)
print("Muestra del Pipeline Maestro Completo:")

df_master_pipeline.show(5, truncate=False)

# Conteo total de registros almacenados en Parquet
print(
    "Total de registros en la tabla maestra:",
    df_master_pipeline.count()
)

# ==========================================
# 10. AGREGACIONES CLAVE DEL NEGOCIO
# ==========================================

# Análisis del comportamiento de compra de los usuarios
# Se agrupan los registros por user_id para calcular indicadores
# relacionados con la frecuencia y el volumen de compras

print("-" * 50)
print("EJECUTANDO AGREGACIONES CLAVE DEL NEGOCIO:")

# Cálculo de indicadores por usuario:
# countDistinct: cantidad de pedidos únicos realizados por el usuario
# count: cantidad total de productos asociados a sus pedidos
# avg: promedio de días transcurridos entre sus pedidos

df_agregaciones = df_master_pipeline.groupBy("user_id").agg(
    countDistinct("order_id").alias("total_pedidos_unicos"),
    count("product_id").alias("total_productos_comprados"),
    avg("days_since_prior_order").alias("promedios_dias_entre_pedidos")
).orderBy(
    col("total_pedidos_unicos").desc()
)

# Mostrar los diez usuarios con mayor cantidad de pedidos únicos
df_agregaciones.show(10, truncate=False)

df_agregaciones2 = df_master_pipeline.groupBy("department").agg(
    count("product_id").alias("productos_comprados"),
    round(avg("reordered") * 100, 2).alias("porcentaje_promedio_reorden")
).orderBy(col("productos_comprados").desc())

df_agregaciones2.show(10, truncate=False)

# ==========================================
# 11. CIERRE DE SPARK
# ==========================================

# Finalización de la sesión para liberar los recursos utilizados
spark.stop()
print("Pipeline finalizado correctamente")
