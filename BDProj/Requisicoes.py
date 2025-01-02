from tkinter import Toplevel, Label, Button, Entry, messagebox, Frame
from tkinter.ttk import Treeview, Scrollbar
import datetime

def abrir_tela(conn):
    """
    Tela principal de CRUD para Requisições.
    """
    if conn is None:
        messagebox.showerror("Erro", "Conexão com o banco de dados não está configurada.")
        return

    tela_requisicoes = Toplevel()
    tela_requisicoes.title("Gestão de Requisições")
    tela_requisicoes.geometry("600x400")

    Label(tela_requisicoes, text="Gestão de Requisições", font=("Arial", 16, "bold")).pack(pady=10)

    Button(tela_requisicoes, text="Criar Requisição", width=25, font=("Arial", 14),
           command=lambda: criar_requisicao(conn)).pack(pady=5)
    Button(tela_requisicoes, text="Visualizar Requisições", font=("Arial", 14), width=25,
           command=lambda: visualizar_requisicoes(conn)).pack(pady=5)
    Button(tela_requisicoes, text="Alterar Requisição", font=("Arial", 14), width=25,
           command=lambda: atualizar_requisicao(conn)).pack(pady=5)
    Button(tela_requisicoes, text="Excluir Requisição", font=("Arial", 14), width=25,
           command=lambda: excluir_requisicao(conn)).pack(pady=5)


def criar_requisicao(conn):
    """
    Janela para criar uma nova requisição.
    """
    if conn is None:
        messagebox.showerror("Erro", "Conexão com o banco de dados não está configurada.")
        return

    # Janela de criação
    janela = Toplevel()
    janela.title("Criar Requisição")
    janela.geometry("800x600")

    Label(janela, text="Criar Nova Requisição", font=("Arial", 16, "bold")).pack(pady=10)

    # Frame da tabela (Treeview)
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

    # Buscar equipamentos disponíveis no banco e preencher a tabela
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

    # Função para confirmar a criação da requisição
    def confirmar_requisicao():
        """
        Confirmar a criação da requisição:
        1. Cria a reserva.
        2. Adiciona o equipamento na tabela tblRes_equip.
        3. Cria a requisição.
        4. Associa o equipamento na tabela tblEquip_req.
        """
        # Captura de valores
        item_selecionado = tabela.selection()
        if not item_selecionado:
            messagebox.showerror("Erro", "Nenhum equipamento selecionado!")
            return

        equipamento_id = tabela.item(item_selecionado, "values")[0]  # EquipID
        usuario_id = entrada_usuario.get()

        if not usuario_id:
            messagebox.showerror("Erro", "O campo ID do Usuário é obrigatório!")
            return

        try:
            cursor = conn.cursor()

            # Criar reserva
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


            # Inserir dado na tabela tblRes_equip
            print("Vinculando equipamento à reserva...")
            cursor.execute("""
                INSERT INTO tblRes_equip (ReservaID, EquipID, Necessario)
                VALUES (?, ?, 1);
            """, (reserva_id, equipamento_id))

            # Criar uma nova requisição vinculada à reserva
            print("Criando requisição no banco de dados...")
            cursor.execute("""
                INSERT INTO tblRequisicao (ReservaID, UserID, EstadoID, DataRetirada)
                VALUES (?, ?, ?, GETDATE());
            """, (reserva_id, usuario_id, 1))  # Estado padrão = 1

            # Obter o ReqID da requisição recém-criada
            cursor.execute("""
                SELECT TOP 1 ReqID
                FROM tblRequisicao
                WHERE UserID = ?
                ORDER BY DataRetirada DESC;
            """, (usuario_id,))
            requisicao_id = cursor.fetchone()[0]

            if not requisicao_id:
                raise Exception("Erro ao criar a requisição. Nenhum ReqID foi retornado.")

            # Inserir o equipamento na tabela tblEquip_req vinculado à requisição
            print("Vinculando equipamento à requisição...")
            cursor.execute("""
                INSERT INTO tblEquip_req (ReqID, EquipID, Equip_estado)
                VALUES (?, ?, ?);
            """, (requisicao_id, equipamento_id, 1))  # Equip_estado = 1 (Ajustável)

            # Commit de todas as operações no banco
            conn.commit()

            # Feedback ao usuário
            messagebox.showinfo("Sucesso", f"Requisição criada com sucesso!\nReqID: {requisicao_id}")
            janela.destroy()

        except Exception as e:
            conn.rollback()  # Reverter alterações em caso de falha
            print(f"Erro ao criar requisição: {str(e)}")
            messagebox.showerror("Erro", f"Erro ao criar requisição: {e}")

    # Botão de confirmar requisição
    Button(janela, text="Confirmar Requisição", font=("Arial", 12), width=20, command=confirmar_requisicao).pack(
        pady=20)


