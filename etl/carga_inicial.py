from utils import conn_olap, cursor_olap, cursor_oltp
from staging.insert_table_staging import InsertTableStaging

from staging.create_table_staging import CreateTablesStaging
from dw.ddl_tabelas_star import CreateTablesDW



# #  CRIAR AS TABELAS DE STAGING  # #
criar_tabelas_staging = CreateTablesStaging(cursor_olap, conn_olap)
criar_tabelas_staging.create_tables()



# # CRIAR AS TABELAS DO DW  # #
criar_tabelas_dw = CreateTablesDW(cursor_olap, conn_olap)
criar_tabelas_dw.create_tables_dw()




def inicializar_controle_etl(cursor, conn, schema, processos):
    """
    # Carga inicial de controle  
    Essa função faz a carga inicial nas tabelas que controlam o ETL:  
    Tabelas controle_etl do postgres para ter uma data inicial  
    assim podendo comprar a data mais recente
    """
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
    """
    # Carga inicial para tabelas de dados
    Essa função faz um `SELECT *` para todas as tabelas declaradas em `processos`  
    e assim passando tudo para as tabelas dos `schemas`
    """
    print(f"Executando carga inicial para {schema}...")

    carga_func()

    inicializar_controle_etl(cursor_olap, conn_olap, schema, processos)

    cursor_olap.execute(f"""
        UPDATE {schema}.controle_carga
        SET carga_inicial = TRUE
    """)

    conn_olap.connection.commit()




def verificar_carga_inicial(schema):
    """
    # Verificar o controle de carga  
    Conta os registros nas tabelas de controle de carga  
    return True = tem dados  
    return False = não tem dados
    """
    cursor_olap.execute(f"""
        SELECT COALESCE(BOOL_OR(carga_inicial), FALSE)
        FROM {schema}.controle_carga;
    """)

    result = cursor_olap.fetchone()
    return result[0] if result else False




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
        INSERT INTO dw.DimTempo (
            IdData,
            Data,
            AnoMes,
            Ano,
            Mes,
            NomeMes,
            Trimestre
        )
        SELECT DISTINCT
            TO_CHAR(OrderDate,'YYYYMMDD')::INT,
            OrderDate::DATE,
            TO_CHAR(OrderDate,'YYYYMM')::INT,
            EXTRACT(YEAR FROM OrderDate)::INT,
            EXTRACT(MONTH FROM OrderDate)::INT,
            TO_CHAR(OrderDate,'TMMonth'),
            EXTRACT(QUARTER FROM OrderDate)::INT
        FROM staging.SalesOrderHeader
        WHERE OrderDate IS NOT NULL
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
