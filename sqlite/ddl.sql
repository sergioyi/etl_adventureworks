CREATE TABLE IF NOT EXISTS SalesTerritory (
TerritoryID INTEGER PRIMARY KEY,
Name TEXT,
CountryRegionCode TEXT,
"Group" TEXT
);

CREATE TABLE IF NOT EXISTS SalesPerson (
BusinessEntityID INTEGER PRIMARY KEY,
TerritoryID INTEGER,
SalesQuota REAL,
Bonus REAL,
CommissionPct REAL,
FOREIGN KEY (TerritoryID) REFERENCES SalesTerritory(TerritoryID)
);

CREATE TABLE IF NOT EXISTS Product (
   ProductID INTEGER PRIMARY KEY,
   Name TEXT,
   StandardCost REAL,
   ListPrice REAL
);

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
);

CREATE TABLE IF NOT EXISTS SalesOrderDetail (
    SalesOrderID INTEGER,
    ProductID INTEGER,
    OrderQty INTEGER,
    UnitPrice REAL,
    LineTotal REAL,

    PRIMARY KEY (SalesOrderID, ProductID),

    FOREIGN KEY (SalesOrderID) REFERENCES SalesOrderHeader(SalesOrderID),
    FOREIGN KEY (ProductID) REFERENCES Product(ProductID)
);
CREATE TABLE IF NOT EXISTS controle_etl (
    processo VARCHAR(100) PRIMARY KEY,
    ultima_execucao TIMESTAMP
);
  