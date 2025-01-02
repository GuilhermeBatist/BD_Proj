-- Cria��o do banco de dados e uso do banco UGANDAKnuckles
CREATE DATABASE UGANDAKnuckles;
GO
USE UGANDAKnuckles;
GO



_________________________________________________________________________________________________________________
-- Tabela tblPrioridade: Define as prioridades associadas aos utilizadores
CREATE TABLE tblPrioridade (
    PrioID INT IDENTITY(1,1) PRIMARY KEY, -- ID único para a prioridade
    Classe_Prio NVARCHAR(50) UNIQUE NOT NULL, -- Nome da classe de prioridade, único
    Nivel_Prio INT CHECK (Nivel_Prio > 0) NOT NULL -- Nível de prioridade, deve ser maior que 0
);

-- Tabela tblEstado: Define os estados gerais do sistema
CREATE TABLE tblEstado (
    EstadoID INT IDENTITY(1,1) PRIMARY KEY, -- ID único para o estado
    Nome NVARCHAR(50) NOT NULL -- Nome do estado (ex: Ativo, Cancelado)
);

-- Tabela tblFuncao: Define as funções associadas aos utilizadores
CREATE TABLE tblFuncao (
    FuncaoID INT IDENTITY(1,1) PRIMARY KEY, -- ID único para a função
    NomeFuncao NVARCHAR(50) NOT NULL -- Nome da função (ex: Professor, Investigador)
);

-- Tabela tblUtilizador: Contém informações sobre os utilizadores do sistema
CREATE TABLE tblUtilizador (
    UserID INT IDENTITY(1,1) PRIMARY KEY, -- ID único para o utilizador
    Nome NVARCHAR(100) NOT NULL, -- Nome completo do utilizador
    Telefone NVARCHAR(15), -- Telefone do utilizador
    Email NVARCHAR(100), -- Email do utilizador
    PrioID INT NOT NULL, -- Referência à prioridade do utilizador
    FOREIGN KEY (PrioID) REFERENCES tblPrioridade(PrioID) -- Chave estrangeira para tblPrioridade
        ON DELETE CASCADE -- Apagar utilizador apaga também a referência à prioridade
);

-- Tabela tblUtilizadorFuncao: Associa utilizadores a funções
CREATE TABLE tblUtilizadorFuncao (
    UserID INT NOT NULL, -- Referência ao ID do utilizador
    FuncaoID INT NOT NULL, -- Referência ao ID da função
    PRIMARY KEY (UserID, FuncaoID), -- Chave primária composta
    FOREIGN KEY (UserID) REFERENCES tblUtilizador(UserID) -- Chave estrangeira para tblUtilizador
        ON DELETE CASCADE, -- Apagar utilizador apaga também suas funções associadas
    FOREIGN KEY (FuncaoID) REFERENCES tblFuncao(FuncaoID) -- Chave estrangeira para tblFuncao
        ON DELETE CASCADE -- Apagar função apaga também associações
);

-- Tabela tblReserva: Registra reservas realizadas por utilizadores
CREATE TABLE tblReserva (
    ReservaID CHAR(8) PRIMARY KEY, -- ID da reserva com formato fixo de 8 caracteres
    UserID INT NOT NULL, -- Referência ao ID do utilizador que fez a reserva
    EstadoID INT NOT NULL, -- Referência ao estado da reserva
    DataReserva DATETIME NOT NULL DEFAULT GETDATE(), -- Marca o momento em que a reserva foi criada
    FOREIGN KEY (UserID) REFERENCES tblUtilizador(UserID) -- Chave estrangeira para tblUtilizador
        ON DELETE CASCADE, -- Apagar utilizador apaga suas reservas
    FOREIGN KEY (EstadoID) REFERENCES tblEstado(EstadoID) -- Chave estrangeira para tblEstado
        ON DELETE CASCADE -- Apagar estado apaga também reservas associadas
);

-- Tabela tblEquipamento: Contém informações sobre os equipamentos disponíveis
CREATE TABLE tblEquipamento (
    EquipID INT IDENTITY(1,1) PRIMARY KEY, -- ID único para o equipamento
    Descricao NVARCHAR(100) NOT NULL, -- Descrição do equipamento
    EstadoID INT NOT NULL, -- Estado do equipamento (ex: Disponível, Em manutenção)
    FOREIGN KEY (EstadoID) REFERENCES tblEstado(EstadoID) -- Chave estrangeira para tblEstado
        ON DELETE CASCADE -- Apagar estado apaga também equipamentos associados
);

-- Tabela tblRequisicao: Registra requisições de equipamentos
CREATE TABLE tblRequisicao (
    ReqID INT IDENTITY(1,1) PRIMARY KEY, -- ID único para a requisição
    ReservaID CHAR(8) NOT NULL, -- Referência à reserva associada
    UserID INT NOT NULL, -- Referência ao utilizador que fez a requisição
    EstadoID INT NOT NULL, -- Estado atual da requisição
    DataRetirada DATETIME NOT NULL DEFAULT GETDATE(), -- Marca o momento em que a requisição foi criada
    FOREIGN KEY (ReservaID) REFERENCES tblReserva(ReservaID) -- Chave estrangeira para tblReserva
        ON DELETE CASCADE, -- Apagar reserva apaga também requisições associadas
    FOREIGN KEY (UserID) REFERENCES tblUtilizador(UserID) -- Chave estrangeira para tblUtilizador
        ON DELETE CASCADE, -- Apagar utilizador apaga suas requisições
    FOREIGN KEY (EstadoID) REFERENCES tblEstado(EstadoID) -- Chave estrangeira para tblEstado
        ON DELETE CASCADE -- Apagar estado apaga também requisições associadas
);

-- Tabela tblEquip_req: Relaciona equipamentos às requisições feitas por utilizadores
CREATE TABLE tblEquip_req (
    Equip_reqID INT IDENTITY(1,1) PRIMARY KEY, -- ID único para cada relação de equipamento com requisição
    Equip_estado INT NOT NULL, -- Estado do equipamento dentro da requisição
    ReqID INT NOT NULL, -- Referência à requisição associada
    EquipID INT NOT NULL, -- Referência ao equipamento associado
    UserID INT NOT NULL, -- Referência ao utilizador que requisitou o equipamento
    FOREIGN KEY (ReqID) REFERENCES tblRequisicao(ReqID) -- Chave estrangeira para tblRequisicao
        ON DELETE CASCADE, -- Apagar requisição apaga também as associações de equipamentos
    FOREIGN KEY (EquipID) REFERENCES tblEquipamento(EquipID) -- Chave estrangeira para tblEquipamento
        ON DELETE CASCADE, -- Apagar equipamento apaga também as associações
    FOREIGN KEY (UserID) REFERENCES tblUtilizador(UserID) -- Chave estrangeira para tblUtilizador
        ON DELETE CASCADE -- Apagar utilizador apaga suas associações de equipamentos
);
CREATE TABLE tblRes_equip
(
  ResEquipID INT IDENTITY(1,1) NOT NULL,
  Necessario INT NOT NULL CHECK (Necessario >= 0),
  ReservaID cHAR(8) NOT NULL,
  EquipID INT NOT NULL,
  PRIMARY KEY (ResEquipID),
  FOREIGN KEY (ReservaID) REFERENCES tblReserva(ReservaID)
    ON DELETE CASCADE, -- Mant�m cascata para ReservaID
  FOREIGN KEY (EquipID) REFERENCES tblEquipamento(EquipID)
    ON DELETE NO ACTION -- Remove cascata para EquipID
);
GO