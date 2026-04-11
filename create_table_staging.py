# Faça desse código uma importação para o meu arquivo principal para criar as tabelas no banco de dados PostgreSQL
# ele vai recerber o cursor do banco de dados PostgreSQL para criar as tabelas de staging
import psycopg2

class CreateTablesStaging:
    def __init__(self, cursor):
        self.cursor = cursor

    def create_tables(self):
        self.cursor.execute("""
          CREATE TABLE IF NOT EXISTS staging.SalesTerritory (
                TerritoryID INT PRIMARY KEY,
                Name VARCHAR(100),
                CountryRegionCode VARCHAR(10),
                "Group" VARCHAR(50)
            );
          """)
        self.cursor.execute("""
         CREATE TABLE IF NOT EXISTS staging.SalesPerson (
            BusinessEntityID INT PRIMARY KEY,
            TerritoryID INT,
            SalesQuota NUMERIC(12,2),
            Bonus NUMERIC(12,2),
            CommissionPct NUMERIC(5,2),

            FOREIGN KEY (TerritoryID) REFERENCES SalesTerritory(TerritoryID)
        );
          """)
        self.cursor.execute("""
         CREATE TABLE IF NOT EXISTS staging.Product (
            ProductID INT PRIMARY KEY,
            Name VARCHAR(255),
            StandardCost NUMERIC(12,2),
            ListPrice NUMERIC(12,2)
        );
            """)
        self.cursor.execute("""
        CREATE TABLE SalesOrderHeader (
            SalesOrderID INT PRIMARY KEY,
            OrderDate DATE,
            ShipDate DATE,
            CustomerID INT,
            SalesPersonID INT,
            TerritoryID INT,
            SubTotal NUMERIC(12,2),
            ModifiedDate TIMESTAMP,

            FOREIGN KEY (SalesPersonID) REFERENCES SalesPerson(BusinessEntityID),
            FOREIGN KEY (TerritoryID) REFERENCES SalesTerritory(TerritoryID)
        );""")
        self.cursor.execute("""
        CREATE TABLE SalesOrderDetail (
            SalesOrderID INT,
            ProductID INT,
            OrderQty INT,
            UnitPrice NUMERIC(12,2),
            LineTotal NUMERIC(12,2),

            PRIMARY KEY (SalesOrderID, ProductID),

            FOREIGN KEY (SalesOrderID) REFERENCES SalesOrderHeader(SalesOrderID),
            FOREIGN KEY (ProductID) REFERENCES Product(ProductID)
        );""")