import sqlite3
from time import sleep
from utils.conn_sqlsqerver import SQLServerConnection
from utils.conn_postgres import PostgresConnection
from datetime import datetime
from staging.create_table_staging import CreateTablesStaging
from staging.insert_table_staging import InsertTableStaging
import os
from utils.processos import processos
from dotenv import load_dotenv
load_dotenv()



# #  CONEXÃO COM BANCO DE DADOS  # #

#sqlserver_conn = SQLServerConnection(
conn_oltp = SQLServerConnection(
    server=os.getenv("SERVER"),
    database=os.getenv("DATABASE_OLTP"),
    username=os.getenv("USERNAME_OLTP"),
    password=os.getenv("PASSWORD_OLTP")
)
#sqlserver_conn.connect()
conn_oltp.connect()

# Usar para executar consultas e operações no banco de dados SQL Server
#cursor_sqlserver = sqlserver_conn.cursor()
cursor_oltp = conn_oltp.cursor()

#conn_postgres = PostgresConnection(
conn_olap = PostgresConnection(
    host=os.getenv("HOST"),
    port=os.getenv("PORT"),
    database=os.getenv("DATABASE_OLAP"),
    user=os.getenv("USERNAME_OLAP"),
    password=os.getenv("PASSWORD_OLAP")
)
#conn_postgres.connect()
conn_olap.connect()

# Usar para executar consultas e operações no banco de dados PostgreSQL
#cursor_postgres = conn_postgres.cursor()

# OLTP - Online Transaction Processing
#conn_oltp = sqlite3.connect('AdventureWorks.db')

# OLAP - Online Analytical Processing
#conn_olap = sqlite3.connect('StagingAdventureWorks.db')
cursor_olap = conn_olap.cursor()



# #  CRIAR AS TABELAS DE STAGING  # #

#criar_tabelas_staging = CreateTablesStaging(cursor_postgres)

#criar_tabelas_staging_sqlite = CreateTablesStagingSqlite(cursor_olap)
#criar_tabelas_staging_sqlite.create_tables()
criar_tabelas_staging = CreateTablesStaging(cursor_olap, conn_olap)
criar_tabelas_staging.create_tables()


# # #  VERIFICAR DADOS NOVOS E PROCESSAR O ETL COM SQLITE  # #
def verificar_carga_inicial():
    cursor_olap.execute("""
        SELECT carga_inicial FROM staging.controle_carga
    """)
    
    result = cursor_olap.fetchone()

    if not result or result[0] == False:
        return False
    
    return True


def carga_inicial_staging():
    insert = InsertTableStaging(cursor_olap, conn_olap)
    print("Rodando carga inicial...")
    
    # Territory
    cursor_oltp.execute("SELECT TerritoryID, Name, CountryRegionCode, [Group], ModifiedDate FROM Sales.SalesTerritory")
    rows = cursor_oltp.fetchall()

    insert.insert_salesTerritory(rows)

    # Product
    cursor_oltp.execute("SELECT ProductID, Name, StandardCost, ListPrice, ModifiedDate FROM Production.Product")
    rows = cursor_oltp.fetchall()
    insert.insert_product(rows)

    # SalesPerson
    cursor_oltp.execute(" SELECT BusinessEntityID, TerritoryID, SalesQuota, Bonus, CommissionPct, ModifiedDate FROM Sales.SalesPerson ")
    rows = cursor_oltp.fetchall()
    insert.insert_salesperson(rows)

    # SalesOrderHeader
    cursor_oltp.execute("SELECT SalesOrderID, OrderDate, ShipDate, CustomerID, SalesPersonID, TerritoryID, SubTotal, ModifiedDate FROM Sales.SalesOrderHeader")
    rows = cursor_oltp.fetchall()
    insert.insert_salesorderheader(rows)

    # SalesOrderDetail
    cursor_oltp.execute(" SELECT SalesOrderID, ProductID, OrderQty, UnitPrice, LineTotal, ModifiedDate FROM Sales.SalesOrderDetail")
    rows = cursor_oltp.fetchall()
    insert.insert_salesorderdetail(rows)


carga_inicial_staging()

def verificar_dados_novos():

    print("Verificando dados novos...")

    # buscar controle
    cursor_olap.execute("""
        SELECT processo, ultima_execucao 
        FROM staging.controle_etl;
    """)

    controle = {row[0]: row[1] for row in cursor_olap.fetchall()}

    load_staging = InsertTableStaging(cursor_olap, conn_olap)

    for processo, config in processos.items():

        ultima_execucao = controle.get(processo, datetime(1900, 1, 1))

        # pegar última modificação
        cursor_oltp.execute(config["query_max"])
        max_modified = cursor_oltp.fetchone()[0]

        if not max_modified or max_modified <= ultima_execucao:
            print(f"{processo}: sem atualização")
            continue

        print(f"{processo}: atualizado, executando ETL...")

        # extract
        cursor_oltp.execute(config["query_incremental"], (ultima_execucao,))
        rows = cursor_oltp.fetchall()

        if not rows:
            continue

        # load dinâmico
        getattr(load_staging, config["load_function"])(rows)

        # atualizar controle
        max_data = max(row[config["coluna_data_index"]] for row in rows)

        cursor_olap.execute("""
            UPDATE staging.controle_etl
            SET ultima_execucao = %s
            WHERE processo = %s
        """, (max_data, processo))

        conn_olap.connection.commit()

        print(f"{processo}: {len(rows)} registros processados")


if not verificar_carga_inicial():
    print("Executando carga inicial...")
    carga_inicial_staging()
    
    # dados iniciais para controle do processo ETL
    cursor_olap.execute("""
        INSERT INTO staging.controle_etl (processo, ultima_execucao)
        VALUES 
        ('Product', '1900-01-01'),
        ('SalesPerson', '1900-01-01'),
        ('SalesTerritory', '1900-01-01'),
        ('SalesOrderHeader', '1900-01-01'),
        ('SalesOrderDetail', '1900-01-01')
        ON CONFLICT (processo) DO NOTHING;""")
    conn_olap.connection.commit()

    cursor_olap.execute("""
        UPDATE staging.controle_carga
        SET carga_inicial = TRUE
    """)
    conn_olap.connection.commit()


else:
    print("Carga inicial já realizada. Rodando incremental...")
    verificar_dados_novos()

# Mantendo a aplicação ligada
while True:
    verificar_dados_novos()
    sleep(30)  # Espera por 30 segundos antes de verificar novamente
    
