class CreateTablesStaging:
    def __init__(self, cursor, conn_olap):
        self.cursor = cursor
        self.conn_olap = conn_olap

    def create_tables(self):
        self.cursor.execute("""
        CREATE SCHEMA IF NOT EXISTS staging;
        """)
        self.conn_olap.connection.commit()
        
        self.cursor.execute("""
          CREATE TABLE IF NOT EXISTS staging.SalesTerritory (
                TerritoryID INT PRIMARY KEY,
                Name VARCHAR(100),
                CountryRegionCode VARCHAR(10),
                "Group" VARCHAR(50),
                ModifiedDate TIMESTAMP
            );
          """)
        self.conn_olap.connection.commit()
        self.cursor.execute("""
         CREATE TABLE IF NOT EXISTS staging.SalesPerson (
            BusinessEntityID INT PRIMARY KEY,
            TerritoryID INT,
            SalesQuota NUMERIC(12,2),
            Bonus NUMERIC(12,2),
            CommissionPct NUMERIC(5,2),
            ModifiedDate TIMESTAMP,
            FOREIGN KEY (TerritoryID) REFERENCES staging.SalesTerritory(TerritoryID)
        );
          """)
        self.conn_olap.connection.commit()
        self.cursor.execute("""
         CREATE TABLE IF NOT EXISTS staging.Product (
            ProductID INT PRIMARY KEY,
            Name VARCHAR(255),
            StandardCost NUMERIC(12,2),
            ListPrice NUMERIC(12,2),
            ModifiedDate TIMESTAMP
        );
            """)
        self.conn_olap.connection.commit()
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS staging.SalesOrderHeader (
            SalesOrderID INT PRIMARY KEY,
            OrderDate DATE,
            ShipDate DATE,
            CustomerID INT,
            SalesPersonID INT,
            TerritoryID INT,
            SubTotal NUMERIC(12,2),
            ModifiedDate TIMESTAMP,

            FOREIGN KEY (SalesPersonID) REFERENCES staging.SalesPerson(BusinessEntityID),
            FOREIGN KEY (TerritoryID) REFERENCES staging.SalesTerritory(TerritoryID)
        );""")
        self.conn_olap.connection.commit()

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS staging.SalesOrderDetail (
            SalesOrderID INT,
            ProductID INT,
            OrderQty INT,
            UnitPrice NUMERIC(12,2),
            LineTotal NUMERIC(12,2),
            ModifiedDate TIMESTAMP,

            PRIMARY KEY (SalesOrderID, ProductID),

            FOREIGN KEY (SalesOrderID) REFERENCES staging.SalesOrderHeader(SalesOrderID),
            FOREIGN KEY (ProductID) REFERENCES staging.Product(ProductID)
        );""")
        self.conn_olap.connection.commit()
        
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS staging.controle_etl (
            processo VARCHAR(100) PRIMARY KEY,
            ultima_execucao TIMESTAMP
        );""")
        self.conn_olap.connection.commit()