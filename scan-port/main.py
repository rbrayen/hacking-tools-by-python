import socket

host = input("Adresse IP ou domaine : ")

start_port = int(input("Port de début : "))
end_port = int(input("Port de fin : "))

print(f"\nScan de {host}...\n")

for port in range(start_port, end_port + 1):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.5)

    result = sock.connect_ex((host, port))

    if result == 0:
        print(f"[+] Port {port} ouvert")

    sock.close()

print("\nScan terminé.")
