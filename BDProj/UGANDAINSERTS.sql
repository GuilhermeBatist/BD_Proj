use UGANDAKnuckles

-- Inserir dados na tabela tblPrioridade
INSERT INTO tblPrioridade (Classe_Prio, Nivel_Prio) VALUES
('M�xima', 1),
('Acima da M�dia', 2),
('M�dia', 3),
('Abaixo da M�dia', 4),
('M�nima', 5);

-- Inserir dados na tabela tblEstado
INSERT INTO tblEstado (Nome) VALUES
('Active'),
('Satisfied'),
('Canceled'),
('Waiting'),
('Forgotten');

-- Inserir fun��es na tabela tblFuncao
INSERT INTO tblFuncao (NomeFuncao) VALUES
('Professor'),
('Investigador'),
('Estudante de Licenciatura'),
('Estudante de Mestrado'),
('Estudante de Doutoramento'),
('Pessoal de Apoio'),
('Externo');

-- Inserir utilizadores na tabela tblUtilizador
INSERT INTO tblUtilizador (Nome, Telefone, Email, PrioID) VALUES
('Jos� Ribeiro', '912345678', 'jose.ribeiro@email.com', 2),
('Maria Oliveira', '923456789', 'maria.oliveira@email.com', 2),
('Carlos Pereira', '934567890', 'carlos.pereira@email.com', 3),
('Ana Costa', '945678901', 'ana.costa@email.com', 3),
('Miguel Silva', '956789012', 'miguel.silva@email.com', 4),
('Joana Martins', '967890123', 'joana.martins@email.com', 5),
('Rui Ferreira', '978901234', 'rui.ferreira@email.com', 1),
('Pedro Sousa', '989012345', 'pedro.sousa@email.com', 2),
('Cl�udia Souza', '913456789', 'claudia.souza@email.com', 2),
('Ricardo Almeida', '924567890', 'ricardo.almeida@email.com', 3),
('Lu�s Duarte', '935678901', 'luis.duarte@email.com', 4),
('Patr�cia Costa', '946789012', 'patricia.costa@email.com', 5),
('Felipe Mendes', '957890123', 'felipe.mendes@email.com', 2),
('Raquel Pereira', '968901234', 'raquel.pereira@email.com', 1),
('F�bio Carvalho', '979012345', 'fabio.carvalho@email.com', 1),
('Sofia Lima', '990123456', 'sofia.lima@email.com', 2),
('Jo�o Martins', '901234567', 'joao.martins@email.com', 3),
('Mariana Gomes', '912345678', 'mariana.gomes@email.com', 4),
('Gustavo Costa', '923456789', 'gustavo.costa@email.com', 5);

-- Inserir fun��es associadas aos utilizadores na tabela tblUtilizadorFuncao
INSERT INTO tblUtilizadorFuncao (UserID, FuncaoID) VALUES
(1, 1), -- Jos� Ribeiro � "Professor"
(2, 1), -- Maria Oliveira � "Professor"
(3, 2), -- Carlos Pereira � "Investigador"
(4, 3), -- Ana Costa � "Estudante de Licenciatura"
(5, 4), -- Miguel Silva � "Estudante de Mestrado"
(6, 5), -- Joana Martins � "Estudante de Doutoramento"
(7, 6), -- Rui Ferreira � "Pessoal de Apoio"
(8, 7), -- Pedro Sousa � "Externo"
(9, 1), -- Cl�udia Souza � "Professor"
(10, 2), -- Ricardo Almeida � "Investigador"
(11, 3), -- Lu�s Duarte � "Estudante de Licenciatura"
(12, 4), -- Patr�cia Costa � "Estudante de Mestrado"
(13, 5), -- Felipe Mendes � "Estudante de Doutoramento"
(14, 6), -- Raquel Pereira � "Pessoal de Apoio"
(15, 7), -- F�bio Carvalho � "Externo"
(16, 1), -- Sofia Lima � "Professor"
(17, 2), -- Jo�o Martins � "Investigador"
(18, 3), -- Mariana Gomes � "Estudante de Licenciatura"
(19, 4); -- Gustavo Costa � "Estudante de Mestrado"

-- Inserir dados na tabela tblReserva
INSERT INTO tblReserva (ReservaID, UserID, EstadoID) VALUES
('20240001', 1, 1),
('20240002', 2, 1),
('20240003', 3, 4),
('20240004', 4, 3),
('20240005', 5, 2),
('20240006', 6, 4),
('20240007', 7, 2),
('20240008', 8, 5),
('20240009', 9, 3),
('20240010', 10, 1),
('20240011', 11, 1),
('20240012', 12, 5),
('20240013', 13, 2),
('20240014', 14, 4),
('20240015', 15, 3),
('20240016', 16, 1),
('20240017', 17, 5),
('20240018', 18, 2),
('20240019', 19, 3),

-- Inserir dados na tabela tblEquipamento
INSERT INTO tblEquipamento (Descricao, EstadoID) VALUES
('Projetor de V�deo', 1),
('Computador Port�til', 2),
('Mesa de Reuni�o', 1),
('Cadeira', 1),
('Microfone', 3),
('C�mera de V�deo', 4),
('Papel e Caneta', 1),
('Extens�o El�trica', 2),
('Quadro Branco', 1),
('Impressora', 5),
('Scanner', 3),
('Lousa Digital', 1),
('Caixa de Som', 2),
('Ventilador', 4),
('Ar Condicionado', 5),
('Carregador de Telefone', 2),
('Tablet', 1),
('C�mera de Seguran�a', 3),
('Refrigerador', 4),
('Microfone Sem Fio', 5);