def visualizar_requisicoes(conn):
    """
    Exibir todas as requisições em uma tabela, mostrando o nome do estado.
    """
    janela = Toplevel()
    janela.title("Visualizar Requisições")
    janela.geometry("800x400")

    Label(janela, text="Lista de Requisições", font=("Arial", 16, "bold")).pack(pady=10)

    frame_tabela = Frame(janela)
    frame_tabela.pack(pady=10)

    scrollbar = Scrollbar(frame_tabela)
    scrollbar.pack(side="right", fill="y")

    tabela = Treeview(frame_tabela, columns=("ID", "ReservaID", "UserID", "Estado", "DataRetirada", "Timestamp"),
                      show="headings", yscrollcommand=scrollbar.set)
    tabela.heading("ID", text="ReqID")
    tabela.heading("ReservaID", text="ReservaID")
    tabela.heading("UserID", text="UserID")
    tabela.heading("Estado", text="Estado")  # Substituímos EstadoID por Estado (Nome)
    tabela.heading("DataRetirada", text="DataRetirada")
    tabela.column("ID", width=50, anchor="w")
    tabela.column("ReservaID", width=150, anchor="w")
    tabela.column("UserID", width=100, anchor="w")
    tabela.column("Estado", width=100, anchor="w")
    tabela.column("DataRetirada", width=150, anchor="w")
    tabela.pack(side="left", fill="both", expand=True)
    scrollbar.config(command=tabela.yview)

    try:
        cursor = conn.cursor()
        # Buscando o nome no lugar do ID
        cursor.execute("""
            SELECT r.ReqID, r.ReservaID, r.UserID, e.Nome AS Estado, r.DataRetirada
            FROM tblRequisicao r
            JOIN tblEstado e ON r.EstadoID = e.EstadoID
        """)
        requisicoes = cursor.fetchall()

        for req in requisicoes:
            tabela.insert("", "end", values=(req[0], req[1], req[2], req[3], req[4]))
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao carregar requisições: {e}")



def atualizar_requisicao(conn):
    """
    Janela para atualizar dados de uma requisição.
    """
    janela = Toplevel()
    janela.title("Atualizar Requisição")
    janela.geometry("800x450")

    Label(janela, text="Atualizar Requisição", font=("Arial", 16, "bold")).pack(pady=10)

    frame_tabela = Frame(janela)
    frame_tabela.pack(fill="x", pady=10)

    scrollbar = Scrollbar(frame_tabela)
    scrollbar.pack(side="right", fill="y")

    tabela = Treeview(frame_tabela, columns=("ID", "ReservaID", "UserID", "EstadoID", "DataRetirada"),
                      show="headings", yscrollcommand=scrollbar.set)
    tabela.heading("ID", text="ReqID")
    tabela.heading("ReservaID", text="ReservaID")
    tabela.heading("UserID", text="UserID")
    tabela.heading("EstadoID", text="EstadoID")
    tabela.heading("DataRetirada", text="DataRetirada")
    tabela.column("ID", width=50, anchor="w")
    tabela.column("ReservaID", width=150, anchor="w")
    tabela.column("UserID", width=100, anchor="w")
    tabela.column("EstadoID", width=100, anchor="w")
    tabela.column("DataRetirada", width=150, anchor="w")

    tabela.pack(side="left", fill="both", expand=True)
    scrollbar.config(command=tabela.yview)

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT ReqID, ReservaID, UserID, EstadoID, DataRetirada FROM tblRequisicao")
        requisicoes = cursor.fetchall()

        for req in requisicoes:
            tabela.insert("", "end", values=(req[0], req[1], req[2], req[3], req[4]))
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao carregar requisições: {e}")

    Label(janela, text="Novo EstadoID:", font=("Arial", 12)).pack(pady=10)
    entrada_estado_id = Entry(janela, width=40)
    entrada_estado_id.pack(pady=5)

    def confirmar_atualizacao():
        item_selecionado = tabela.selection()
        if not item_selecionado:
            messagebox.showerror("Erro", "Nenhuma requisição selecionada!")
            return

        valores = tabela.item(item_selecionado, "values")
        req_id = valores[0]
        novo_estado_id = entrada_estado_id.get()

        if not novo_estado_id:
            messagebox.showerror("Erro", "Insira um EstadoID válido!")
            return

        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE tblRequisicao SET EstadoID = ? WHERE ReqID = ?", (novo_estado_id, req_id))
            conn.commit()
            messagebox.showinfo("Sucesso", "Requisição atualizada com sucesso!")
            janela.destroy()
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Erro", f"Erro ao atualizar requisição: {e}")

    Button(janela, text="Confirmar Atualização", command=confirmar_atualizacao).pack(pady=10)


