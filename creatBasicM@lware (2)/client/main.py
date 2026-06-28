import socket
import sys

HOST = "127.0.0.1"
PORT = 5000


def main() -> None:
    if len(sys.argv) >= 3:
        host = sys.argv[1]
        port = int(sys.argv[2])
    else:
        host = HOST
        port = PORT

    try:
        with socket.create_connection((host, port), timeout=5) as client_socket:
            print(f"[+] Connecté à {host}:{port}")
            while True:
                message = input(">>> ").strip()
                if not message:
                    continue

                if message.lower() == "quit":
                    client_socket.sendall(message.encode("utf-8"))
                    break

                client_socket.sendall(message.encode("utf-8"))
                response = client_socket.recv(4096).decode("utf-8")
                print(response)
    except KeyboardInterrupt:
        print("\n[!] Déconnexion")
    except OSError as exc:
        print(f"[!] Erreur de connexion : {exc}")


if __name__ == "__main__":
    main()
