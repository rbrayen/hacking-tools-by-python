

import socket

# 1. Création du socket TCP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 2. Récupération de l'adresse IP (sans .split())
# Astuce : Tu peux entrer '0.0.0.0' pour écouter sur toutes tes interfaces réseau
server_ip = "192.168.1.185"
socket_connect = (server_ip, 3001)

# 3. Liaison (Bind) du socket à l'adresse et au port
server_socket.bind(socket_connect)

# 4. Mise en écoute (jusqu'à 10 connexions en attente)
server_socket.listen(10)
print(f"[*] Serveur en écoute sur {server_ip}:3000...")

# 5. Acceptation de la connexion client
# On utilise client_socket pour ne pas écraser server_socket
client_socket, client_address = server_socket.accept()

print(f"[+] Connexion réussie avec le client : {client_address}")


# 6. Envoi du message (Correction ici : on utilise client_socket)
msg = "hhhhh "
client_socket.send(msg.encode())


