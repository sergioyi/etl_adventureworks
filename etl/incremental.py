from datetime import datetime

from utils import conn_olap, cursor_olap, cursor_oltp
from staging.insert_table_staging import InsertTableStaging
from utils.processos import processos

from dw.insert_dw import InsertDW
from utils.processos_dw import processos_dw

def verificar_dados_novos():

    print("Verificando dados novos...")

    # buscar controle
    cursor_olap.execute("""
        SELECT processo, ultima_execucao 
        FROM staging.controle_etl;
    """)

    controle = {row[0]: row[1] for row in cursor_olap.fetchall()}

    load_staging = InsertTableStaging(cursor_olap, conn_olap)

    for processo, config in processos.items():

        ultima_execucao = controle.get(processo, datetime(1900, 1, 1))

        # pegar última modificação
        cursor_oltp.execute(config["query_max"])
        max_modified = cursor_oltp.fetchone()[0]

        if not max_modified or max_modified <= ultima_execucao:
            print(f"{processo}: sem atualização")
            continue

        print(f"{processo}: atualizado, executando ETL...")

        # extract
        cursor_oltp.execute(config["query_incremental"], (ultima_execucao,))
        rows = cursor_oltp.fetchall()

        if not rows:
            continue

        # load dinâmico
        getattr(load_staging, config["load_function"])(rows)

        # atualizar controle
        max_data = max(row[config["coluna_data_index"]] for row in rows)

        cursor_olap.execute("""
            UPDATE staging.controle_etl
            SET ultima_execucao = %s
            WHERE processo = %s
        """, (max_data, processo))

        conn_olap.connection.commit()

        print(f"{processo}: {len(rows)} registros processados")




def verificar_dados_novos_dw():
    print("Verificando dados novos DW...")

    cursor_olap.execute("""
        SELECT processo, ultima_execucao 
        FROM dw.controle_etl;
    """)

    controle = {row[0]: row[1] for row in cursor_olap.fetchall()}

    load_dw = InsertDW(cursor_olap, conn_olap)

    for processo, config in processos_dw.items():

        ultima_execucao = controle.get(processo, datetime(1900, 1, 1))

        # pega última data do staging
        cursor_olap.execute(config["query_max"])
        max_data = cursor_olap.fetchone()[0]

        if not max_data or max_data <= ultima_execucao:
            print(f"{processo}: sem atualização")
            continue

        print(f"{processo}: atualizando DW...")

        # executa carga
        getattr(load_dw, config["load_function"])()

        # atualiza controle
        cursor_olap.execute("""
            UPDATE dw.controle_etl
            SET ultima_execucao = %s
            WHERE processo = %s
        """, (max_data, processo))

        conn_olap.connection.commit()