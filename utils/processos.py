# Quero usar essa variavel para armazenar as informações de cada processo, como as queries e a função de carga correspondente. 
# Assim, posso iterar sobre ela para executar os processos de forma dinâmica.

processos = {

    "SalesOrderHeader": {
        "query_max": "SELECT MAX(ModifiedDate) FROM Sales.SalesOrderHeader",
        "query_incremental": """
            SELECT 
                SalesOrderID,
                OrderDate,
                ShipDate,
                CustomerID,
                SalesPersonID,
                TerritoryID,
                SubTotal,
                ModifiedDate
            FROM Sales.SalesOrderHeader
            WHERE ModifiedDate > ?
        """,
        "load_function": "insert_salesorderheader",
        "coluna_data_index": 7
    },

    "SalesPerson": {
        "query_max": "SELECT MAX(ModifiedDate) FROM Sales.SalesPerson",
        "query_incremental": """
            SELECT 
                BusinessEntityID,
                TerritoryID,
                SalesQuota,
                Bonus,
                CommissionPct,
                ModifiedDate
            FROM Sales.SalesPerson
            WHERE ModifiedDate > ?
        """,
        "load_function": "insert_salesperson",
        "coluna_data_index": 5
    },

    "SalesTerritory": {
        "query_max": "SELECT MAX(ModifiedDate) FROM Sales.SalesTerritory",
        "query_incremental": """
            SELECT 
                TerritoryID,
                Name,
                CountryRegionCode,
                [Group],
                ModifiedDate
            FROM Sales.SalesTerritory
            WHERE ModifiedDate > ?
        """,
        "load_function": "insert_salesTerritory",
        "coluna_data_index": 4
    },

    "Product": {
        "query_max": "SELECT MAX(ModifiedDate) FROM Production.Product",
        "query_incremental": """
            SELECT 
                ProductID,
                Name,
                StandardCost,
                ListPrice,
                ModifiedDate
            FROM Production.Product
            WHERE ModifiedDate > ?
        """,
        "load_function": "insert_product",
        "coluna_data_index": 4
    },

    "SalesOrderDetail": {
        "query_max": "SELECT MAX(ModifiedDate) FROM Sales.SalesOrderDetail",
        "query_incremental": """
            SELECT 
                SalesOrderID,
                ProductID,
                OrderQty,
                UnitPrice,
                LineTotal,
                ModifiedDate
            FROM Sales.SalesOrderDetail
            WHERE ModifiedDate > ?
        """,
        "load_function": "insert_salesorderdetail",
        "coluna_data_index": 5
    }
}