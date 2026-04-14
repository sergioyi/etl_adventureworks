from time import sleep
from utils.conn_sqlsqerver import SQLServerConnection
from utils.conn_postgres import PostgresConnection
from datetime import datetime

from staging.create_table_staging import CreateTablesStaging
from staging.insert_table_staging import InsertTableStaging
from dw.ddl_tabelas_star import CreateTablesDW

from utils.processos import processos
from utils.processos_dw import processos_dw
import os
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

cursor_olap = conn_olap.cursor()



# #  CRIAR AS TABELAS DE STAGING  # #

criar_tabelas_staging = CreateTablesStaging(cursor_olap, conn_olap)
criar_tabelas_staging.create_tables()



# # CRIAR AS TABELAS DO DW  # #
criar_tabelas_dw = CreateTablesDW(cursor_olap, conn_olap)
criar_tabelas_dw.create_tables_dw()



def verificar_carga_inicial(schema):
    cursor_olap.execute(f"""
        SELECT COALESCE(BOOL_OR(carga_inicial), FALSE)
        FROM {schema}.controle_carga;
    """)

    result = cursor_olap.fetchone()
    return result[0] if result else False

def garantir_tabelas_controle(schema):
    cursor_olap.execute(f"""
        CREATE TABLE IF NOT EXISTS {schema}.controle_carga (
            carga_inicial BOOLEAN
        );
    """)

    cursor_olap.execute(f"""
        CREATE TABLE IF NOT EXISTS {schema}.controle_etl (
            processo VARCHAR(100) PRIMARY KEY,
            ultima_execucao TIMESTAMP
        );
    """)

    # Garante pelo menos 1 linha
    cursor_olap.execute(f"""
        INSERT INTO {schema}.controle_carga (carga_inicial)
        SELECT FALSE
        WHERE NOT EXISTS (
            SELECT 1 FROM {schema}.controle_carga
        );
    """)

    conn_olap.connection.commit()

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


def carga_inicial_dw():
    print("Rodando carga inicial DW...")

    # =========================
    # DIMENSÕES
    # =========================

    # 🟢 DimRegiao
    cursor_olap.execute("""
        INSERT INTO dw.DimRegiao (IdRegiao, NomeRegiao, Pais, Grupo)
        SELECT 
            TerritoryID,
            Name,
            CountryRegionCode,
            "Group"
        FROM staging.SalesTerritory
        ON CONFLICT (IdRegiao) DO NOTHING;
    """)

    # 🟢 DimProduto
    cursor_olap.execute("""
        INSERT INTO dw.DimProduto (IdProduto, Nome, Preco, Custo)
        SELECT 
            ProductID,
            Name,
            ListPrice,
            StandardCost
        FROM staging.Product
        ON CONFLICT (IdProduto) DO NOTHING;
    """)

    # 🟢 DimVendedor
    cursor_olap.execute("""
        INSERT INTO dw.DimVendedor (IdVendedor, Meta)
        SELECT 
            BusinessEntityID,
            SalesQuota
        FROM staging.SalesPerson
        ON CONFLICT (IdVendedor) DO NOTHING;
    """)

    # 🟢 DimCliente (simples - pode melhorar depois)
    cursor_olap.execute("""
        INSERT INTO dw.DimCliente (IdCliente, TipoCliente)
        SELECT DISTINCT
            CustomerID,
            'Regular'
        FROM staging.SalesOrderHeader
        ON CONFLICT (IdCliente) DO NOTHING;
    """)

    # 🟢 DimTempo
    cursor_olap.execute("""
        INSERT INTO dw.DimTempo (IdData, Data, Ano, Mes, NomeMes, Trimestre)
        SELECT DISTINCT
            CAST(TO_CHAR(OrderDate, 'YYYYMMDD') AS INT),
            OrderDate,
            EXTRACT(YEAR FROM OrderDate),
            EXTRACT(MONTH FROM OrderDate),
            TO_CHAR(OrderDate, 'Month'),
            EXTRACT(QUARTER FROM OrderDate)
        FROM staging.SalesOrderHeader
        ON CONFLICT (IdData) DO NOTHING;
    """)

    conn_olap.connection.commit()

    # =========================
    # FATO
    # =========================

    cursor_olap.execute("""
        INSERT INTO dw.FatoVendas (
            IdPedido,
            IdProduto,
            IdCliente,
            IdVendedor,
            IdRegiao,
            IdData,
            DataEnvio,
            Quantidade,
            PrecoUnitario,
            Receita,
            Custo,
            Lucro
        )
        SELECT
            sod.SalesOrderID,
            sod.ProductID,
            soh.CustomerID,
            soh.SalesPersonID,
            soh.TerritoryID,
            CAST(TO_CHAR(soh.OrderDate, 'YYYYMMDD') AS INT),
            soh.ShipDate,
            sod.OrderQty,
            sod.UnitPrice,
            sod.LineTotal,
            (sod.OrderQty * p.StandardCost),
            (sod.LineTotal - (sod.OrderQty * p.StandardCost))
        FROM staging.SalesOrderDetail sod
        JOIN staging.SalesOrderHeader soh 
            ON sod.SalesOrderID = soh.SalesOrderID
        JOIN staging.Product p 
            ON sod.ProductID = p.ProductID
        ON CONFLICT (IdPedido, IdProduto) DO NOTHING;
    """)

    conn_olap.connection.commit()

    print("Carga inicial DW finalizada com sucesso!")

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


