-----------------------------------------------------------------------FUNCTIONS-----------------------------------------------------------------------
-- Funcao para gerar IDs de reserva/requisicao
    CREATE FUNCTION Fun_MakeID
    (
        @Data DATE,
        @Numero INT
    )
    RETURNS CHAR(8)
    AS
    BEGIN
        RETURN FORMAT(@Data, 'yyyyMMdd') + RIGHT('0000' + CAST(@Numero AS VARCHAR), 4);
    END;
    GO

-- Funcao para gerar IDs de usuário (AUMENTAR O NUMERO DE CHARS DE NOME?? EX:Fernand(o) ou Sebasti(ao))
    CREATE FUNCTION Fun_GenerateUserID
    (
        @Prefix VARCHAR(2),
        @Name VARCHAR(50)
    )
    RETURNS CHAR(10)
    AS
    BEGIN
        RETURN @Prefix + '_' + LEFT(@Name, 7);
    END;
    GO

	----------------------------------------------------------------------Procedure----------------------------------------------------------------------

--Alteracao:
    --"Transforma" uma reserva em uma requisicao
        CREATE PROCEDURE Procedure_Reserva_to_Requisicao
            @ReservaID INT
        AS
        BEGIN
            DECLARE @UserID INT, @EstadoID INT, @DataAtual DATE;

            -- Obter informacoes da reserva
            SELECT @UserID = UserID, @EstadoID = EstadoID
            FROM tblReserva
            WHERE ReservaID = @ReservaID;

            -- Inserir a requisicao correspondente
            INSERT INTO tblRequisicao (DataRetirada, EstadoID)
            VALUES (GETDATE(), @EstadoID);

            DECLARE @ReqID INT = SCOPE_IDENTITY();

            -- Mover os equipamentos da reserva para a requisicao
            INSERT INTO tblEquip_Req (Equip_estado, ReqID, EquipID)
            SELECT Necessario, @ReqID, EquipID
            FROM tblRes_equip
            WHERE ReservaID = @ReservaID;

            -- Atualizar o estado da reserva
            UPDATE tblReserva
            SET EstadoID = (SELECT EstadoID FROM tblEstado WHERE Nome = 'Satisfied')
            WHERE ReservaID = @ReservaID;
        END;
        GO

--Decisao de Penalizacao:
    --Cancela a Reserva e penaliza o utilizador se necessario
        CREATE PROCEDURE Procedure_Cancel_Reserva
            @ReservaID INT,
            @CancelTime DATETIME
        AS
        BEGIN
            DECLARE @StartTime DATETIME, @UserID INT;

            -- Obter o periodo de uso da reserva
            SELECT 
                @StartTime = Timestamp,
                @UserID = UserID
            FROM tblReserva
            WHERE ReservaID = @ReservaID;

            -- Determinar penalizacao com base no momento do cancelamento
            IF @CancelTime < DATEADD(HOUR, -2, @StartTime)
            BEGIN
                -- Cancelamento sem penalizacao
                UPDATE tblReserva SET EstadoID = (SELECT EstadoID FROM tblEstado WHERE Nome = 'Canceled') WHERE ReservaID = @ReservaID;
            END
            ELSE
            BEGIN
                -- Cancelamento com penalizacao
                UPDATE tblReserva SET EstadoID = (SELECT EstadoID FROM tblEstado WHERE Nome = 'Canceled') WHERE ReservaID = @ReservaID;

                UPDATE tblPrioridade
                SET Nivel_Prio = Nivel_Prio - 1
                WHERE PrioID = (SELECT PrioID FROM tblUtilizador WHERE UserID = @UserID);
            END;
        END;
        GO

    --Penaliza o utilizador diminuido a sua prioridade
        CREATE PROCEDURE Procedure_PenalizeForDelay
            @ReqID INT,
            @ReturnTime DATETIME
        AS
        BEGIN
            DECLARE @EndTime DATETIME, @UserID INT, @DelayHours INT;

            -- Obter o período de uso da requisicao
            SELECT 
                @EndTime = r.DataRetirada,
                @UserID = u.UserID
            FROM tblRequisicao r
            JOIN tblReserva res ON r.ReqID = res.ReservaID
            JOIN tblUtilizador u ON res.UserID = u.UserID
            WHERE r.ReqID = @ReqID;

            -- Calcular atraso
            SET @DelayHours = DATEDIFF(HOUR, @EndTime, @ReturnTime);

            -- Aplicar penalizacao com base no atraso
            IF @DelayHours > 0
            BEGIN
                DECLARE @Penalties INT = CEILING(@DelayHours / 1.0);

                UPDATE tblPrioridade
                SET Nivel_Prio = Nivel_Prio - @Penalties
                WHERE PrioID = (SELECT PrioID FROM tblUtilizador WHERE UserID = @UserID);
            END;
        END;
        GO



