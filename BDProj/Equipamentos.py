from tkinter import Toplevel, Label, Button, Entry, messagebox, Frame
from tkinter.ttk import Treeview, Scrollbar


def abrir_tela(conn):
    """
    Função para abrir a tela principal de Equipamentos, recebendo a conexão com o banco como argumento.
    """
    if conn is None:
        messagebox.showerror("Erro", "Conexão com o banco de dados não está configurada.")
        return

    tela_equipamentos = Toplevel()
    tela_equipamentos.title("Equipamentos")
    tela_equipamentos.geometry("600x400")

    Label(tela_equipamentos, text="Gestão de Equipamentos", font=("Arial", 16, "bold")).pack(pady=10)
    Button(tela_equipamentos, text="Criar Equipamento", width=25, font=("Arial", 14),
           command=lambda: criar_equipamento(conn)).pack(pady=5)
    Button(tela_equipamentos, text="Visualizar Equipamentos", font=("Arial", 14), width=25,
           command=lambda: visualizar_equipamentos(conn)).pack(pady=5)
    Button(tela_equipamentos, text="Alterar Equipamento", font=("Arial", 14), width=25,
           command=lambda: atualizar_equipamento(conn)).pack(pady=5)
    Button(tela_equipamentos, text="Excluir Equipamento", font=("Arial", 14), width=25,
           command=lambda: excluir_equipamento(conn)).pack(pady=5)


def criar_equipamento(conn):
    """
    Janela para criar um novo equipamento.
    """
    if conn is None:
        messagebox.showerror("Erro", "Conexão com o banco de dados não está configurada.")
        return

    janela = Toplevel()
    janela.title("Criar Equipamento")
    janela.geometry("400x300")

    Label(janela, text="Criar Novo Equipamento", font=("Arial", 16, "bold")).pack(pady=10)

    Label(janela, text="Descrição:", font=("Arial", 12)).pack(pady=5)
    entrada_descricao = Entry(janela, width=30)
    entrada_descricao.pack(pady=5)

    Label(janela, text="Estado ID:", font=("Arial", 12)).pack(pady=5)
    entrada_estado_id = Entry(janela, width=30)
    entrada_estado_id.pack(pady=5)

    def confirmar_criacao():
        descricao = entrada_descricao.get()
        estado_id = entrada_estado_id.get()

        if not descricao or not estado_id:
            print("Erro: Campos obrigatórios não preenchidos para criar um equipamento.")
            messagebox.showerror("Erro", "Todos os campos devem ser preenchidos!")
            return

        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO tblEquipamento (Descricao, EstadoID) VALUES (?, ?)", (descricao, estado_id))
            conn.commit()
            print(f"Sucesso: Equipamento '{descricao}' criado com sucesso!")
            messagebox.showinfo("Sucesso", "Equipamento criado com sucesso!")
            janela.destroy()
        except Exception as e:
            conn.rollback()
            print(f"Erro ao criar equipamento: {e}")
            messagebox.showerror("Erro", f"Erro ao criar equipamento: {e}")

    Button(janela, text="Confirmar", command=confirmar_criacao).pack(pady=10)


