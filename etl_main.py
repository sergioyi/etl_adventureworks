from time import sleep

from etl.controle import preparar_ambiente
from etl.carga_inicial import carga_inicial_dw, carga_inicial_staging, executar_carga_inicial, verificar_carga_inicial
from etl.incremental import verificar_dados_novos, verificar_dados_novos_dw


# Inicio
preparar_ambiente()


PROCESSOS_STAGING = {
    "Product": {},
    "SalesPerson": {},
    "SalesTerritory": {},
    "SalesOrderHeader": {},
    "SalesOrderDetail": {}
}

if not verificar_carga_inicial("staging"):
    executar_carga_inicial(
        schema="staging",
        carga_func=carga_inicial_staging,
        processos=PROCESSOS_STAGING
    )

PROCESSOS_DW = {
    "DimProduto": {},
    "DimCliente": {},
    "DimTempo": {},
    "DimVendedor": {},
    "FatoVendas": {},
    "FatoVendasMensal": {}
}


if not verificar_carga_inicial("dw"):
    executar_carga_inicial(
        schema="dw",
        carga_func=carga_inicial_dw,
        processos=PROCESSOS_DW
    )

# Mantendo a aplicação ligada
while True:
    verificar_dados_novos()      # STAGING
    verificar_dados_novos_dw()   # DW
    sleep(30)