CREATE PROCEDURE sp_InsertReservaComNovoID
    @UserID INT,
    @EstadoID INT,
    @NovoReservaID CHAR(8) OUTPUT
AS
BEGIN
    -- Declaração de variáveis
    DECLARE @AnoAtual CHAR(4) = CAST(YEAR(GETDATE()) AS CHAR(4)); -- Ano atual
    DECLARE @UltimaSequencia INT; -- Últimos 4 caracteres convertidos para inteiro
    DECLARE @UltimoReservaID CHAR(8); -- Último ID encontrado

    -- Identificar o maior ReservaID no formato yyyySSSS
    SELECT @UltimoReservaID = MAX(ReservaID)
    FROM tblReserva
    WHERE LEFT(ReservaID, 4) = @AnoAtual; -- Filtrar IDs do ano atual

    -- Determinar a sequência atual
    IF @UltimoReservaID IS NULL
    BEGIN
        -- Se não houver reservas para o ano atual, iniciar com 0001
        SET @UltimaSequencia = 0;
    END
    ELSE
    BEGIN
        -- Extrair os últimos 4 caracteres do ID e converter para inteiro
        SET @UltimaSequencia = CAST(RIGHT(@UltimoReservaID, 4) AS INT);
    END

    -- Incrementar a sequência
    SET @UltimaSequencia = @UltimaSequencia + 1;

    -- Gerar o novo ReservaID no formato yyyySSSS
    SET @NovoReservaID = @AnoAtual + RIGHT('0000' + CAST(@UltimaSequencia AS VARCHAR), 4);

    -- Inserir na tabela tblReserva
    INSERT INTO tblReserva (ReservaID, DataReserva, UserID, EstadoID)
    VALUES (@NovoReservaID, GETDATE(), @UserID, @EstadoID);

   -- Retornar o ID gerado
   SELECT @NovoReservaID AS NovoReservaID;

END;
GO



--------------------------------------------------------------------------------------Triggers--------------------------------------------------------------------------------------

--Deletes:
    -- Trigger para remover um registros de tblReserva_Equip quando apagam um equipamento
        CREATE TRIGGER trg_Delete_EquipID_Equipamento
        ON tblEquipamento
        FOR DELETE
        AS
        BEGIN
        DELETE FROM tblRes_equip WHERE EquipID IN (SELECT EquipID FROM DELETED);
        END;
        GO
    -- Trigger para remover um equipamento de tblEquip_Req quando apagam uma requisicao
        CREATE TRIGGER trg_Delete_ReqID_Equipamente
        ON tblRequisicao
        FOR DELETE
        AS
        BEGIN
        DELETE FROM tblEquip_Req WHERE ReqID IN (SELECT ReqID FROM DELETED);
        END;
        GO

    -- Trigger para remover um registro de equipamentos em tblReserva_Equip quando apagam uma reserva
        CREATE TRIGGER trg_Delete_ReservaID_Equipamento
        ON tblReserva
        FOR DELETE
        AS
        BEGIN
        DELETE FROM tblRes_equip WHERE ReservaID IN (SELECT ReservaID FROM DELETED);
        END;
        GO

--Mudanca de Estados:
    --Trigger para quando a reserva expira diminuir o nivel de prioridade do utilizador
        CREATE TRIGGER trg_Expired_Reserva
        ON tblReserva
        AFTER UPDATE
        AS
        BEGIN
            DECLARE @ReservaID INT, @EstadoID INT, @UserID INT;

            -- Obter as reservas cujo periodo expirou sem acao
            SELECT 
                @ReservaID = i.ReservaID,
                @EstadoID = i.EstadoID,
                @UserID = r.UserID
            FROM 
                INSERTED i
                JOIN tblReserva r ON i.ReservaID = r.ReservaID
            WHERE i.EstadoID = (SELECT EstadoID FROM tblEstado WHERE Nome = 'Forgotten');

            -- Penalizar prioridade do utilizador
            IF @EstadoID = (SELECT EstadoID FROM tblEstado WHERE Nome = 'Forgotten')
            BEGIN
                UPDATE tblPrioridade
                SET Nivel_Prio = Nivel_Prio - 1
                WHERE PrioID = (SELECT PrioID FROM tblUtilizador WHERE UserID = @UserID);
            END;
        END;
        GO    
        
        -- Trigger para chamar Procedure_Reserva_to_Requisicao ao mudar estado para 'Satisfied'
        CREATE TRIGGER trg_Satisfied_Reserva
        ON tblReserva
        AFTER UPDATE
        AS
        BEGIN
            IF EXISTS (SELECT 1 FROM INSERTED WHERE EstadoID = (SELECT EstadoID FROM tblEstado WHERE Nome = 'Satisfied'))
            BEGIN
                DECLARE @ReservaID INT;
                SELECT @ReservaID = ReservaID FROM INSERTED;
                EXEC Procedure_Reserva_to_Requisicao @ReservaID;
            END;
        END;
        GO