from dw.insert_dw import InsertDW
from utils.processos_dw import processos_dw

def verificar_dados_novos_dw():
    print("Verificando dados novos DW...")

    cursor_olap.execute("""
        SELECT processo, ultima_execucao 
        FROM dw.controle_etl;
    """)

    controle = {row[0]: row[1] for row in cursor_olap.fetchall()}

    load_dw = InsertDW(cursor_olap, conn_olap)

    for processo, config in processos_dw.items():

        ultima_execucao = controle.get(processo, datetime(1900, 1, 1))

        # pega última data do staging
        cursor_olap.execute(config["query_max"])
        max_data = cursor_olap.fetchone()[0]

        if not max_data or max_data <= ultima_execucao:
            print(f"{processo}: sem atualização")
            continue

        print(f"{processo}: atualizando DW...")

        # executa carga
        getattr(load_dw, config["load_function"])()

        # atualiza controle
        cursor_olap.execute("""
            UPDATE dw.controle_etl
            SET ultima_execucao = %s
            WHERE processo = %s
        """, (max_data, processo))

        conn_olap.connection.commit()


def inicializar_controle_etl(cursor, conn, schema, processos):
    print(f"Inicializando controle ETL para schema: {schema}")

    valores = [
        (processo, '1900-01-01')
        for processo in processos.keys()
    ]

    cursor.executemany(f"""
        INSERT INTO {schema}.controle_etl (processo, ultima_execucao)
        VALUES (%s, %s)
        ON CONFLICT (processo) DO NOTHING;
    """, valores)

    conn.connection.commit()



PROCESSOS_STAGING = {
    "Product": {},
    "SalesPerson": {},
    "SalesTerritory": {},
    "SalesOrderHeader": {},
    "SalesOrderDetail": {}
}

def inicializar_controle_etl(cursor, conn, schema, processos):
    print(f"Inicializando controle ETL para schema: {schema}")

    valores = [
        (processo, '1900-01-01')
        for processo in processos.keys()
    ]

    cursor.executemany(f"""
        INSERT INTO {schema}.controle_etl (processo, ultima_execucao)
        VALUES (%s, %s)
        ON CONFLICT (processo) DO NOTHING;
    """, valores)

    conn.connection.commit()


def executar_carga_inicial(schema, carga_func, processos):
    print(f"Executando carga inicial para {schema}...")

    carga_func()

    inicializar_controle_etl(cursor_olap, conn_olap, schema, processos)

    cursor_olap.execute(f"""
        UPDATE {schema}.controle_carga
        SET carga_inicial = TRUE
    """)

    conn_olap.connection.commit()

if not verificar_carga_inicial("staging"):
    executar_carga_inicial(
        schema="staging",
        carga_func=carga_inicial_staging,
        processos=PROCESSOS_STAGING
    )

PROCESSOS_DW = {
    "DimProduto": {},
    "DimCliente": {},
    "DimTempo": {},
    "DimVendedor": {},
    "FatoVendas": {}
}


if not verificar_carga_inicial("dw"):
    executar_carga_inicial(
        schema="dw",
        carga_func=carga_inicial_dw,
        processos=PROCESSOS_DW
    )

# Mantendo a aplicação ligada
while True:
    verificar_dados_novos()      # STAGING
    verificar_dados_novos_dw()   # DW
    sleep(30)