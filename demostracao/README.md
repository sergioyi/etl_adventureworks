# Comportamento do Projeto
Para uma explicação mais prática desse projeto de ETL faz aqui vai um tutorial de como é o comportamento esperado com o sistema em funcionamento
Execute o `inserts_demostracao.sql` em uma conexão do SQL Server, nele vai ter três registros para a tabela *SalesOrderHeader* do esquema `Sales` e assim que esses registros estiverem na tabela do SQL Server vai ter um no console do srcipt que é executado a cada 30 segundos uma mensagem:
```cmd
SalesOrderHeader: atualizado, executando ETL...
SalesOrderHeader: 3 registros processados
```
Isso comprova que o registro foi feito também na tabela de *salesorderheader* do Postgres do esquema `staging` assim realizando o seu comportamento esperado de ETL.
