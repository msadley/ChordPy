from tkinter import Label, Button, Entry, Toplevel, PhotoImage, END, Tk
from tkinter import messagebox
from os.path import dirname, join
from controller import ChordController


class ChordGUI:
    def __init__(self, controller: ChordController):  # type: ignore
        self._controller = controller
        self.main_window = Tk()

        # CUSTOMIZAÇÃO DA JANELA
        self.main_window.geometry("430x370")
        self.main_window.title("ChordPy")
        self.main_window.config(background="#1f1f1f")

        self.icon = PhotoImage(file=join(dirname(__file__), "icon.png"))
        self.title = PhotoImage(file=join(dirname(__file__), "titulo.png"))
        self.main_window.iconphoto(True, self.icon)

        # TÍTULO
        window_title = Label(self.main_window, image=self.title, bg="#1f1f1f")
        window_title.pack()

        # BOTÕES
        print_adress_button = Button(
            self.main_window,
            text="Imprimir Endereço",
            font=("Liberation Mono", 20, "bold"),
            fg="black",
            command=self.imprimeEndereco,  ## Botão de imprimir endereço
        )

        connection_button = Button(
            self.main_window,
            text="Conectar a uma\nrede",
            font=("Liberation Mono", 20, "bold"),
            fg="black",
            command=self.connect_window,  # Local do erro
        )

        print_adress_button.pack(side="top", pady=30)
        connection_button.pack(side="top", pady=5)

    def start(self):
        self.main_window.mainloop()

    def imprimeEndereco(self):
        ip = self._controller.get_address()
        messagebox.showinfo("Endereço IP", f"Seu endereço é: {ip}")

    def value_search(self, key_entry: Entry, search_window: Toplevel):
        key = key_entry.get()
        key_entry.delete(0, END)

        response = self._controller.get(key)
        if response["success"]:
            messagebox.showinfo(
                title="Valor encontrado",
                message=f"O valor da chave '{key}' é: {response['value']}",
            )
            # self.third_window() ####    EDITADO PARA CHAMAR APROXIMA JANELA DO MENU: OPCOES DA REDE
        else:
            messagebox.showerror("Erro", response["message"])

        search_window.destroy()

    def value_insert(
        self, key_entry: Entry, value_entry: Entry, insert_window: Toplevel
    ):
        key = key_entry.get()
        value = value_entry.get()

        key_entry.delete(0, END)
        value_entry.delete(0, END)

        response = self._controller.put(key, value)
        if response["success"]:
            messagebox.showinfo("Sucesso", response["message"])
        else:
            messagebox.showerror("Erro", response["message"])

        insert_window.destroy()

    def buscar_valor(self):
        search_window = Toplevel()
        search_window.geometry("350x250")
        search_window.config(background="#1f1f1f")

        Label(
            search_window,
            text="Digite a chave:",
            font=("Liberation Mono", 20, "bold"),
            bg="#1f1f1f",
            fg="white",
            pady=20,
        ).pack()

        key_entry = Entry(search_window, bg="white", font=("Liberation Mono", 15))
        key_entry.pack(side="top")

        Button(  # Buscar valor
            search_window,
            text="Buscar",
            font=("Liberation Mono", 10, "bold"),
            command=lambda: self.value_search(
                key_entry, search_window
            ),  # MOMENTO QUE CHAMA A OUTRA INTERFACE
        ).pack(side="top", pady=2)

    def inserir_valor(self):
        insert_window = Toplevel()
        insert_window.geometry("350x250")
        insert_window.config(background="#1f1f1f")

        Label(
            insert_window,
            text="Inserir chave e valor:",
            font=("Liberation Mono", 20, "bold"),
            bg="#1f1f1f",
            fg="white",
        ).pack(padx=10, pady=10)

        Label(insert_window, text="Chave:", bg="#1f1f1f", fg="white").pack()
        key_entry = Entry(insert_window, font=("Liberation Mono", 15))
        key_entry.pack()

        Label(insert_window, text="Valor:", bg="#1f1f1f", fg="white").pack()
        value_entry = Entry(insert_window, font=("Liberation Mono", 15))
        value_entry.pack()

        Button(
            insert_window,
            text="Inserir",
            font=("Liberation Mono", 10, "bold"),
            command=lambda: self.value_insert(key_entry, value_entry, insert_window),
        ).pack()

    def join_network(self, address_entry: Entry, connection_window: Toplevel):
        address = address_entry.get()
        address_entry.delete(0, END)

        response = self._controller.join_network(address)
        if response["success"]:
            connection_window.destroy()
            self.wired_window()  # LOCAL DE CHAMAR O MENU DE REDE
        else:
            messagebox.showerror("Erro de conexão", response["message"])

    def connect_window(self):  # Verificar erros
        connection_window = Toplevel(self.main_window)
        connection_window.geometry("430x370")
        connection_window.title("ChordPy")
        connection_window.config(background="#1f1f1f")

        Label(
            connection_window,
            text="Conectar a uma rede",
            font=("Liberation Mono", 20, "bold"),
            bg="#1f1f1f",
            fg="white",
            pady=20,
        ).pack()

        address_entry = Entry(
            connection_window, bg="white", font=("Liberation Mono", 15)
        )
        address_entry.pack(side="top")

        Button(
            connection_window,
            text="Conectar",
            font=("Liberation Mono", 10, "bold"),
            command=lambda: self.join_network(address_entry, connection_window),
        ).pack(side="top", pady=2)

    def wired_window(self):  ## MENU DE CONEXAO
        # self.main_window.destroy()
        # self.connection_window = Tk()
        self.main_window.withdraw()

        self.connection_window = Toplevel(self.main_window)
        self.connection_window.geometry("437x375")
        self.connection_window.title("ChordPy Wired")
        self.connection_window.config(background="#1f1f1f")

        self.title = PhotoImage(file=join(dirname(__file__), "titulo.png"))

        Label(self.connection_window, image=self.title, background="#1f1f1f").pack(
            side="top"
        )

        Label(
            self.connection_window,
            text=f"Opções da Rede: {self._controller.get_address()}",
            font=("Liberation Mono", 20, "bold"),
            fg="white",
            bg="#1f1f1f",
            relief="flat",
        ).pack()

        Button(  # Botão de imprimir endereço
            self.connection_window,
            text="Imprimir Endereço",
            font=("Liberation Mono", 20, "bold"),
            bg="white",
            command=self.imprimeEndereco,
        ).pack(pady=10)

        Button(  # Botão de Inserir valor
            self.connection_window,
            text="Inserir valor",
            font=("Liberation Mono", 20, "bold"),
            bg="white",
            command=self.inserir_valor,
        ).pack(pady=10)

        Button(  # botão de buscar
            self.connection_window,
            text="Buscar valor",
            font=("Liberation Mono", 20, "bold"),
            bg="white",
            command=self.buscar_valor,
        ).pack(pady=20)

        # self.connection_window.mainloop()

    def third_window(self):  # MENU GATO DE CONEXÃO ADPTADO
        third_window = Toplevel(self.main_window)
        third_window.geometry("430x370")
        third_window.title("Opções de Rede")
        third_window.config(background="#1f1f1f")

        # título
        Label(
            third_window,
            text="Opções de Rede",
            font=("Liberation Mono", 20, "bold"),
            bg="#1f1f1f",
            fg="white",
            pady=20,
        ).pack()

        # botão 1
        Button(
            third_window,
            text="Inserir Valor",
            font=("Liberation Mono", 15, "bold"),
            bg="white",
            command=lambda: messagebox.showinfo("Ação 1", "Você clicou na ação 1!"),
        ).pack(pady=10)

        # botão 2
        Button(
            third_window,
            text="Buscar Valor",
            font=("Liberation Mono", 15, "bold"),
            bg="white",
            command=lambda: messagebox.showinfo("Ação 2", "Você clicou na ação 2!"),
        ).pack(pady=10)

        # botao 3
        Button(
            third_window,
            text="Sair da Rede",
            font=("Liberation Mono", 15, "bold"),
            bg="white",
            command=lambda: messagebox.showinfo("Ação 3", "Você clicou na ação 3!"),
        ).pack(pady=10)
