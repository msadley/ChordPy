import socket
import os

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_local_ip():
    s = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 1))
        ip_local = s.getsockname()[0]
    except Exception as e:
        print(f"Não foi possível obter o IP: {e}")
        ip_local = socket.gethostbyname(socket.gethostname())
    finally:
        if s:
            s.close()
    return ip_local

def print_menu():
    entries = ["=======================",
                " Bem-vindo ao CHORDPY!",
                "=======================",
                "",
                "1. Imprimir Endereço",
                "2. Conectar à uma Rede",
                "3. Inserir valor",
                "4. Buscar Valor",
                ""]
    for line in entries:
        print(line)    
   
def menu():
    
    while True:
        clear_screen()
        print_menu()
        
        choice = input("Digite o número da sua escolha: ")
        
        match choice:            
            case "1":
                print(f"Seu IP é {get_local_ip()}\n")
                input("Pressione Enter para continuar...")
