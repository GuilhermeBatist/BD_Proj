import pyodbc
from tkinter import Tk, Button, messagebox, Label
import Reservas
import Requisicoes
import Equipamentos


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Menu Principal")

        # Configurações da janela principal
        self.root.geometry("400x400")

        # Texto grande "Gestão de Equipamentos"
        Label(root, text="Gestão de Equipamentos", font=("Arial", 20, "bold")).pack(pady=10)

        # Botões do menu com texto maior
        Button(root, text="Reservas", command=self.menu_reservas, width=20, font=("Arial", 14)).pack(pady=10)
        Button(root, text="Requisições", command=self.menu_requisicoes, width=20, font=("Arial", 14)).pack(pady=10)
        Button(root, text="Equipamentos", command=self.menu_equipamentos, width=20, font=("Arial", 14)).pack(pady=10)

        # Conexão com a base de dados
        self.conn = None
        self.cursor = None
        self.ligar_a_bd()

    def ligar_a_bd(self):
        try:
            ip = "192.168.100.14"
            user = "User_BD_PL4_01"
            password = "diubi:2024!BD!PL4_01"
            database = "BD_PL4_01"

            self.conn = pyodbc.connect(
                f"DRIVER={{SQL Server}};"
                f"SERVER={ip};"
                f"DATABASE={database};"
                f"UID={user};"
                f"PWD={password}")
            self.cursor = self.conn.cursor()
            messagebox.showinfo("Sucesso", "Ligação efetuada com sucesso a BD_PL4_01!")
        except Exception as e:
            messagebox.showerror("Erro na ligação", f"Erro no acesso à base de dados BD_PL4_01 : {e}")

    def menu_reservas(self):
        Reservas.abrir_tela(self.conn)

    def menu_requisicoes(self):
        Requisicoes.abrir_tela(self.conn)

    def menu_equipamentos(self):
        Equipamentos.abrir_tela(self.conn)


# Criação da aplicação
if __name__ == "__main__":
    root = Tk()
    app = App(root)
    root.mainloop()
