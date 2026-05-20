# DuasMeninas Collect

Pipeline ETL para coleta, transformação e carga de dados do frigorífico Duas Meninas. Extrai dados de uma planilha Google Sheets, aplica regras de negócio e carrega o resultado em um banco PostgreSQL — podendo ser executado manualmente ou agendado via Apache Airflow.

---

## Arquitetura

```
Google Sheets (xlsx)
        │
        ▼
  [Extract]  collector.conectar_dados()
        │
        ▼
[Transform]  collector.tratamento_dados()
             collector.tratamento_clientes()
        │
        ▼
   [Load]    collector.carregar_dados()
        │
        ▼
PostgreSQL (tbfatos + tbclientes)
```

### Estrutura de arquivos

```
DuasMeninas_collect/
├── main.py                  # Ponto de entrada para execução manual
├── pyproject.toml           # Metadados e dependências do projeto
├── .env                     # Variáveis de ambiente (credenciais)
│
├── config/
│   └── conectDB.py          # Conexão com o banco de dados
│
├── src/
│   └── collector.py         # Classe Collector — lógica ETL principal
│
├── dags/
│   └── dag_duasmeninas.py   # DAG do Apache Airflow (agendamento diário)
│
└── sql/
    ├── tb_fatos.sql         # Script de criação da tabela de fatos
    └── tb_cliente.sql       # Script de criação da tabela de clientes
```

---

## Pré-requisitos

- Python >= 3.14
- PostgreSQL acessível na rede
- (Opcional) Apache Airflow para execução agendada

---

## Instalação

1. Clone o repositório:

```bash
git clone <url-do-repositorio>
cd DuasMeninas_collect
```

2. Crie e ative um ambiente virtual:

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate
```

3. Instale as dependências:

```bash
pip install -e .
```

> Alternativamente: `pip install pandas openpyxl psycopg2-binary python-dotenv`

---

## Configuração

Crie um arquivo `.env` na raiz do projeto com as variáveis abaixo:

```env
DB_HOST=<host-do-banco>
DB_NAME=<nome-do-banco>
DB_USER=<usuario>
DB_PASSWORD=<senha>
DB_PORT=5432
LINK_CONNECTION=<url-publica-da-planilha-google-sheets>
```

**Como obter o `LINK_CONNECTION`:** no Google Sheets, vá em **Arquivo → Compartilhar → Publicar na web**, selecione o formato **Microsoft Excel (.xlsx)** e copie o link gerado.

---

## Banco de dados

Antes da primeira execução, crie as tabelas no PostgreSQL:

```bash
psql -h <host> -U <usuario> -d <banco> -f sql/tb_fatos.sql
psql -h <host> -U <usuario> -d <banco> -f sql/tb_cliente.sql
```

---

## Execução

### Manual

```bash
python main.py
```

O pipeline irá:
1. Conectar ao banco de dados
2. Baixar a planilha do Google Sheets
3. Filtrar registros com `Check == 3`
4. Renomear e selecionar as colunas relevantes
5. Extrair clientes únicos
6. Truncar as tabelas `tbfatos` e `tbclientes`
7. Carregar os dados transformados

### Agendado via Apache Airflow

Copie o arquivo da DAG para o diretório de DAGs do Airflow:

```bash
cp dags/dag_duasmeninas.py $AIRFLOW_HOME/dags/
```

A DAG `etl_frigorifico` será detectada automaticamente e executará diariamente (`@daily`), a partir de 01/01/2025.

Para acionar manualmente pelo Airflow:

```bash
airflow dags trigger etl_frigorifico
```

---

## Modelo de dados

### `tbfatos` — Tabela de fatos (transações)

| Coluna        | Tipo    | Descrição                  |
|---------------|---------|----------------------------|
| status        | TEXT    | Status do registro         |
| codterceiros  | TEXT    | Código de terceiros        |
| nomfor        | TEXT    | Nome do fornecedor         |
| nomcli        | TEXT    | Nome do cliente            |
| codcli        | TEXT    | Código do cliente          |
| datemi        | DATE    | Data de emissão            |
| receita       | NUMERIC | Receita bruta              |
| custovendas   | NUMERIC | Custo de vendas            |
| pmv           | NUMERIC | Preço médio de venda       |
| mc            | NUMERIC | Margem de contribuição     |
| codtipo       | TEXT    | Código do tipo             |
| miudos        | NUMERIC | Valor de miúdos            |
| mccommiudo    | NUMERIC | MC com miúdo               |
| boi           | NUMERIC | Quantidade de boi          |

### `tbclientes` — Tabela de clientes

| Coluna  | Tipo | Descrição         |
|---------|------|-------------------|
| codcli  | TEXT | Código do cliente |
| nomcli  | TEXT | Nome do cliente   |

---

## Dependências

| Pacote             | Versão mínima | Uso                              |
|--------------------|---------------|----------------------------------|
| pandas             | 3.0.3         | Manipulação e transformação de dados |
| openpyxl           | 3.1.5         | Leitura de arquivos Excel        |
| psycopg2-binary    | 2.9.12        | Conexão com PostgreSQL           |
| python-dotenv      | 1.2.2         | Carregamento de variáveis de ambiente |

---

## Observações

- A cada execução as tabelas são **truncadas** antes do carregamento — os dados anteriores são substituídos.
- O arquivo `.env` **não deve ser versionado**; certifique-se de que ele está no `.gitignore`.
- A planilha Google Sheets precisa estar **publicada na web** no formato xlsx para ser acessível sem autenticação.
