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
        # clear_screen()
        print_menu()

        choice = input("Digite o número da sua escolha: ")

        match choice:
            case "1":
                chord.start_network()
                menu_network(chord)
                input("\nPressione Enter para voltar...")
            case "2":
                address = input(">")
                chord.join_network(address)
                menu_network(chord)

            case "3":
                print("Encerrando...")
                chord.stop()


def menu_network(chord: ChordController) -> None:
    while True:
        # clear_screen()
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

            case "5":
                neighbors = chord.getNeighbors()
                if neighbors["success"]:
                    print(
                        f"Vizinhos:\nAnterior: {neighbors['prev']}\nPróximo: {neighbors['next']}\n"
                    )

            case "6":
                local_dict = chord.getLocalDict()
                if local_dict["success"]:
                    print("Dicionário Local:")
                    for k, v in local_dict["data"].items():
                        print(f"{k}: {v}")
                    print()
                else:
                    print(f"Erro: {local_dict['message']}\n")

            case "7":
                finger_table = chord.getFingerTable()
                if finger_table["success"]:
                    print("Finger Table:")
                    for i, addr in finger_table["finger_table"].items():
                        print(f"{i}: {addr}")
                    print()
                else:
                    print(f"Erro: {finger_table['message']}\n")
            case "8":
                print(f"ID do Nó: {chord.getId()}\n")


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
        "5. Obter Vizinhos",
        "6. Obter Dicionário Local",
        "7. Obter Finger Table",
        "8. Obter ID do Nó",
        "",
    ]
    for line in entries:
        print(line)
