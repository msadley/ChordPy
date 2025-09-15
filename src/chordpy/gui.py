from tkinter import * # type: ignore
from tkinter import messagebox
from os.path import dirname, join


class ChordGUI:
    def __init__(self, node: "LocalNode") -> None: # type: ignore
        self.main_window = Tk()
        self._node = node

        # CUSTOMIZAÇÃO DA JANELA
        self.main_window.geometry("430x370")

        self.icon = PhotoImage(file=join(dirname(__file__), "icon.png"))
        self.main_window.title("ChordPy")
        self.main_window.iconphoto(True, self.icon)
        self.main_window.config(background="#1f1f1f")

        # WIDGETS

        self.title = PhotoImage(file=join(dirname(__file__), "titulo.png"))

        window_title = Label(self.main_window, image=self.title, bg="#1f1f1f")

        window_title.pack()

        # BOTÕES

        print_adress_button = Button(
            self.main_window,
            text="Imprimir Endereço",
            font=("Liberation Mono", 20, "bold"),
            fg="black",
            command=self.imprimeEndereco,
        )

        conecction_button = Button(
            self.main_window,
            text="Conectar a uma\nrede",
            font=("Liberation Mono", 20, "bold"),
            fg="black",
            command=self.connect_window,
        )

        print_adress_button.pack(side="top", pady=30)
        conecction_button.pack(side="top", pady=5)

    def start(self):
        self.main_window.mainloop()

    def value_search(self, key_entry: Entry, search_window: Toplevel):
        key = key_entry.get()
        key_entry.delete(0, END)

        value = self._node.get(key)

        if value:
            messagebox.showinfo(
                title="Valor encontrado", message=f"O valor da chave {key} é {value}"
            )
        else:
            messagebox.showinfo(title="Ops!", message="Valor não encontrado")

        search_window.destroy()

    def value_insert(
        self, key_entry: Entry, value_entry: Entry, insert_window: Toplevel
    ):
        key = key_entry.get()
        value = value_entry.get()

        key_entry.delete(0, END)
        value_entry.delete(0, END)

        self._node.put(key, value)

        messagebox.showinfo(title="Sucesso!", message="Inserção realizada com sucesso")

        insert_window.destroy()

    def buscar_valor(self):
        search_window = Toplevel()
        search_window.geometry("350x250")
        search_window.config(background="#1f1f1f")

        title_label = Label(
            search_window,
            text="Digite a chave:",
            font=("Liberation Mono", 20, "bold"),
            bg="#1f1f1f",
            fg="white",
            pady=20,
        )

        title_label.pack()

        key_entry = Entry(search_window, bg="white", font=("Liberation Mono", 15))

        key_entry.pack(side="top")

        submit_button = Button(
            search_window,
            text="Buscar",
            font=("Liberation Mono", 10, "bold"),
            command=lambda: self.value_search(key_entry, search_window),
        )

        submit_button.pack(side="top", pady=2)

    def inserir_valor(self):
        insert_window = Toplevel()
        insert_window.geometry("350x250")
        insert_window.config(background="#1f1f1f")

        insert_title = Label(
            insert_window,
            text="Inserir chave e valor:",
            font=("Liberation Mono", 20, "bold"),
            bg="#1f1f1f",
            fg="white",
        )

        insert_title.pack(padx=10, pady=10)

        key_label = Label(insert_window, text="Chave:", bg="#1f1f1f", fg="white")
        key_label.pack()
        key_entry = Entry(insert_window, font=("Liberation Mono", 15))

        key_entry.pack()

        value_label = Label(insert_window, text="Valor:", bg="#1f1f1f", fg="white")
        value_label.pack()
        value_entry = Entry(insert_window, font=("Liberation Mono", 15))

        value_entry.pack()

        insert_button = Button(
            insert_window,
            text="Inserir",
            font=("Liberation Mono", 10, "bold"),
            command=lambda: self.value_insert(key_entry, value_entry, insert_window),
        )

        insert_button.pack()

    def imprimeEndereco(self):
        messagebox.showinfo(
            title="Endereço IP", message=f"Seu endereço é: {self._node.get_ip()}"
        )

    def join_network(self, adress_entry: Entry, connection_window: Toplevel):
        adress = adress_entry.get()
        adress_entry.delete(0, END)

        ip, port = adress.split(":")
        self._node.join_network((ip, int(port)))

        connection_window.destroy()
        self.wired_window()

    def connect_window(self):
        connection_window = Toplevel(self.main_window)
        connection_window.geometry("430x370")
        connection_window.title("ChordPy")
        connection_window.config(background="#1f1f1f")

        title_label = Label(
            connection_window,
            text="Conectar a uma rede",
            font=("Liberation Mono", 20, "bold"),
            bg="#1f1f1f",
            fg="white",
            pady=20,
        )

        title_label.pack()

        adress_entry = Entry(
            connection_window, bg="white", font=("Liberation Mono", 15)
        )

        adress_entry.pack(side="top")

        submit_button = Button(
            connection_window,
            text="Conectar",
            font=("Liberation Mono", 10, "bold"),
            command=lambda: self.join_network(adress_entry, connection_window),
        )

        submit_button.pack(side="top", pady=2)

    def wired_window(self):
        self.main_window.destroy()
        self.connection_window = Tk()

        self.connection_window.geometry("437x375")
        self.connection_window.title("ChordPy Wired")
        self.connection_window.config(background="#1f1f1f")

        self.title = PhotoImage(file=join(dirname(__file__), "titulo.png"))

        connection_window_title = Label(
            self.connection_window, image=self.title, background="#1f1f1f"
        )

        connection_window_title.pack(side="top")

        adress_label = Label(
            self.connection_window,
            text=f"Rede: {self._node.get_ip()}",
            font=("Liberation Mono", 20, "bold"),
            fg="white",
            bg="#1f1f1f",
            relief="flat",
        )

        adress_label.pack()

        buscar_valor_button = Button(
            self.connection_window,
            text="Buscar valor",
            font=("Liberation Mono", 20, "bold"),
            bg="white",
            command=self.buscar_valor,
        )

        buscar_valor_button.pack(pady=20)

        inserir_valor_button = Button(
            self.connection_window,
            text="Inserir valor",
            font=("Liberation Mono", 20, "bold"),
            bg="white",
            command=self.inserir_valor,
        )

        inserir_valor_button.pack(pady=10)

        self.connection_window.mainloop()
