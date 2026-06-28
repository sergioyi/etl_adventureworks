from utils import conn_olap, cursor_olap

def garantir_tabelas_controle(schema):
    cursor_olap.execute(f"""
        CREATE TABLE IF NOT EXISTS {schema}.controle_carga (
            carga_inicial BOOLEAN
        );
    """)

    cursor_olap.execute(f"""
        CREATE TABLE IF NOT EXISTS {schema}.controle_etl (
            processo VARCHAR(100) PRIMARY KEY,
            ultima_execucao TIMESTAMP
        );
    """)

    # Garante pelo menos 1 linha
    cursor_olap.execute(f"""
        INSERT INTO {schema}.controle_carga (carga_inicial)
        SELECT FALSE
        WHERE NOT EXISTS (
            SELECT 1 FROM {schema}.controle_carga
        );
    """)

    conn_olap.connection.commit()

def preparar_ambiente():

    garantir_tabelas_controle("staging")
    garantir_tabelas_controle("dw")