from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

from config.conectDB import connect_db
from src.collector import Collector

import os
import dotenv

dotenv.load_dotenv()

url = os.getenv("LINK_CONNECTION")


# ==========================================
# FUNÇÃO PRINCIPAL
# ==========================================
def executar_etl():

    conn = connect_db()

    collector = Collector(url, conn)

    # extract
    df = collector.conectar_dados()

    # transform
    df_tratado = collector.tratamento_dados(df)

    # dimensão clientes
    df_clientes = collector.tratamento_clientes(df_tratado)

    # load fatos
    collector.carregar_dados(
        df_tratado,
        "tbfatos",
        "sql/tb_fatos.sql"
    )

    # load clientes
    collector.carregar_dados(
        df_clientes,
        "tbclientes",
        "sql/tb_cliente.sql"
    )


# ==========================================
# DAG
# ==========================================
with DAG(

    dag_id="etl_frigorifico",

    start_date=datetime(2025, 1, 1),

    schedule="@daily",

    catchup=False

) as dag:

    executar_pipeline = PythonOperator(

        task_id="executar_etl",

        python_callable=executar_etl

    )