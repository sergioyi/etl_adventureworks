import pyodbc
class SQLServerConnection:
    
    def __init__(self, server, database, username, password):
        self.server = server
        self.database = database
        self.username = username
        self.password = password
        self.connection = None
        self.cursor = None

    def connect(self):
        try:
            self.connection = pyodbc.connect(
                f"DRIVER={{ODBC Driver 18 for SQL Server}};"
                f"SERVER={self.server};"
                f"DATABASE={self.database};"
                f"UID={self.username};"
                f"PWD={self.password};"
                "Encrypt=yes;"
                "TrustServerCertificate=yes;"
            )
            self.cursor = self.connection.cursor()
            print("Conexão com SQL Server estabelecida com sucesso.")
        except Exception as e:
            print(f"Erro ao conectar ao SQL Server: {e}")

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            print("Conexão com SQL Server fechada.")
