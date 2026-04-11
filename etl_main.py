import sqlite3
from time import sleep
#from conn_sqlsqerver import SQLServerConnection
#from conn_postgres import PostgresConnection

#from create_table_stating import CreateTablesStaging
from sqlite.create_table_staging_sqlite import CreateTablesStagingSqlite
from insert_sqlite import InsertSqlite



# #  CONEXÃO COM BANCO DE DADOS  # #

#sqlserver_conn = SQLServerConnection(
#    server="127.0.0.1,1433",
#    database="AdventureWorks2022",
#    username="sa",
#    password="SuaSenhaForte123!"
#)
#sqlserver_conn.connect()

# Usar para executar consultas e operações no banco de dados SQL Server
#cursor_sqlserver = sqlserver_conn.cursor()

#conn_postgres = PostgresConnection(
#    host="localhost",
#    port=5432,
#    database="adventureworks",
#    user="postgres",
#    password="postgres"
#)
#conn_postgres.connect()

# Usar para executar consultas e operações no banco de dados PostgreSQL
#cursor_postgres = conn_postgres.cursor()

# OLTP - Online Transaction Processing
conn_oltp = sqlite3.connect('AdventureWorks.db')
cursor_oltp = conn_oltp.cursor()

# OLAP - Online Analytical Processing
conn_olap = sqlite3.connect('StagingAdventureWorks.db')
cursor_olap = conn_olap.cursor()



# #  CRIAR AS TABELAS DE STAGING  # #

#criar_tabelas_staging = CreateTablesStaging(cursor_postgres)

criar_tabelas_staging_sqlite = CreateTablesStagingSqlite(cursor_olap)
criar_tabelas_staging_sqlite.create_tables()


# # #  VERIFICAR DADOS NOVOS E PROCESSAR O ETL COM SQLITE  # #

def verificar_dados_novos():
    print("Verificando dados novos...")

    # 1ª etapa: verificar a última data de execução do processo de ETL no controle de ETL
    cursor_olap.execute("""SELECT ultima_execucao FROM controle_etl WHERE processo = 'SalesOrderHeader';""")
    ultima_execucao = cursor_olap.fetchone()[0]

    # 2ª etapa: verificar a última data de modificação na tabela SalesOrderHeader do banco OLTP
    cursor_oltp.execute("""SELECT MAX(ModifiedDate) AS MaxModifiedDate FROM SalesOrderHeader;""")
    max_modified_date = cursor_oltp.fetchone()[0]

    # 3ª etapa: comparar as datas para determinar se há dados novos a serem processados
    if max_modified_date > ultima_execucao:
        print("Dados novos encontrados. Iniciando processo de ETL...")
        # SE A CONSULTA DIZER QUE EXISTE DADOS NOVOS, ENTÃO É FEITO O PROCESSO DE ETL PARA A TABELA SalesOrderHeader
        # SELECT incremental
        cursor_oltp.execute(f"""
        SELECT *
        FROM SalesOrderHeader
        WHERE ModifiedDate > '{ultima_execucao}'
        """)

        rows = cursor_oltp.fetchall()

        # SE A CONSULTA DIZER TRUE PARA DADOS NOVOS, ENTÃO É FEITO O PROCESSO DE ETL PARA A TABELA SalesOrderHeader
        
        inserir_dados_sqlite = InsertSqlite(conn_olap, cursor_olap)
        inserir_dados_sqlite.inserir_dados_salesorderheader(rows)

        #cursor_olap.executemany("""
        #INSERT OR REPLACE INTO SalesOrderHeader (
        #    SalesOrderID,
        #    OrderDate,
        #    ShipDate,
        #    CustomerID,
        #    SalesPersonID,
        #    TerritoryID,
        #    SubTotal,
        #    ModifiedDate
        #) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        #""", rows)
        #conn_olap.commit()
        
        # ATUALIZAR A DATA DE ÚLTIMA EXECUÇÃO NO CONTROLE DE ETL
        if rows:
            max_data = max(row[7] for row in rows)

            cursor_olap.execute("""
            UPDATE controle_etl
            SET ultima_execucao = ?
            WHERE processo = 'SalesOrderHeader'
            """, (max_data,))

            conn_olap.commit()

            print(f"{len(rows)} registros processados")
        else:
            print("Nenhum dado novo")









# Mantendo a aplicação ligada
while True:
    verificar_dados_novos()
    sleep(30)  # Espera por 30 segundos antes de verificar novamente
    
