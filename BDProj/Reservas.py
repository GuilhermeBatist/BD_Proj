from tkinter import Toplevel, Label, Button, Entry, messagebox, Frame
from tkinter.ttk import Treeview, Scrollbar

import pyodbc



def abrir_tela(conn):
    """
    Função para abrir a tela específica de Reservas, recebendo a conexão como argumento.
    """
    tela_reservas = Toplevel()
    tela_reservas.title("Reservas")
    tela_reservas.geometry("400x300")

    Label(tela_reservas, text="Gestão de Reservas", font=("Arial", 16, "bold")).pack(pady=10)
    Button(tela_reservas, text="Criar Reserva", width=25, font=("Arial", 14),command=lambda: criar_reserva(conn)).pack(pady=5)
    Button(tela_reservas, text="Visualizar Reservas", font=("Arial", 14),width=25, command=lambda: ler_reservas(conn)).pack(pady=5)
    Button(tela_reservas, text="Atualizar Reserva", font=("Arial", 14),width=25,command=lambda :atualizar_reserva(conn)).pack(pady=5)
    Button(tela_reservas, text="Excluir Reserva",font=("Arial", 14), width=25,command=lambda :excluir_reserva(conn)).pack(pady=5)



def criar_reserva(conn):
    """
    Janela para criar uma nova reserva com Equipamento incluído.
    """
    if conn is None:
        messagebox.showerror("Erro", "Conexão com o banco de dados não está configurada.")
        return

    # Janela de criação
    janela = Toplevel()
    janela.title("Criar Reserva")
    janela.geometry("800x600")

    Label(janela, text="Criar Nova Reserva", font=("Arial", 16, "bold")).pack(pady=10)

    # Frame da tabela (tkinter Treeview)
    frame_tabela = Frame(janela)
    frame_tabela.pack(pady=10)

    # Scrollbar para a tabela
    scrollbar = Scrollbar(frame_tabela)
    scrollbar.pack(side="right", fill="y")

    tabela = Treeview(frame_tabela, columns=("ID", "Descrição"), show="headings", yscrollcommand=scrollbar.set,
                      height=10)
    tabela.heading("ID", text="EquipID")
    tabela.heading("Descrição", text="Descrição do Equipamento")
    tabela.column("ID", width=100, anchor="center")
    tabela.column("Descrição", width=400, anchor="w")
    tabela.pack(side="left", fill="both", expand=True)
    scrollbar.config(command=tabela.yview)

    # Buscar equipamentos disponíveis no banco e preencher na tabela
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT e.EquipID, e.Descricao
            FROM tblEquipamento e
            WHERE NOT EXISTS (
                SELECT 1
                FROM tblRes_equip re
                JOIN tblReserva r ON re.ReservaID = r.ReservaID
                WHERE re.EquipID = e.EquipID
                AND r.Timestamp BETWEEN GETDATE() AND DATEADD(HOUR, 48, GETDATE())
            )
        """)
        equipamentos = cursor.fetchall()

        if not equipamentos:
            tabela.insert("", "end", values=("Nenhum", "Não há equipamentos disponíveis no momento"))
        else:
            for equip in equipamentos:
                tabela.insert("", "end", values=(equip[0], equip[1]))

    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao carregar equipamentos disponíveis: {e}")
        return

    # Frame com campos adicionais
    frame_campos = Frame(janela)
    frame_campos.pack(pady=20)

    # Campo de ID do Usuário
    Label(frame_campos, text="ID do Usuário:", font=("Arial", 12)).grid(row=0, column=0, padx=10)
    entrada_usuario = Entry(frame_campos, width=20)
    entrada_usuario.grid(row=0, column=1, padx=10)

    # Função para confirmar a reserva
    def confirmar_reserva():
        """
        Confirmar a criação da reserva com dados nas tabelas tblRes_equip e tblEquip_req.
        """
        # Captura de valores
        item_selecionado = tabela.selection()
        if not item_selecionado:
            messagebox.showerror("Erro", "Nenhum equipamento selecionado!")
            return

        equipamento_id = tabela.item(item_selecionado, "values")[0]  # Captura o EquipID
        usuario_id = entrada_usuario.get()

        if not usuario_id:
            messagebox.showerror("Erro", "O campo ID do Usuário é obrigatório!")
            return

        try:
            cursor = conn.cursor()

            # Criação de uma nova reserva (Retorna o ReservaID)
            print("Criando reserva...")
            cursor.execute("""
                DECLARE @NovoReservaID CHAR(8);
                EXEC sp_InsertReservaComNovoID 
                    @UserID = ?, 
                    @EstadoID = ?, 
                    @NovoReservaID = @NovoReservaID OUTPUT;
                SELECT @NovoReservaID;
            """, (usuario_id, 1))  # Estado padrão = 1 (Ajuste aqui)
            cursor.execute("""
                            SELECT TOP 1 ReservaID 
                            FROM tblReserva 
                            WHERE UserID = ? 
                            ORDER BY Timestamp DESC;
                        """, (usuario_id,))
            result = cursor.fetchone()
            if result:
                reserva_id = result[0]
                print(f"Reserva criada com ID: {reserva_id}")
            else:
                raise Exception("Erro ao criar a reserva. Nenhum ID retornado.")

            # Inserir dado na tabela `tblRes_equip`
            print("Vinculando equipamento à reserva...")
            cursor.execute("""
                INSERT INTO tblRes_equip (ReservaID, EquipID, Necessario)
                VALUES (?, ?, 1)
            """, (reserva_id, equipamento_id))

            # Criar uma requisição vinculada à reserva
            print("Criando requisição para a reserva...")
            cursor.execute("""
                INSERT INTO tblRequisicao (ReservaID, UserID, EstadoID, DataRetirada)
                VALUES (?, ?, ?, GETDATE());
            """, (reserva_id, usuario_id, 1))  # Estado padrão = 1
            cursor.execute("""
                SELECT TOP 1 ReqID
                FROM tblRequisicao
                WHERE UserID = ?
                ORDER BY DataRetirada DESC;
            """, (usuario_id,))
            requisicao_id = cursor.fetchone()[0]

            # Inserir o equipamento na tabela `tblEquip_req` (relação com requisição)
            print("Vinculando equipamento à requisição...")
            cursor.execute("""
                INSERT INTO tblEquip_req (ReqID, EquipID, Equip_estado)
                VALUES (?, ?, ?)
            """, (requisicao_id, equipamento_id, 1))  # Equip_estado = 1 (Pode ser ajustado)

            # Commit de todas as operações
            conn.commit()
            print(f"Reserva e requisição criadas com sucesso!\nReservaID: {reserva_id}, ReqID: {requisicao_id}")

            # Feedback ao usuário
            messagebox.showinfo("Sucesso", f"Reserva e requisição criadas com sucesso!\nReservaID: {reserva_id}")
            janela.destroy()

        except Exception as e:
            conn.rollback()  # Reverter alterações em caso de falha
            print(f"Erro ao criar reserva: {str(e)}")
            messagebox.showerror("Erro", f"Erro ao criar reserva: {e}")

    # Botão de confirmar reserva
    Button(janela, text="Confirmar Reserva", font=("Arial", 12), width=20, command=confirmar_reserva).pack(pady=20)


def ler_reservas(conn):
    """
    Função para exibir todas as reservas em uma tabela.
    """
    if conn is None:
        messagebox.showerror("Erro", "Conexão com o banco de dados não está configurada.")
        return

    # Janela para listar reservas
    janela_listar = Toplevel()
    janela_listar.title("Reservas Existentes")
    janela_listar.geometry("700x400")

    Label(janela_listar, text="Lista de Reservas", font=("Arial", 16, "bold")).pack(pady=10)

    # Frame para a tabela
    frame_tabela = Frame(janela_listar)
    frame_tabela.pack(pady=10)

    # Barra de rolagem
    scrollbar = Scrollbar(frame_tabela)
    scrollbar.pack(side="right", fill="y")

    # Tabela para exibir as reservas
    tabela = Treeview(frame_tabela, columns=("ID", "Usuário", "Data/Hora", "Estado"), show="headings",
                      yscrollcommand=scrollbar.set, height=15)
    tabela.heading("ID", text="ID da Reserva")
    tabela.heading("Usuário", text="ID do Usuário")
    tabela.heading("Data/Hora", text="Data e Hora")
    tabela.heading("Estado", text="Estado")
    tabela.column("ID", width=150, anchor="center")
    tabela.column("Usuário", width=150, anchor="center")
    tabela.column("Data/Hora", width=200, anchor="center")
    tabela.column("Estado", width=100, anchor="center")
    tabela.pack(side="left", fill="x", expand=True)
    scrollbar.config(command=tabela.yview)

    # Buscar reservas no banco de dados
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT r.ReservaID, r.UserID, r.Timestamp, r.EstadoID
            FROM tblReserva r
        """)
        reservas = cursor.fetchall()

        if not reservas:
            tabela.insert("", "end", values=("Nenhum", "Sem reservas", "", ""))
        else:
            for reserva in reservas:
                tabela.insert("", "end", values=(reserva[0], reserva[1], reserva[2], reserva[3]))

    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao listar reservas: {e}")
        return