def visualizar_equipamentos(conn):
    """
    Exibir todos os equipamentos em uma tabela, incluindo o Estado correspondente.
    """
    if conn is None:
        messagebox.showerror("Erro", "Conexão com o banco de dados não está configurada.")
        return

    # Janela para exibir equipamentos
    janela_visualizar = Toplevel()
    janela_visualizar.title("Visualizar Equipamentos")
    janela_visualizar.geometry("700x400")

    Label(janela_visualizar, text="Lista de Equipamentos", font=("Arial", 16, "bold")).pack(pady=10)

    frame_tabela = Frame(janela_visualizar)
    frame_tabela.pack(pady=10)

    # Barra de rolagem
    scrollbar = Scrollbar(frame_tabela)
    scrollbar.pack(side="right", fill="y")

    # Tabela Treeview
    tabela = Treeview(frame_tabela, columns=("ID", "Descrição", "Estado"), show="headings",
                      yscrollcommand=scrollbar.set)
    # Configuração das colunas
    tabela.heading("ID", text="ID", anchor="center")  # Título centralizado
    tabela.heading("Descrição", text="Descrição", anchor="center")  # Título centralizado
    tabela.heading("Estado", text="Estado", anchor="center")  # Título centralizado

    # Alinhar os dados à direita
    tabela.column("ID", width=100, anchor="w")  # Dados alinhados à direita
    tabela.column("Descrição", width=250, anchor="w")  # Dados alinhados à direita
    tabela.column("Estado", width=150, anchor="w")  # Dados alinhados à direita

    tabela.pack(side="left", fill="both", expand=True)

    scrollbar.config(command=tabela.yview)

    # Consulta os dados do banco
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT e.EquipID, e.Descricao, est.Nome
            FROM tblEquipamento e
            LEFT JOIN tblEstado est ON e.EstadoID = est.EstadoID
        """)
        equipamentos = cursor.fetchall()

        if not equipamentos:
            tabela.insert("", "end", values=("Nenhum", "Nenhum equipamento encontrado", ""))
        else:
            for equipamento in equipamentos:
                tabela.insert("", "end", values=(equipamento[0], equipamento[1], equipamento[2]))

    except Exception as e:
        print(f"Erro ao visualizar equipamentos: {e}")
        messagebox.showerror("Erro", f"Erro ao carregar equipamentos: {e}")


def atualizar_equipamento(conn):
    """
    Janela para atualizar um equipamento existente, exibindo todos os equipamentos em uma tabela.
    """
    if conn is None:
        messagebox.showerror("Erro", "Conexão com o banco de dados não está configurada.")
        return

    # Janela de Atualizar Equipamento
    janela = Toplevel()
    janela.title("Atualizar Equipamento")
    janela.geometry("800x600")

    Label(janela, text="Atualizar Equipamento", font=("Arial", 16, "bold")).pack(pady=10)

    # Frame para a tabela de equipamentos
    frame_tabela = Frame(janela)
    frame_tabela.pack(fill="both", expand=True, pady=10)

    # Barra de rolagem
    scrollbar = Scrollbar(frame_tabela)
    scrollbar.pack(side="right", fill="y")

    # Tabela para exibir equipamentos
    tabela = Treeview(frame_tabela, columns=("ID", "Descrição", "Estado"), show="headings",
                      yscrollcommand=scrollbar.set, height=15)
    tabela.heading("ID", text="ID do Equipamento")
    tabela.heading("Descrição", text="Descrição")
    tabela.heading("Estado", text="Estado")
    tabela.column("ID", width=150, anchor="center")
    tabela.column("Descrição", width=300, anchor="center")
    tabela.column("Estado", width=150, anchor="center")
    tabela.pack(side="left", fill="both", expand=True)
    scrollbar.config(command=tabela.yview)

    # Buscar equipamentos no banco de dados
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT e.EquipID, e.Descricao, est.Nome
            FROM tblEquipamento e
            LEFT JOIN tblEstado est ON e.EstadoID = est.EstadoID
        """)
        equipamentos = cursor.fetchall()

        if not equipamentos:
            tabela.insert("", "end", values=("Nenhum", "Nenhum equipamento cadastrado", ""))
        else:
            for equipamento in equipamentos:
                tabela.insert("", "end", values=(equipamento[0], equipamento[1], equipamento[2]))

    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao buscar equipamentos: {e}")
        return

    # Campo para atualizar informações
    Label(janela, text="Escolha o ID do equipamento na tabela acima e insira os novos valores abaixo:",
          font=("Arial", 12)).pack(pady=10)

    # Campo para nova descrição
    Label(janela, text="Nova Descrição:", font=("Arial", 12)).pack()
    entrada_nova_descricao = Entry(janela, width=50)
    entrada_nova_descricao.pack(pady=5)

    # Campo para novo estado (ID)
    Label(janela, text="Novo Estado (ID):", font=("Arial", 12)).pack()
    entrada_novo_estado = Entry(janela, width=30)
    entrada_novo_estado.pack(pady=5)

    def selecionar_equipamento_para_atualizar(event):
        """
        Função chamada ao selecionar um equipamento na tabela.
        """
        item_selecionado = tabela.selection()
        if item_selecionado:
            valores = tabela.item(item_selecionado, "values")
            entrada_nova_descricao.delete(0, "end")
            entrada_nova_descricao.insert(0, valores[1])  # Preenche com a descrição antiga
            entrada_novo_estado.delete(0, "end")
            entrada_novo_estado.insert(0, valores[2])  # Preenche com o estado antigo

    # Vincular clique na tabela à seleção do equipamento
    tabela.bind("<<TreeviewSelect>>", selecionar_equipamento_para_atualizar)

    def confirmar_atualizacao():
        """
        Atualizar o equipamento selecionado.
        """
        item_selecionado = tabela.selection()
        if not item_selecionado:
            messagebox.showerror("Erro", "Nenhum equipamento selecionado para atualizar!")
            return

        valores = tabela.item(item_selecionado, "values")
        equipamento_id = valores[0]  # ID do equipamento selecionado
        nova_descricao = entrada_nova_descricao.get()
        novo_estado = entrada_novo_estado.get()

        if not equipamento_id or not nova_descricao or not novo_estado:
            print("Erro: ID do equipamento, nova descrição ou novo estado está vazio.")
            messagebox.showerror("Erro", "Todos os campos devem ser preenchidos!")
            return

        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE tblEquipamento
                SET Descricao = ?, EstadoID = ?
                WHERE EquipID = ?
            """, (nova_descricao, novo_estado, equipamento_id))

            conn.commit()
            print(f"Equipamento {equipamento_id} atualizado com sucesso!")
            messagebox.showinfo("Sucesso", "Equipamento atualizado com sucesso!")
            janela.destroy()
        except Exception as e:
            conn.rollback()
            print(f"Erro ao atualizar equipamento: {e}")
            messagebox.showerror("Erro", f"Erro ao atualizar equipamento: {e}")

    Button(janela, text="Confirmar Atualização", width=20, font=("Arial", 12), command=confirmar_atualizacao).pack(
        pady=20)




def excluir_equipamento(conn):
    """
    Janela para excluir um equipamento existente, exibindo todos os equipamentos em uma tabela.
    """
    if conn is None:
        messagebox.showerror("Erro", "Conexão com o banco de dados não está configurada.")
        return

    # Janela de Excluir Equipamento
    janela = Toplevel()
    janela.title("Excluir Equipamento")
    janela.geometry("800x600")

    Label(janela, text="Excluir Equipamento", font=("Arial", 16, "bold")).pack(pady=10)

    # Frame para a tabela de equipamentos
    frame_tabela = Frame(janela)
    frame_tabela.pack(fill="both", expand=True, pady=10)

    # Barra de rolagem
    scrollbar = Scrollbar(frame_tabela)
    scrollbar.pack(side="right", fill="y")

    # Tabela para exibir equipamentos
    tabela = Treeview(frame_tabela, columns=("ID", "Descrição", "Estado"), show="headings",
                      yscrollcommand=scrollbar.set, height=15)
    tabela.heading("ID", text="ID do Equipamento")
    tabela.heading("Descrição", text="Descrição")
    tabela.heading("Estado", text="Estado")
    tabela.column("ID", width=150, anchor="center")
    tabela.column("Descrição", width=300, anchor="center")
    tabela.column("Estado", width=150, anchor="center")
    tabela.pack(side="left", fill="both", expand=True)
    scrollbar.config(command=tabela.yview)

    # Buscar equipamentos no banco de dados
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT e.EquipID, e.Descricao, est.Nome
            FROM tblEquipamento e
            LEFT JOIN tblEstado est ON e.EstadoID = est.EstadoID
        """)
        equipamentos = cursor.fetchall()

        if not equipamentos:
            tabela.insert("", "end", values=("Nenhum", "Nenhum equipamento cadastrado", ""))
        else:
            for equipamento in equipamentos:
                tabela.insert("", "end", values=(equipamento[0], equipamento[1], equipamento[2]))

    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao carregar equipamentos: {e}")
        return

    def confirmar_exclusao():
        """
        Função para confirmar a exclusão do equipamento selecionado.
        """
        item_selecionado = tabela.selection()
        if not item_selecionado:
            messagebox.showerror("Erro", "Nenhum equipamento selecionado para exclusão!")
            return

        valores = tabela.item(item_selecionado, "values")
        equipamento_id = valores[0]  # ID do equipamento selecionado

        try:
            cursor = conn.cursor()

            # Excluir dependências relacionadas ao equipamento antes de excluí-lo
            cursor.execute("DELETE FROM tblRes_equip WHERE EquipID = ?", (equipamento_id,))
            cursor.execute("DELETE FROM tblEquipamento WHERE EquipID = ?", (equipamento_id,))

            # Confirmar as alterações no banco de dados
            conn.commit()
            print(f"Equipamento {equipamento_id} excluído com sucesso!")
            messagebox.showinfo("Sucesso", f"Equipamento {equipamento_id} excluído com sucesso!")
            tabela.delete(item_selecionado)  # Remove o equipamento da tabela do tkinter GUI
        except Exception as e:
            conn.rollback()
            print(f"Erro ao excluir equipamento: {str(e)}")
            messagebox.showerror("Erro", f"Erro ao excluir equipamento: {e}")

    # Botão para confirmar a exclusão
    Button(janela, text="Excluir Equipamento", width=20, font=("Arial", 12), command=confirmar_exclusao).pack(pady=20)
