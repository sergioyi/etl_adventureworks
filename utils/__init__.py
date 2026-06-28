from .conn_sqlsqerver import SQLServerConnection
from .conn_postgres import PostgresConnection

import os
from dotenv import load_dotenv
load_dotenv()

# #  CONEXÃO COM BANCO DE DADOS  # #

conn_oltp = SQLServerConnection(
    server=os.getenv("SERVER"),
    database=os.getenv("DATABASE_OLTP"),
    username=os.getenv("USERNAME_OLTP"),
    password=os.getenv("PASSWORD_OLTP")
)

conn_oltp.connect()
cursor_oltp = conn_oltp.cursor()



conn_olap = PostgresConnection(
    host=os.getenv("HOST"),
    port=os.getenv("PORT"),
    database=os.getenv("DATABASE_OLAP"),
    user=os.getenv("USERNAME_OLAP"),
    password=os.getenv("PASSWORD_OLAP")
)

conn_olap.connect()
cursor_olap = conn_olap.cursor()