def excluir_requisicao(conn):
    """
    Janela para excluir uma requisição, exibindo todas as requisições em uma tabela e deletando
    suas dependências conforme necessário.
    """
    if conn is None:
        messagebox.showerror("Erro", "Conexão com o banco de dados não está configurada.")
        return

    # Janela de Exclusão de Requisição
    janela = Toplevel()
    janela.title("Excluir Requisição")
    janela.geometry("800x600")

    Label(janela, text="Excluir Requisição", font=("Arial", 16, "bold")).pack(pady=10)

    # Frame para a tabela de exibição
    frame_tabela = Frame(janela)
    frame_tabela.pack(fill="both", expand=True, pady=10)

    # Barra de rolagem e tabela
    scrollbar = Scrollbar(frame_tabela)
    scrollbar.pack(side="right", fill="y")

    tabela = Treeview(frame_tabela, columns=("ID", "ReservaID", "Usuário", "EstadoID", "DataRetirada"), show="headings",
                      yscrollcommand=scrollbar.set, height=15)
    tabela.heading("ID", text="ReqID")
    tabela.heading("ReservaID", text="ReservaID")
    tabela.heading("Usuário", text="ID do Usuário")
    tabela.heading("EstadoID", text="EstadoID")
    tabela.heading("DataRetirada", text="DataRetirada")
    tabela.column("ID", width=80, anchor="center")
    tabela.column("ReservaID", width=150, anchor="center")
    tabela.column("Usuário", width=100, anchor="center")
    tabela.column("EstadoID", width=100, anchor="center")
    tabela.column("DataRetirada", width=150, anchor="center")
    tabela.pack(side="left", fill="both", expand=True)
    scrollbar.config(command=tabela.yview)

    # Preencher a tabela com os dados de requisições
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ReqID, ReservaID, UserID, EstadoID, DataRetirada
            FROM tblRequisicao
        """)
        requisicoes = cursor.fetchall()

        if not requisicoes:
            tabela.insert("", "end", values=("Nenhum", "Nenhum dado", "Nenhum dado", "Nenhum dado", "Nenhum dado"))
        else:
            for req in requisicoes:
                tabela.insert("", "end", values=(req[0], req[1], req[2], req[3], req[4]))

    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao carregar requisições: {e}")
        return

    def confirmar_exclusao():
        """
        Função para confirmar a exclusão da requisição selecionada.
        """
        # Selecionar o item na tabela
        item_selecionado = tabela.selection()
        if not item_selecionado:
            messagebox.showerror("Erro", "Nenhuma requisição selecionada para exclusão!")
            return

        valores = tabela.item(item_selecionado, "values")
        req_id = valores[0]  # Obter o ReqID da requisição selecionada

        try:
            cursor = conn.cursor()

            # Excluir dependências relacionadas à requisição
            cursor.execute("DELETE FROM tblEquip_req WHERE ReqID = ?", (req_id,))
            cursor.execute("DELETE FROM tblRequisicao WHERE ReqID = ?", (req_id,))

            # Confirmar as alterações no banco
            conn.commit()
            messagebox.showinfo("Sucesso", f"Requisição {req_id} excluída com sucesso!")
            tabela.delete(item_selecionado)  # Remover a linha da tabela exibida

        except Exception as e:
            conn.rollback()  # Reverter mudanças em caso de erro
            messagebox.showerror("Erro", f"Erro ao excluir requisição: {e}")

    Button(janela, text="Excluir", width=20, font=("Arial", 12), command=confirmar_exclusao).pack(pady=20)



