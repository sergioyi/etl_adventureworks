# Projeto desenvolvimento de Data WareHouse
Esse projeto tem o objetivo de demostrar o funcionamento de um Data WareHouse percorrendo os processos de ETL de uma base de dados OLTP para popular uma base de dados OLAP seguindo os padrões de modelagem multidimensional usando Python.

## Requisitos para a aplicação:
* SQLServer com a base de dados AdventureWorks
* PostgreSQL
* Python 3.11>
* DBaver ou alguma outra IDE dados
* Crie o arquivo `.env` usando de exemplo o `.env.example`

## controle de carga no OLAP
crie a tabela controle de carga e faça a inserção inicial manualmnente:

```sql
CREATE SCHEMA staging AUTHORIZATION postgres;
CREATE SCHEMA dw AUTHORIZATION postgres;
-- DDL
CREATE TABLE IF NOT EXISTS staging.controle_carga (
    carga_inicial BOOLEAN
);

CREATE TABLE IF NOT EXISTS dw.controle_carga (
    carga_inicial BOOLEAN
);
-- INSERT
INSERT INTO staging.controle_carga (carga_inicial)
VALUES (FALSE);
INSERT INTO dw.controle_carga (carga_inicial)
VALUES (FALSE);
```

