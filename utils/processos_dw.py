processos_dw = {

    "DimProduto": {
        "query_max": "SELECT MAX(ModifiedDate) FROM staging.Product",
        "load_function": "insert_dimproduto"
    },

    "DimVendedor": {
        "query_max": "SELECT MAX(ModifiedDate) FROM staging.SalesPerson",
        "load_function": "insert_dimvendedor"
    },

    "FatoVendas": {
        "query_max": """
            SELECT MAX(ModifiedDate) 
            FROM staging.SalesOrderDetail
        """,
        "load_function": "insert_fatovendas"
    }
}