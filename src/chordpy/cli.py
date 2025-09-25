import os

from controller import ChordController
from logger import current_log_file


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
        print_menu()

        choice = input("Digite o número da sua escolha: ")

        match choice:
            case "1":
                chord.start_network()
                menu_network(chord)
            
            case "2":
                address = input(">")
                result = chord.join_network(address)
                if result["success"]:
                    menu_network(chord)
                else:
                    print(f"\nErro: {result['message']}")
                    input("Pressione Enter para continuar...")
                    clear_screen()
            
            case "3":
                print("Encerrando...")
                chord.stop()
            
            case _:
                print("Opção inválida")
                input("Pressione Enter para continuar...")
                clear_screen()


def menu_network(chord: ChordController) -> None:
    while True:
        clear_screen()
        print_menu_network()

        choice = input("Digite o número da sua escolha: ")

        match choice:
            case "1":
                print(f"Seu endereço é {chord.get_address()}\n")
                input("Pressione Enter para continuar...")
                clear_screen()

            case "2":
                try:
                    user_input = input("""
Insira o conjunto chave-valor a ser adicionado na rede 
utilizando o formato <chave> = <valor>:\n>""")
                    print()
                    if " = " not in user_input:
                        print("Formato inválido! Use o formato: <chave> = <valor>")
                        input("Pressione Enter para continuar...")
                        clear_screen()
                        continue
                    part = user_input.split(" = ", 1)
                    key, value = part
                    if not key or not value:
                        print("Chave e valor não podem estar vazios!")
                        input("Pressione Enter para continuar...")
                        clear_screen()
                        continue
                    
                    result = chord.put(key, value)
                    if result["success"]:
                        input("Valor adicionado\nPressione Enter para continuar...")
                    else:
                        if "não reachable" in result["message"] or "timed out" in result["message"]:
                            print(f"ERRO DE CONEXÃO: {result['message']}")
                        else:
                            print(f"Falha ao adicionar o valor: {result['message']}")
                        input("Pressione Enter para continuar...")
                    
                except Exception as e:
                    print(f"Erro ao processar entrada: {e}")
                    input("Pressione Enter para continuar...")
    
                clear_screen()

            case "3":
                key = input("\nInsira a chave a ser buscada:\n>")
                result = chord.get(key)
                if result["success"]:
                    print(f"{key} = {result['value']}\n(Armazenado no nó: {result['node']})")
                    if "history" in result:
                        print("Histórico de busca:")
                        for entry in result["history"]:
                            print(f" - {entry}")
                    else:
                        print("\nChave não encontrada.")
                    
                input("\nPressione Enter para continuar...")
                clear_screen()

            case "4":
                clear_screen()
                return

            case "5":
                neighbors = chord.getNeighbors()
                if neighbors["success"]:
                    print(
                        f"Vizinhos:\nAnterior: {neighbors['prev']}\nPróximo: {neighbors['next']}\n"
                    )
                    input("Pressione Enter para continuar...")
                    clear_screen()

            case "6":
                local_dict = chord.getLocalDict()
                if local_dict["success"]:
                    print("Dicionário Local:")
                    for k, v in local_dict["data"].items():
                        print(f"{k}: {v}")
                    print()
                    input("Pressione Enter para continuar...")
                    clear_screen()
                else:
                    print(f"Erro: {local_dict['message']}\n")
                    input("Pressione Enter para continuar...")
                    clear_screen()

            case "7":
                finger_table = chord.getFingerTable()
                if finger_table["success"]:
                    print("Finger Table:")
                    for i, addr in finger_table["finger_table"].items():
                        print(f"{i}: {addr}")
                    print()
                    input("Pressione Enter para continuar...")
                    clear_screen()
                else:
                    print(f"Erro: {finger_table['message']}\n")
                    input("Pressione Enter para continuar...")
                    clear_screen()
                    
            case "8":
                print(f"ID do Nó: {chord.getId()}\n")
                input("Pressione Enter para continuar...")
                clear_screen()

            case "9":
                log()
                
            # Adicionado caso default para opções inválidas
            case _:
                print("Opção inválida")
                input("Pressione Enter para continuar...")
                clear_screen()


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
        "9. Ver Log",
        "",
    ]
    for line in entries:
        print(line)


def log() -> None:
    try:
        clear_screen()
        
        with open(current_log_file, "r") as log_file:
            log_content = log_file.read()
            print("\n=== LOG ===\n")
            print(log_content)
            print("\n=====================\n")
            input("Pressione Enter para continuar...")
            clear_screen()
    except Exception as e:
        print(f"Erro ao ler o arquivo de log: {e}")
        input("Pressione Enter para continuar...")
        clear_screen()
