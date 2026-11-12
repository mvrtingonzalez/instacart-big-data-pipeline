from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("Validate Instacart Parquet") \
    .getOrCreate()

df = spark.read.parquet(
    "data/processed/master_instacart.parquet"
)

print("Muestra de datos:")
df.show(5)

print("Cantidad de registros:", df.count())

print("Esquema:")
df.printSchema()

spark.stop()