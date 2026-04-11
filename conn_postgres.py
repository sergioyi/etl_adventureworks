import psycopg2
# Faça um módulo de conexão com o PostgreSQL, para ser importado no etl_stating.py
class PostgresConnection:
    def __init__(self, host, port, database, user, password):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.connection = None

    def connect(self):
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            print("Conexão com PostgreSQL estabelecida com sucesso!")
        except Exception as e:
            print(f"Erro ao conectar ao PostgreSQL: {e}")