def atualizar_reserva(conn):
    """
    Janela para atualizar uma reserva existente, exibindo todas as reservas em uma tabela.
    """
    if conn is None:
        messagebox.showerror("Erro", "Conexão com o banco de dados não está configurada.")
        return

    # Janela de Atualizar Reserva
    janela = Toplevel()
    janela.title("Atualizar Reserva")
    janela.geometry("800x800")

    Label(janela, text="Atualizar Reserva", font=("Arial", 16, "bold")).pack(pady=10)

    # Frame para a tabela de reservas
    frame_tabela = Frame(janela)
    frame_tabela.pack(fill="both", expand=True, pady=10)

    # Barra de rolagem
    scrollbar = Scrollbar(frame_tabela)
    scrollbar.pack(side="right", fill="y")

    # Tabela para exibir reservas
    tabela = Treeview(frame_tabela, columns=("ID", "Usuário", "Data/Hora", "Estado"), show="headings",
                      yscrollcommand=scrollbar.set, height=15)
    tabela.heading("ID", text="ID da Reserva")
    tabela.heading("Usuário", text="ID do Usuário")
    tabela.heading("Data/Hora", text="Data e Hora")
    tabela.heading("Estado", text="Estado")
    tabela.column("ID", width=150, anchor="center")
    tabela.column("Usuário", width=150, anchor="center")
    tabela.column("Data/Hora", width=250, anchor="center")
    tabela.column("Estado", width=100, anchor="center")
    tabela.pack(side="left", fill="both", expand=True)
    scrollbar.config(command=tabela.yview)

    # Buscar reservas no banco de dados
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT r.ReservaID, r.UserID, r.Timestamp, r.EstadoID
            FROM tblReserva r
        """)
        reservas = cursor.fetchall()

        if not reservas:
            tabela.insert("", "end", values=("Nenhum", "Sem usuário", "Sem data", "Sem estado"))
        else:
            for reserva in reservas:
                tabela.insert("", "end", values=(reserva[0], reserva[1], reserva[2], reserva[3]))

    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao buscar reservas: {e}")
        return

    # Campo para atualizar informações
    Label(janela, text="Escolha o ID da reserva na tabela acima e insira o novo estado abaixo:",
          font=("Arial", 12)).pack(pady=10)
    Label(janela, text="Novo Estado (ID):", font=("Arial", 12)).pack()
    entrada_novo_estado = Entry(janela, width=30)
    entrada_novo_estado.pack(pady=5)

    def selecionar_reserva_para_atualizar(event):
        """
        Função chamada ao selecionar uma reserva na tabela.
        """
        item_selecionado = tabela.selection()
        if item_selecionado:
            valores = tabela.item(item_selecionado, "values")
            entrada_novo_estado.focus()  # Foca no campo de novo estado

    # Vincular clique na tabela à seleção da reserva
    tabela.bind("<<TreeviewSelect>>", selecionar_reserva_para_atualizar)

    def confirmar_atualizacao():
        """
        Atualizar a reserva selecionada.
        """
        item_selecionado = tabela.selection()
        if not item_selecionado:
            messagebox.showerror("Erro", "Nenhuma reserva selecionada para atualizar!")
            return

        valores = tabela.item(item_selecionado, "values")
        reserva_id = valores[0]  # ID da reserva selecionada
        novo_estado = entrada_novo_estado.get()

        if not reserva_id or not novo_estado:
            print("Erro: ID da reserva ou novo estado está vazio.")
            return

        try:
            cursor = conn.cursor()
            print(f"ID da reserva: {reserva_id}")
            # Atualizar o estado da reserva no banco
            cursor.execute("""
                UPDATE tblRequisicao
                SET EstadoID = ?
                WHERE ReservaID = ?
            """, (novo_estado, reserva_id))
            cursor.execute("""
                UPDATE tblReserva
                SET EstadoID = ?
                WHERE ReservaID = ?
            """, (novo_estado, reserva_id))


            conn.commit()
            print(f"Reserva {reserva_id} atualizada com sucesso para o estado {novo_estado}!")
            janela.destroy()
        except Exception as e:
            conn.rollback()
            print(f"Erro ao atualizar reserva: {str(e)}")

    Button(janela, text="Atualizar", width=20, font=("Arial", 12), command=confirmar_atualizacao).pack(pady=20)


def excluir_reserva(conn):
    """
    Janela para excluir uma reserva existente, exibindo todas as reservas em uma tabela.
    """
    if conn is None:
        messagebox.showerror("Erro", "Conexão com o banco de dados não está configurada.")
        return

    # Janela de Excluir Reserva
    janela = Toplevel()
    janela.title("Excluir Reserva")
    janela.geometry("800x600")

    Label(janela, text="Excluir Reserva", font=("Arial", 16, "bold")).pack(pady=10)

    # Frame para a tabela de reservas
    frame_tabela = Frame(janela)
    frame_tabela.pack(fill="both", expand=True, pady=10)

    # Barra de rolagem
    scrollbar = Scrollbar(frame_tabela)
    scrollbar.pack(side="right", fill="y")

    # Tabela para exibir reservas
    tabela = Treeview(frame_tabela, columns=("ID", "Usuário", "Data/Hora", "Estado"), show="headings",
                      yscrollcommand=scrollbar.set, height=15)
    tabela.heading("ID", text="ID da Reserva")
    tabela.heading("Usuário", text="ID do Usuário")
    tabela.heading("Data/Hora", text="Data e Hora")
    tabela.heading("Estado", text="Estado")
    tabela.column("ID", width=150, anchor="center")
    tabela.column("Usuário", width=150, anchor="center")
    tabela.column("Data/Hora", width=250, anchor="center")
    tabela.column("Estado", width=100, anchor="center")
    tabela.pack(side="left", fill="both", expand=True)
    scrollbar.config(command=tabela.yview)

    # Buscar reservas no banco de dados
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT r.ReservaID, r.UserID, r.Timestamp, r.EstadoID
            FROM tblReserva r
        """)
        reservas = cursor.fetchall()

        if not reservas:
            tabela.insert("", "end", values=("Nenhum", "Sem usuário", "Sem data", "Sem estado"))
        else:
            for reserva in reservas:
                tabela.insert("", "end", values=(reserva[0], reserva[1], reserva[2], reserva[3]))
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao buscar reservas: {e}")
        return

    def confirmar_exclusao():
        """
        Função para confirmar a exclusão da reserva.
        """
        item_selecionado = tabela.selection()
        if not item_selecionado:
            messagebox.showerror("Erro", "Nenhuma reserva selecionada para exclusão!")
            return

        valores = tabela.item(item_selecionado, "values")
        reserva_id = valores[0]  # ID da reserva selecionada

        try:
            cursor = conn.cursor()

            # Excluir dependências na ordem correta
            cursor.execute(
                "DELETE FROM tblEquip_req WHERE ReqID IN (SELECT ReqID FROM tblRequisicao WHERE ReservaID = ?)",
                (reserva_id,))
            cursor.execute("DELETE FROM tblRequisicao WHERE ReservaID = ?", (reserva_id,))
            cursor.execute("DELETE FROM tblRes_equip WHERE ReservaID = ?", (reserva_id,))
            cursor.execute("DELETE FROM tblReserva WHERE ReservaID = ?", (reserva_id,))

            # Confirmar as alterações no banco de dados
            conn.commit()
            print(f"Reserva {reserva_id} excluída com sucesso!")
            tabela.delete(item_selecionado)  # Remove da tabela visível no tkinter
        except Exception as e:
            conn.rollback()
            print(f"Erro ao excluir reserva: {str(e)}")

    Button(janela, text="Excluir", width=20, font=("Arial", 12), command=confirmar_exclusao).pack(pady=20)


