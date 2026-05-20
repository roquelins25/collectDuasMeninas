FROM apache/airflow:2.10.4

RUN pip install --no-cache-dir \
    "pandas>=2.0.0" \
    "openpyxl>=3.1.5" \
    "psycopg2-binary>=2.9.12" \
    "python-dotenv>=1.2.2"
