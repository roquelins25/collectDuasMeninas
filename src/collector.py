import pandas as pd
import dotenv
import os

dotenv.load_dotenv()


class Collector:

    def __init__(self, url, conn):

        self.url = url
        self.conn = conn

    def conectar_dados(self):

        try:

            df = pd.read_excel(
                self.url,
                sheet_name='Dados',
                header=10
            )

            print("Dados conectados com sucesso.")

            return df

        except Exception as e:

            print(f"Erro ao conectar aos dados: {e}")

            return None

    def tratamento_dados(self, df):

        try:

            df_filtrado = df[df['Check'] == 3].copy()

            colunas_desejadas = [
                "Check", "Cód", "Unnamed: 4", "Fornecedor",
                "Cliente 1", "Cód Cliente 1",
                "Data Emissão NF", "Receita (R$)",
                "Custo sobre as Vendas (R$)",
                "PMV (R$/Kg)", "MC (R$)",
                "Cód.1", "Miúdos (R$)",
                "MC com Miúdo (R$)", "Boi"
            ]

            df = df_filtrado[colunas_desejadas]

            df = df.rename(columns={
                "Check": "status",
                "Cód": "codterceiros",
                "Unnamed: 4": "datacriacao",
                "Fornecedor": "nomfor",
                "Cliente 1": "nomcli",
                "Cód Cliente 1": "codcli",
                "Data Emissão NF": "datemi",
                "Receita (R$)": "receita",
                "Custo sobre as Vendas (R$)": "custovendas",
                "PMV (R$/Kg)": "pmv",
                "MC (R$)": "mc",
                "Cód.1": "codtipo",
                "Miúdos (R$)": "miudos",
                "MC com Miúdo (R$)": "mccommiudo",
                "Boi": "boi"
            })

            df['datacriacao'] = pd.to_datetime(df['datacriacao'], errors='coerce').dt.date
            df['datemi'] = pd.to_datetime(df['datemi'], errors='coerce').dt.date

            return df

        except Exception as e:

            print(f"Erro no tratamento: {e}")

            return None

    def tratamento_clientes(self, df):

        try:

            df_cliente = (
                df[['codcli', 'nomcli']]
                .drop_duplicates()
                .copy()
            )

            df_cliente.columns = ['codcli', 'nomcli']

            df_filtrado = df_cliente

            return df_cliente

        except Exception as e:

            print(f"Erro clientes: {e}")

            return None

    def executar_sql(self, cursor, arquivo_sql):

        with open(arquivo_sql, 'r', encoding='utf-8') as file:

            sql = file.read()

        cursor.execute(sql)
    

    def carregar_dados(self, df, tabela, arquivo_sql):

        df.columns = [c.lower() for c in df.columns]

        df = df.where(pd.notnull(df), None)

        cursor = self.conn.cursor()

        try:

            self.executar_sql(cursor, arquivo_sql)

            cursor.execute(f"TRUNCATE TABLE {tabela}")

            cols = ','.join(df.columns)

            placeholders = ','.join(['%s'] * len(df.columns))

            sql_insert = f"""
                INSERT INTO {tabela} ({cols})
                VALUES ({placeholders})
            """

            records = df.to_records(index=False).tolist()

            cursor.executemany(sql_insert, records)

            self.conn.commit()

            print(f"{len(df)} registros carregados em {tabela}")

        except Exception as e:

            self.conn.rollback()

            print(f"Erro: {e}")

        finally:

            cursor.close()