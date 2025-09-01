import os

from typing import Tuple
from chordpy.chord import Chord


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def print_menu() -> None:
    entries = [
        "=======================",
        " Bem-vindo ao CHORDPY!",
        "=======================",
        "",
        "1. Imprimir Endereço",
        "2. Conectar a uma Rede",
        "3. Inserir valor",
        "4. Buscar Valor",
        "5. Sair",
        "",
    ]
    for line in entries:
        print(line)


def menu(chord: Chord) -> None:
    while True:
        clear_screen()
        print_menu()

        choice = input("Digite o número da sua escolha: ")

        match choice:
            case "1":
                print(f"Seu IP é {chord.get_ip()}\n")
                input("Pressione Enter para continuar...")

            case "2":
                data = input("""
Insira o endereço e porta do par já iniciado na rede
utilizando o formato <endereço-ip>:<porta>\n>""").split(":")
                address: Tuple[str, int] = data[0], int(data[1])
                chord.join_network(address)

            case "3":
                key, value = input("""
Insira o conjunto chave-valor a ser adicionado na rede 
utilizando o formato <chave> = <valor>:\n>""").split(" = ")
                chord.put(key, value)
                
            case "4":
                key = input("""
Insira o valor da chave a ser buscada:\n>""")
                print(chord.get(key))
                
            case "5":
                print("Encerrando...")
                chord.stop()