-- Inserir m�ltiplos registros na tabela tblEquip_req
INSERT INTO tblEquip_req (Equip_estado, ReqID, EquipID, UserID)
VALUES
(1, 1, 1, 1),  -- Equipamento 'Projetor de V�deo' (EquipID 1), Requisi��o 1, Utilizador 1
(2, 2, 2, 2),  -- Equipamento 'Computador Port�til' (EquipID 2), Requisi��o 2, Utilizador 2
(1, 3, 3, 3),  -- Equipamento 'Mesa de Reuni�o' (EquipID 3), Requisi��o 3, Utilizador 3
(1, 4, 4, 4),  -- Equipamento 'Cadeira' (EquipID 4), Requisi��o 4, Utilizador 4
(3, 5, 5, 5),  -- Equipamento 'Microfone' (EquipID 5), Requisi��o 5, Utilizador 5
(4, 6, 6, 6),  -- Equipamento 'C�mera de V�deo' (EquipID 6), Requisi��o 6, Utilizador 6
(1, 7, 7, 7),  -- Equipamento 'Papel e Caneta' (EquipID 7), Requisi��o 7, Utilizador 7
(2, 8, 8, 8),  -- Equipamento 'Extens�o El�trica' (EquipID 8), Requisi��o 8, Utilizador 8
(1, 9, 9, 9),  -- Equipamento 'Quadro Branco' (EquipID 9), Requisi��o 9, Utilizador 9
(5, 10, 10, 10), -- Equipamento 'Impressora' (EquipID 10), Requisi��o 10, Utilizador 10
(3, 11, 11, 11), -- Equipamento 'Scanner' (EquipID 11), Requisi��o 11, Utilizador 11
(1, 12, 12, 12), -- Equipamento 'Lousa Digital' (EquipID 12), Requisi��o 12, Utilizador 12
(2, 13, 13, 13), -- Equipamento 'Caixa de Som' (EquipID 13), Requisi��o 13, Utilizador 13
(4, 14, 14, 14), -- Equipamento 'Ventilador' (EquipID 14), Requisi��o 14, Utilizador 14
(5, 15, 15, 15), -- Equipamento 'Ar Condicionado' (EquipID 15), Requisi��o 15, Utilizador 15
(2, 16, 16, 16), -- Equipamento 'Carregador de Telefone' (EquipID 16), Requisi��o 16, Utilizador 16
(1, 17, 17, 17), -- Equipamento 'Tablet' (EquipID 17), Requisi��o 17, Utilizador 17
(3, 18, 18, 18), -- Equipamento 'C�mera de Seguran�a' (EquipID 18), Requisi��o 18, Utilizador 18
(4, 19, 19, 19), -- Equipamento 'Refrigerador' (EquipID 19), Requisi��o 19, Utilizador 19
(5, 20, 20, 20); -- Equipamento 'Microfone Sem Fio' (EquipID 20), Requisi��o 20, Utilizador 20


-- Inserir requisi��es na tabela tblRequisicao
INSERT INTO tblRequisicao (ReservaID, UserID, EstadoID)
VALUES
('20240001', 1, 1),
('20240002', 2, 1),
('20240003', 3, 4),
('20240004', 4, 3),
('20240005', 5, 2),
('20240006', 6, 4),
('20240007', 7, 2),
('20240008', 8, 5),
('20240009', 9, 3),
('20240010', 10, 1),
('20240011', 11, 1),
('20240012', 12, 5),
('20240013', 13, 2),
('20240014', 14, 4),
('20240015', 15, 3),
('20240016', 16, 1),
('20240017', 17, 5),
('20240018', 18, 2),
('20240019', 19, 3),
('20240020', 20, 4);

DECLARE @NovoID CHAR(8);
EXEC sp_InsertReservaComNovoID
    @UserID = 1, -- ID do utilizador
    @EstadoID = 2, -- ID do estado
    @NovoReservaID = @NovoID OUTPUT;

	INSERT INTO tblRes_equip (Necessario, ReservaID, EquipID) VALUES
(3, '20240001', 1),
(5, '20240001', 2),
(2, '20240002', 3),
(4, '20240002', 4),
(1, '20240003', 5),
(3, '20240003', 6),
(2, '20240004', 7),
(4, '20240004', 8),
(5, '20240005', 9),
(1, '20240005', 10),
(2, '20240006', 11),
(3, '20240006', 12),
(4, '20240007', 13),
(1, '20240007', 14),
(5, '20240008', 15),
(3, '20240008', 16),
(4, '20240009', 17),
(2, '20240009', 18),
(1, '20240010', 19),
(5, '20240010', 1),
(3, '20240011', 2),
(4, '20240011', 3),
(2, '20240012', 4),
(1, '20240012', 5),
(5, '20240013', 6),
(3, '20240013', 7),
(2, '20240014', 8),
(1, '20240014', 9),
(4, '20240015', 10),
(2, '20240015', 11),
(1, '20240016', 12),
(3, '20240016', 13),
(5, '20240017', 14),
(4, '20240017', 15),
(2, '20240018', 16),
(1, '20240018', 17),
(3, '20240019', 18),
(4, '20240019', 19);
