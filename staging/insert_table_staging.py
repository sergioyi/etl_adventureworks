# Essa classe serve para inserir os dados nas tabelas de staging

class InsertTableStaging:
    def __init__(self, cursor, conn_olap):
        self.cursor = cursor
        self.conn_olap = conn_olap

    def insert_salesTerritory(self, rows):        
        rows_convertidos = [tuple(row) for row in rows]
        # colocar o ON CONFLICT (TerritoryID) DO NOTHING para evitar erros de chave primária duplicada
        
        self.cursor.executemany("""
            INSERT INTO staging.SalesTerritory (
                TerritoryID,
                Name,
                CountryRegionCode,
                "Group",
                ModifiedDate 
            ) VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (TerritoryID) DO NOTHING;
        """, rows_convertidos)
        
        self.conn_olap.connection.commit()

    def insert_salesperson(self, rows):
        rows_convertidos = [
            (
                row.BusinessEntityID,
                row.TerritoryID,
                float(row.SalesQuota) if row.SalesQuota else None,
                float(row.Bonus) if row.Bonus else None,
                float(row.CommissionPct) if row.CommissionPct else None,
                row.ModifiedDate
            )
            for row in rows
        ]

        self.cursor.executemany("""
            INSERT INTO staging.SalesPerson (
                BusinessEntityID,
                TerritoryID,
                SalesQuota,
                Bonus,
                CommissionPct,
                ModifiedDate
            ) VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (BusinessEntityID) DO NOTHING;
        """, rows_convertidos)

        self.conn_olap.connection.commit()

    def insert_product(self, rows):
        rows_convertidos = [tuple(row) for row in rows]
        self.cursor.executemany("""
          INSERT INTO staging.Product (
            ProductID,
            Name,
            StandardCost,
            ListPrice,
            ModifiedDate
        ) VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (ProductID) DO NOTHING;
        """, rows_convertidos)

        self.conn_olap.connection.commit()

    def insert_salesorderheader(self, rows):
        rows_convertidos = [tuple(row) for row in rows]
        self.cursor.executemany("""
        INSERT INTO staging.SalesOrderHeader (
            SalesOrderID,
            OrderDate,
            ShipDate,
            CustomerID,
            SalesPersonID,
            TerritoryID,
            SubTotal,
            ModifiedDate
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (SalesOrderID) DO NOTHING;
        """, rows_convertidos)
        
        self.conn_olap.connection.commit()

    def insert_salesorderdetail(self, rows):
        rows_convertidos = [tuple(row) for row in rows]
        self.cursor.executemany("""
        INSERT INTO staging.SalesOrderDetail (
            SalesOrderID,
            ProductID,
            OrderQty,
            UnitPrice,
            LineTotal,
            ModifiedDate
        ) VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (SalesOrderID, ProductID) DO NOTHING;
        """, rows_convertidos)
        
        self.conn_olap.connection.commit()

        