--Prioridades:
    --Altera a ordem das reservas mediante a prioridade dos users e o tempo das suas reservas
        CREATE TRIGGER trg_PriorityPreemption
        ON tblReserva
        AFTER INSERT
        AS
        BEGIN
            DECLARE @NewReservaID INT, @NewUserPriority INT, @NewStartTime DATETIME;

            -- Obter os detalhes da reserva inserida
            SELECT 
                @NewReservaID = ReservaID, 
                @NewUserPriority = p.Nivel_Prio,
                @NewStartTime = i.Timestamp
            FROM 
                INSERTED i
                JOIN tblUtilizador u ON i.UserID = u.UserID
                JOIN tblPrioridade p ON u.PrioID = p.PrioID;

            -- Preempcao: Identificar reservas a serem movidas para "waiting"
            UPDATE tblReserva
            SET EstadoID = (SELECT EstadoID FROM tblEstado WHERE Nome = 'Waiting')
            WHERE ReservaID != @NewReservaID
            AND EstadoID = (SELECT EstadoID FROM tblEstado WHERE Nome = 'Active')
            AND Timestamp < DATEADD(HOUR, -48, @NewStartTime)
            AND EXISTS (
                SELECT 1 
                FROM tblUtilizador u
                WHERE u.UserID = tblReserva.UserID
                    AND u.PrioID < @NewUserPriority
            );
        END;
        GO

    --Trigger para alterar prioridade
        CREATE TRIGGER trg_UpdatePriority
ON tblRequisicao
AFTER INSERT
AS
BEGIN
    DECLARE @UserID INT, @CountCorrect INT;

    -- Obter o ID do utilizador relacionado à reserva que gerou a requisição
    SELECT @UserID = r.UserID
    FROM INSERTED i
    JOIN tblReserva r ON r.ReservaID = i.ReqID;

    -- Contar o número de reservas satisfatórias consecutivas para o utilizador
    SELECT @CountCorrect = COUNT(*)
    FROM tblRequisicao rq
    JOIN tblReserva res ON rq.ReqID = res.ReservaID
    WHERE rq.EstadoID = (SELECT EstadoID FROM tblEstado WHERE Nome = 'Satisfied')
      AND res.UserID = @UserID;

    -- Subir prioridade corrente se atingiu 2 consecutivas
    IF @CountCorrect >= 2
    BEGIN
        UPDATE tblPrioridade
        SET Nivel_Prio = Nivel_Prio + 1
        WHERE PrioID = (SELECT PrioID FROM tblUtilizador WHERE UserID = @UserID)
          AND Nivel_Prio < (SELECT MAX(Nivel_Prio) 
                            FROM tblPrioridade 
                            WHERE Classe_Prio = (SELECT Classe_Prio 
                                                 FROM tblPrioridade 
                                                 JOIN tblUtilizador ON tblPrioridade.PrioID = tblUtilizador.PrioID 
                                                 WHERE tblUtilizador.UserID = @UserID));
    END;
END;
GO




------------------------------------------------------------------VIEWS---------------------------------------------------------------

CREATE VIEW ActiveReservations AS
SELECT 
    r.ReservaID,
    r.Timestamp AS ReservationTime,
    u.Nome AS UserName,
    e.Descricao AS Equipment,
    CASE 
        WHEN re.Necessario = 1 THEN 'Essential'
        ELSE 'Non-Essential'
    END AS Importance,
    es.Nome AS State
