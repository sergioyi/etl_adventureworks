# Essa classe é para aramazer as funções de inserção de dados no banco de dados SQLite, que é o banco de dados staging utilizado para o processo de ETL.
import sqlite3

class InsertSqlite:
    def __init__(self, conn, cursor):
        self.conn = conn
        self.cursor = cursor

    def inserir_dados_salesorderheader(self, dados):
        self.cursor.executemany("""
        INSERT OR REPLACE INTO SalesOrderHeader (
            SalesOrderID,
            OrderDate,
            ShipDate,
            CustomerID,
            SalesPersonID,
            TerritoryID,
            SubTotal,
            ModifiedDate
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, dados)
        self.conn.commit()