
import pyarrow.dataset as ds
import psycopg2
import pandas as pd
from io import StringIO
from getpass import getpass

# 1. Leer Parquet
dataset = ds.dataset(
    "data/processed/master_instacart.parquet",
    format="parquet",
    partitioning="hive"
)

# 2. Conectar a PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="instacart",
    user="instacart_user",
    password=getpass("Contraseña PostgreSQL: ")
)

cursor = conn.cursor()

# 3. Crear tabla
cursor.execute("""
CREATE TABLE IF NOT EXISTS master_instacart (
    product_id INTEGER,
    order_id INTEGER,
    user_id INTEGER,
    eval_set TEXT,
    order_number INTEGER,
    order_dow INTEGER,
    order_hour_of_day INTEGER,
    days_since_prior_order DOUBLE PRECISION,
    add_to_cart_order INTEGER,
    reordered INTEGER,
    aisle_id INTEGER,
    product_name TEXT,
    aisle TEXT,
    department TEXT,
    department_id INTEGER
);
""")

# Evitar duplicados si se vuelve a ejecutar
cursor.execute("TRUNCATE TABLE master_instacart")

# 4. Carga por lotes
scanner = dataset.scanner(batch_size=100000)

columns = [
    "product_id", "order_id", "user_id", "eval_set",
    "order_number", "order_dow", "order_hour_of_day",
    "days_since_prior_order", "add_to_cart_order",
    "reordered", "aisle_id", "product_name",
    "aisle", "department", "department_id"
]

copy_sql = """
COPY master_instacart (
    product_id, order_id, user_id, eval_set,
    order_number, order_dow, order_hour_of_day,
    days_since_prior_order, add_to_cart_order,
    reordered, aisle_id, product_name,
    aisle, department, department_id
)
FROM STDIN WITH (FORMAT CSV, NULL '\\N')
"""

total = 0

try:
    for batch in scanner.to_batches():
        df = batch.to_pandas()[columns]

        buffer = StringIO()
        df.to_csv(
            buffer,
            index=False,
            header=False,
            na_rep='\\N'
        )
        buffer.seek(0)

        cursor.copy_expert(copy_sql, buffer)

        total += len(df)
        print(f"Registros cargados: {total:,}")

    conn.commit()
    print("\nCarga completada correctamente.")

except Exception:
    conn.rollback()
    raise

finally:
    cursor.close()
    conn.close()