FROM tblReserva r
JOIN tblEstado es ON r.EstadoID = es.EstadoID
JOIN tblUtilizador u ON r.UserID = u.UserID
JOIN tblRes_equip re ON r.ReservaID = re.ReservaID
JOIN tblEquipamento e ON re.EquipID = e.EquipID
WHERE es.Nome = 'Active';
GO

CREATE VIEW DelayedReturns AS
SELECT 
    rq.ReqID,
    u.Nome AS UserName,
    e.Descricao AS Equipment,
    rq.DataRetirada AS BorrowDate,
    DATEDIFF(HOUR, rq.DataRetirada, GETDATE()) AS DelayHours
FROM tblRequisicao rq
JOIN tblEquip_Req er ON rq.ReqID = er.ReqID
JOIN tblEquipamento e ON er.EquipID = e.EquipID
JOIN tblUtilizador u ON rq.EstadoID = (SELECT EstadoID FROM tblEstado WHERE Nome = 'Active')
WHERE DATEDIFF(HOUR, rq.DataRetirada, GETDATE()) > 0;
GO

CREATE VIEW EquipmentUsageSummary AS
SELECT 
    e.EquipID,
    e.Descricao AS Equipment,
    COUNT(DISTINCT re.ReservaID) AS ReservationCount,
    COUNT(DISTINCT er.ReqID) AS RequisitionCount
FROM tblEquipamento e
LEFT JOIN tblRes_equip re ON e.EquipID = re.EquipID
LEFT JOIN tblEquip_Req er ON e.EquipID = er.EquipID
GROUP BY e.EquipID, e.Descricao;
GO

CREATE VIEW PendingReservations AS
SELECT 
    r.ReservaID,
    r.Timestamp AS ReservationTime,
    u.Nome AS UserName,
    e.Descricao AS Equipment,
    CASE 
        WHEN re.Necessario = 1 THEN 'Essential'
        ELSE 'Non-Essential'
    END AS Importance,
    es.Nome AS State
FROM tblReserva r
JOIN tblEstado es ON r.EstadoID = es.EstadoID
JOIN tblUtilizador u ON r.UserID = u.UserID
JOIN tblRes_equip re ON r.ReservaID = re.ReservaID
JOIN tblEquipamento e ON re.EquipID = e.EquipID
WHERE es.Nome = 'Waiting';
GO

CREATE VIEW ReservationHistory AS
SELECT 
    r.ReservaID,
    r.Timestamp AS ReservationTime,
    r.UserID,
    u.Nome AS UserName,
    e.Descricao AS Equipment,
    CASE 
        WHEN re.Necessario = 1 THEN 'Essential'
        ELSE 'Non-Essential'
    END AS Importance,
    es.Nome AS FinalState
FROM tblReserva r
JOIN tblEstado es ON r.EstadoID = es.EstadoID
JOIN tblUtilizador u ON r.UserID = u.UserID
JOIN tblRes_equip re ON r.ReservaID = re.ReservaID
JOIN tblEquipamento e ON re.EquipID = e.EquipID
WHERE es.Nome IN ('Satisfied', 'Canceled', 'Forgotten');
GO

CREATE VIEW ResourceState AS
SELECT 
    e.EquipID AS ResID,
    e.Descricao AS ResDesc,
    es.Nome AS State,
    COALESCE(r.ReservaID, rq.ReqID) AS ID,
    COALESCE(u.Nome, '-') AS Utilisador
FROM tblEquipamento e
LEFT JOIN tblEstado es ON e.EstadoID = es.EstadoID
LEFT JOIN tblRes_equip re ON e.EquipID = re.EquipID
LEFT JOIN tblReserva r ON re.ReservaID = r.ReservaID
LEFT JOIN tblEquip_Req er ON e.EquipID = er.EquipID
LEFT JOIN tblRequisicao rq ON er.ReqID = rq.ReqID
LEFT JOIN tblUtilizador u ON COALESCE(r.UserID, rq.ReqID) = u.UserID;
GO


CREATE VIEW UserPriorityOverview AS
SELECT 
    u.UserID,
    u.Nome AS UserName,
    p.Classe_Prio AS PriorityClass,
    p.Nivel_Prio AS CurrentPriority,
    u.Email,
    u.Telefone
FROM tblUtilizador u
JOIN tblPrioridade p ON u.PrioID = p.PrioID;
GO



CREATE VIEW Reserva AS
SELECT 
    ReservaID,
	FORMAT(Timestamp, 'yyyy-MM-dd HH:mm') AS DataReserva,
    UserID,
    EstadoID 
FROM tblReserva;
GO