# Faça desse código uma importação para o meu arquivo principal para criar as tabelas no banco de dados PostgreSQL
# ele vai recerber o cursor do banco de dados PostgreSQL para criar as tabelas de staging
import sqlite3

class CreateTablesStagingSqlite:
    def __init__(self, cursor):
        self.cursor = cursor

    def create_tables(self):
        self.cursor.execute("""
          CREATE TABLE IF NOT EXISTS SalesTerritory (
            TerritoryID INTEGER PRIMARY KEY,
            Name TEXT,
            CountryRegionCode TEXT,
            "Group" TEXT
        );
          """)
        self.cursor.execute("""
         CREATE TABLE IF NOT EXISTS SalesPerson (
            BusinessEntityID INTEGER PRIMARY KEY,
            TerritoryID INTEGER,
            SalesQuota REAL,
            Bonus REAL,
            CommissionPct REAL,
            FOREIGN KEY (TerritoryID) REFERENCES SalesTerritory(TerritoryID)
        );
          """)
        self.cursor.execute("""
         CREATE TABLE IF NOT EXISTS Product (
            ProductID INTEGER PRIMARY KEY,
            Name TEXT,
            StandardCost REAL,
            ListPrice REAL
        );
            """)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS SalesOrderHeader (
            SalesOrderID INTEGER PRIMARY KEY,
            OrderDate TEXT,
            ShipDate TEXT,
            CustomerID INTEGER,
            SalesPersonID INTEGER,
            TerritoryID INTEGER,
            SubTotal REAL,
            ModifiedDate TEXT,
            
            FOREIGN KEY (SalesPersonID) REFERENCES SalesPerson(BusinessEntityID),
            FOREIGN KEY (TerritoryID) REFERENCES SalesTerritory(TerritoryID)
        );""")
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS SalesOrderDetail (
            SalesOrderID INTEGER,
            ProductID INTEGER,
            OrderQty INTEGER,
            UnitPrice REAL,
            LineTotal REAL,

            PRIMARY KEY (SalesOrderID, ProductID),

            FOREIGN KEY (SalesOrderID) REFERENCES SalesOrderHeader(SalesOrderID),
            FOREIGN KEY (ProductID) REFERENCES Product(ProductID)
        );""")
        # Extra para controle do processo ETL
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS controle_etl (
            processo VARCHAR(100) PRIMARY KEY,
            ultima_execucao TIMESTAMP
        );""")
        self.cursor.connection.commit()
        
        # dados iniciais para controle do processo ETL
        self.cursor.execute("""
        INSERT INTO controle_etl (processo, ultima_execucao)
        VALUES 
        ('Product', '1900-01-01'),
        ('SalesPerson', '1900-01-01'),
        ('SalesTerritory', '1900-01-01'),
        ('SalesOrderHeader', '1900-01-01'),
        ('SalesOrderDetail', '1900-01-01')
        ON CONFLICT (processo) DO NOTHING;""")
        self.cursor.connection.commit()