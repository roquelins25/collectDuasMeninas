from config.conectDB import connect_db
from src.collector import Collector
import os
import dotenv

dotenv.load_dotenv()

url = os.getenv("LINK_CONNECTION")

conn = connect_db()

collector = Collector(url, conn)

# conecta
print( "iniciando processo - Conectando Dados")
df = collector.conectar_dados()

# trata
df_tratado = collector.tratamento_dados(df)

# clientes
df_clientes = collector.tratamento_clientes(df_tratado)

# carrega
collector.carregar_dados(df_tratado, "tbfatos", 'sql/tb_fatos.sql' )

collector.carregar_dados(df_clientes, "tbclientes", 'sql/tb_cliente.sql')