class InsertDW:
    def __init__(self, cursor, conn):
        self.cursor = cursor
        self.conn = conn

    def insert_dimproduto(self):
        self.cursor.execute("""
            INSERT INTO dw.DimProduto (IdProduto, Nome, Preco, Custo)
            SELECT 
                ProductID,
                Name,
                ListPrice,
                StandardCost
            FROM staging.Product
            ON CONFLICT (IdProduto) DO UPDATE
            SET 
                Nome = EXCLUDED.Nome,
                Preco = EXCLUDED.Preco,
                Custo = EXCLUDED.Custo;
        """)
        self.conn.connection.commit()

    def insert_dimvendedor(self):
        self.cursor.execute("""
            INSERT INTO dw.DimVendedor (IdVendedor, Meta)
            SELECT 
                BusinessEntityID,
                SalesQuota
            FROM staging.SalesPerson
            ON CONFLICT (IdVendedor) DO UPDATE
            SET Meta = EXCLUDED.Meta;
        """)
        self.conn.connection.commit()

    def insert_dimtempo(self):
        self.cursor_olap.execute("""
            INSERT INTO dw.DimTempo (
                IdData,
                Data,
                AnoMes,
                Ano,
                Mes,
                NomeMes,
                Trimestre
            )
            SELECT
                TO_CHAR(data,'YYYYMMDD')::INT AS IdData,
                data AS Data,
                TO_CHAR(data,'YYYYMM')::INT AS AnoMes,
                EXTRACT(YEAR FROM data)::INT AS Ano,
                EXTRACT(MONTH FROM data)::INT AS Mes,
                TO_CHAR(data,'TMMonth') AS NomeMes,
                EXTRACT(QUARTER FROM data)::INT AS Trimestre
            FROM generate_series(
                '2011-01-01'::DATE,
                '2014-12-31'::DATE,
                INTERVAL '1 day'
            ) AS data
            ON CONFLICT (IdData) DO NOTHING;
        """)

        self.conn.connection.commit()
    
    def isert_fatovendasmensal(self):
        self.cursor.execute("""
            INSERT INTO dw.fatovendasmensal
            SELECT
                dt.anoMes,
                SUM(f.receita)
            FROM dw.fatovendas f
            JOIN dw.dimtempo dt
                ON f.iddata = dt.Iddata
            GROUP BY dt.anomes;
        """)

    def insert_fatovendas(self):
        self.cursor.execute("""
            INSERT INTO dw.FatoVendas (
                IdPedido, IdProduto, IdCliente, IdVendedor,
                IdRegiao, IdData, DataEnvio,
                Quantidade, PrecoUnitario, Receita, Custo, Lucro
            )
            SELECT
                sod.SalesOrderID,
                sod.ProductID,
                soh.CustomerID,
                soh.SalesPersonID,
                soh.TerritoryID,
                CAST(TO_CHAR(soh.OrderDate, 'YYYYMMDD') AS INT),
                soh.ShipDate,
                sod.OrderQty,
                sod.UnitPrice,
                sod.LineTotal,
                (sod.OrderQty * p.StandardCost),
                (sod.LineTotal - (sod.OrderQty * p.StandardCost))
            FROM staging.SalesOrderDetail sod
            JOIN staging.SalesOrderHeader soh 
                ON sod.SalesOrderID = soh.SalesOrderID
            JOIN staging.Product p 
                ON sod.ProductID = p.ProductID
            ON CONFLICT (IdPedido, IdProduto) DO NOTHING;
        """)
        self.conn.connection.commit()