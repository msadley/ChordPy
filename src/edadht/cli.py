from node_local import ChordNode
import socket
import os

def limpar_tela():
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

def menu():
    mensagem = ["=======================",
                " Bem-vindo ao CHORDPY!",
                "=======================",
                "",
                "1. Imprimir Endereço",
                "2. Conectar à uma Rede",
                "3. Inserir valor",
                "4. Buscar Valor",
                ""]
    for linha in mensagem:
        print(linha)    
   
def main():
    limpar_tela()
    ip = get_local_ip()
    while True:
        limpar_tela()
        menu()
        escolha = input("Digite o número da sua escolha: ")
        match escolha:
            case "1":
                print(f"Seu IP é {ip}\n")
                input("Pressione Enter para continuar...")
                
if __name__ == '__main__':
    main()