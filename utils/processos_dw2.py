processos_dw = {

    "DimRegiao": {
        "query_max": "SELECT MAX(ModifiedDate) FROM staging.SalesTerritory",
        "query_incremental": """
            SELECT 
                TerritoryID,
                Name,
                CountryRegionCode,
                "Group",
                ModifiedDate
            FROM staging.SalesTerritory
            WHERE ModifiedDate > %s
        """,
        "load_function": "load_dim_regiao",
        "coluna_data_index": 4
    },

    "DimProduto": {
        "query_max": "SELECT MAX(ModifiedDate) FROM staging.Product",
        "query_incremental": """
            SELECT 
                ProductID,
                Name,
                StandardCost,
                ListPrice,
                ModifiedDate
            FROM staging.Product
            WHERE ModifiedDate > %s
        """,
        "load_function": "load_dim_produto",
        "coluna_data_index": 4
    },

    "DimVendedor": {
        "query_max": "SELECT MAX(ModifiedDate) FROM staging.SalesPerson",
        "query_incremental": """
            SELECT 
                BusinessEntityID,
                TerritoryID,
                SalesQuota,
                ModifiedDate
            FROM staging.SalesPerson
            WHERE ModifiedDate > %s
        """,
        "load_function": "load_dim_vendedor",
        "coluna_data_index": 3
    },

    "DimCliente": {
        "query_max": "SELECT MAX(ModifiedDate) FROM staging.SalesOrderHeader",
        "query_incremental": """
            SELECT DISTINCT
                CustomerID,
                ModifiedDate
            FROM staging.SalesOrderHeader
            WHERE ModifiedDate > %s
        """,
        "load_function": "load_dim_cliente",
        "coluna_data_index": 1
    },

    "DimTempo": {
        "query_max": "SELECT MAX(ModifiedDate) FROM staging.SalesOrderHeader",
        "query_incremental": """
            SELECT DISTINCT
                OrderDate,
                ModifiedDate
            FROM staging.SalesOrderHeader
            WHERE ModifiedDate > %s
        """,
        "load_function": "load_dim_tempo",
        "coluna_data_index": 1
    },

    "FatoVendas": {
        "query_max": "SELECT MAX(ModifiedDate) FROM staging.SalesOrderDetail",
        "query_incremental": """
            SELECT 
                sod.SalesOrderID,
                sod.ProductID,
                sod.OrderQty,
                sod.UnitPrice,
                sod.LineTotal,
                sod.ModifiedDate
            FROM staging.SalesOrderDetail sod
            WHERE sod.ModifiedDate > %s
        """,
        "load_function": "load_fato_vendas",
        "coluna_data_index": 5
    }
}