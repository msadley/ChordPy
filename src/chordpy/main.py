from gui import ChordGUI
from controller import ChordController
from cli import menu
import threading
import sys


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else None
    controller = ChordController(port)
    server_thread = threading.Thread(target=controller.start_server)
    server_thread.daemon = True
    server_thread.start()
    menu(controller)


if __name__ == "__main__":
    main()
