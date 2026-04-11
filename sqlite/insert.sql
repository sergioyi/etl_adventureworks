-- controle elt bancop de dados Staging

INSERT INTO controle_etl (processo, ultima_execucao)
VALUES 
('Product', '1900-01-01'),
('SalesPerson', '1900-01-01'),
('SalesTerritory', '1900-01-01'),
('SalesOrderHeader', '1900-01-01'),
('SalesOrderDetail', '1900-01-01')
ON CONFLICT (processo) DO NOTHING;