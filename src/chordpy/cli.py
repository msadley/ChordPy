import os

from typing import Tuple
from controller import ChordController


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def print_menu() -> None:
    entries = [
        "=======================",
        " Bem-vindo ao CHORDPY!",
        "=======================",
        "",
        "1. Iniciar Rede",
        "2. Conectar a uma Rede",
        "3. Sair",
        "",
    ]
    for line in entries:
        print(line)


def menu(chord: ChordController) -> None:
    while True:
        clear_screen()
        print_menu()

        choice = input("Digite o número da sua escolha: ")

        match choice:
            case "1":
                chord.start_network()
                menu_network(chord)
                input("\nPressione Enter para voltar...")
            case "2":
                address = input(">")
                join = chord.join_network(address)
                print(join["message"])

            case "3":
                print("Encerrando...")
                chord.stop()


def menu_network(chord: ChordController) -> None:
    while True:
        clear_screen()
        print_menu_network()

        choice = input("Digite o número da sua escolha: ")

        match choice:
            case "1":
                print(f"Seu endereço é {chord.get_address()}\n")
                input("Pressione Enter para continuar...")

            case "2":
                key, value = input("""
Insira o conjunto chave-valor a ser adicionado na rede 
utilizando o formato <chave> = <valor>:\n>""").split(" = ")
                chord.put(key, value)

            case "3":
                key = input("""
Insira o valor da chave a ser buscada:\n>""")
                print(chord.get(key))

            case "4":
                return


def print_menu_network() -> None:
    entries = [
        "=======================",
        "    Opções de Rede",
        "=======================",
        "",
        "1. Imprimir endereço",
        "2. Inserir Valor",
        "3. Buscar Valor",
        "4. Sair da Rede",
        "",
    ]
    for line in entries:
        print(line)
