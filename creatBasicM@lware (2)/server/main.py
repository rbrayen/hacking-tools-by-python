

import socket
import threading

HOST = "0.0.0.0"
PORT = 5000


def handle_client(client_socket: socket.socket, client_address: tuple[str, int]) -> None:
    print(f"[+] Nouvelle connexion depuis {client_address}")
    try:
        while True:
            data = client_socket.recv(4096)
            if not data:
                break

            message = data.decode("utf-8").strip()
            if not message:
                continue

            print(f"[{client_address}] {message}")
            if message.lower() == "quit":
                client_socket.sendall(b"Connexion ferm\u00e9e par le serveur.")
                break

            response = f"Echo: {message}"
            client_socket.sendall(response.encode("utf-8"))
    except ConnectionResetError:
        print(f"[-] Connexion interrompue par {client_address}")
    finally:
        client_socket.close()
        print(f"[-] Déconnexion de {client_address}")


def main() -> None:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        print(f"[*] Serveur en écoute sur {HOST}:{PORT}")

        while True:
            client_socket, client_address = server_socket.accept()
            thread = threading.Thread(target=handle_client, args=(client_socket, client_address), daemon=True)
            thread.start()
    except KeyboardInterrupt:
        print("\n[!] Arrêt du serveur")
    finally:
        server_socket.close()


if __name__ == "__main__":
    main()


