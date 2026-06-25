import socket 


client_socket = socket.socket(socket.AF_INET , socket.SOCK_STREAM)

server_ip = "192.168.1.185"
server_port = 3001

server_addr  =(server_ip,server_port)
client_socket.connect(server_addr) 
data = client_socket.recv(1024) 
dt = data.decode()
print(dt)