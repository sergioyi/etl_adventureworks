class CreateTablesDW:
    def __init__(self, cursor, conn_olap):
        self.cursor = cursor
        self.conn_olap = conn_olap

    def create_tables_dw(self):

        # Criar schema DW
        self.cursor.execute("CREATE SCHEMA IF NOT EXISTS dw;")

        # DIMENSÕES
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS dw.DimProduto (
            IdProduto INT PRIMARY KEY,
            Nome VARCHAR(255),
            Categoria VARCHAR(100),
            Subcategoria VARCHAR(100),
            Preco DECIMAL(10,2),
            Custo DECIMAL(10,2)
        );
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS dw.DimCliente (
            IdCliente INT PRIMARY KEY,
            TipoCliente VARCHAR(50)
        );
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS dw.DimVendedor (
            IdVendedor INT PRIMARY KEY,
            Meta DECIMAL(10,2)
        );
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS dw.DimRegiao (
            IdRegiao INT PRIMARY KEY,
            NomeRegiao VARCHAR(100),
            Pais VARCHAR(100),
            Grupo VARCHAR(100)
        );
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS dw.DimTempo (
            IdData INT PRIMARY KEY,
            Data DATE NOT NULL,
            AnoMes INT NOT NULL,
            Ano INT NOT NULL,
            Mes INT NOT NULL,
            NomeMes VARCHAR(20),
            Trimestre INT NOT NULL
        );
        """)
        
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS dw.fatovendasmensal (
            idvendames int NOT NULL,
            anomes int NOT NULL,
            receita int NOT NULL,
            CONSTRAINT fatovendasmensal_pkey PRIMARY KEY (idvendames)
        );
        """)

        # FATO
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS dw.FatoVendas (
            IdPedido INT,
            IdProduto INT,
            IdCliente INT,
            IdVendedor INT,
            IdRegiao INT,
            IdData INT,
            DataEnvio DATE,
            Quantidade INT,
            PrecoUnitario DECIMAL(10,2),
            Receita DECIMAL(12,2),
            Custo DECIMAL(12,2),
            Lucro DECIMAL(12,2),

            PRIMARY KEY (IdPedido, IdProduto),

            FOREIGN KEY (IdProduto) REFERENCES dw.DimProduto(IdProduto),
            FOREIGN KEY (IdCliente) REFERENCES dw.DimCliente(IdCliente),
            FOREIGN KEY (IdVendedor) REFERENCES dw.DimVendedor(IdVendedor),
            FOREIGN KEY (IdRegiao) REFERENCES dw.DimRegiao(IdRegiao),
            FOREIGN KEY (IdData) REFERENCES dw.DimTempo(IdData)
        );
        """)

        # CONTROLE DW
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS dw.controle_etl (
            processo VARCHAR(100) PRIMARY KEY,
            ultima_execucao TIMESTAMP
        );
        """)

        self.conn_olap.connection.commit()