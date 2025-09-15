from tkinter import *
from tkinter import messagebox
    
def value_search(value_entry: Entry):
    value = value_entry.get()
    value_entry.delete(0, END)
    messagebox.showinfo(title="Ops!",
                        message="Valor não encontrado") 
    #TODO

def value_insert(insert_entry: Entry, insert_window: Toplevel):
    value = insert_entry.get()
    insert_entry.delete(0, END)
    messagebox.showinfo(title="Ops!",
                        message="Inserção falhou") 
    #TODO


def buscar_valor():
    search_window = Toplevel()
    search_window.geometry("350x250")
    search_window.config(background='#1f1f1f')

    title_label = Label(search_window,
                        text="Digite o valor:",
                        font=('Liberation Mono', 20, 'bold'),
                        bg='#1f1f1f',
                        fg='white',
                        pady=20)
    
    title_label.pack()

    value_entry = Entry(search_window,
                        bg='white',
                        font=('Liberation Mono', 15))

    value_entry.pack(side='top')

    submit_button = Button(search_window,
                           text="Buscar",
                           font=('Liberation Mono',10 ,'bold'),
                           command=lambda: value_search(value_entry))
    
    submit_button.pack(side='top',
                       pady=2)

def inserir_valor():
    insert_window = Toplevel()
    insert_window.geometry("350x250")
    insert_window.config(background='#1f1f1f')

    insert_title = Label(insert_window,
                         text="Inserir valor:",
                         font=('Liberation Mono', 20, 'bold'),
                         bg = '#1f1f1f',
                         fg = 'white')

    insert_title.pack(padx=10, pady=10)

    insert_entry = Entry(insert_window,
                         font=('Liberation Mono', 15))
    
    insert_entry.pack()

    insert_button = Button(insert_window,
                           text="Buscar",
                           font=('Liberation Mono',10 ,'bold'),
                           command=lambda: value_insert(insert_entry, insert_window))
    
    insert_button.pack()
    

def imprimeEndereco():
    adress_window = Toplevel(main_window)
    adress_window.title("Seu endereço")
    adress_window.config(background='#1f1f1f')
    
    adress = Label(adress_window,
                   text=f"Seu endereço é: [...]",
                   font=('Liberation Mono', 20, 'bold'),
                   fg='#ffffff',
                   bg='#1f1f1f')
    
    adress.pack()

def connect_window():
    main_window.destroy()
    connection_window = Tk() 

    connection_window.geometry("437x375")
    connection_window.title("ChordPy Wired")
    connection_window.config(background='#1f1f1f')

    title = PhotoImage(file='src/chordpy/titulo.png')

    connection_window_title = Label(connection_window,
                                   image=title,
                                   background='#1f1f1f')
    
    connection_window_title.pack(side='top')

    adress_label = Label(connection_window,
                         text="Rede: [...]",
                         font=('Liberation Mono', 20, 'bold'),
                         fg='white',
                         bg='#1f1f1f',
                         relief='flat')

    adress_label.pack()    
    
    buscar_valor_button = Button(connection_window,
                                 text='Buscar valor',
                                 font = ('Liberation Mono', 20, 'bold'),
                                 bg='white',
                                 command=buscar_valor)
    
    buscar_valor_button.pack(pady=20)

    inserir_valor_button = Button(connection_window,
                                  text="Inserir valor",
                                  font=('Liberation Mono', 20, 'bold'),
                                  bg='white',
                                  command=inserir_valor)
    
    inserir_valor_button.pack(pady=10)

    connection_window.mainloop()

main_window = Tk()


# CUSTOMIZAÇÃO DA JANELA
main_window.geometry("430x370")


icon = PhotoImage(file='src/chordpy/icon.png')
main_window.title("ChordPy")
main_window.iconphoto(True, icon)
main_window.config(background='#1f1f1f')

# WIDGETS

title = PhotoImage(file='src/chordpy/titulo.png')

window_title = Label(main_window,
                    image=title,
                    bg='#1f1f1f')

window_title.pack()

#BOTÕES

print_adress_button = Button(main_window,
                            text='Imprimir Endereço',
                            font=('Liberation Mono', 20, 'bold'),
                            fg='black',
                            command=imprimeEndereco)


conecction_button = Button(main_window,
                        text = 'Conectar a uma\nrede',
                        font=('Liberation Mono', 20, 'bold'),
                        fg='black',
                        command=connect_window)

print_adress_button.pack(side='top', pady=30)
conecction_button.pack(side='top',pady=5)


main_window.mainloop()