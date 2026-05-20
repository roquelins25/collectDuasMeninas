import sys
import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

import dotenv

dotenv.load_dotenv(PROJECT_ROOT / ".env")

from config.conectDB import connect_db
from src.collector import Collector


# ==========================================
# FUNÇÃO PRINCIPAL
# ==========================================
def executar_etl():

    url = os.getenv("LINK_CONNECTION")

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
        str(PROJECT_ROOT / "sql" / "tb_fatos.sql")
    )

    # load clientes
    collector.carregar_dados(
        df_clientes,
        "tbclientes",
        str(PROJECT_ROOT / "sql" / "tb_cliente.sql")
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