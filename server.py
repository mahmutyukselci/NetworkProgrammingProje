import socket
import sys
import threading
import signal
import subprocess
import re


HOST = '0.0.0.0'
PORT = 80
BUFFER_SIZE = 1024
username = '[SERVER] ' + socket.gethostname()
clientname = ''
def signal_handler(sig, frame):
    print("\nServer shutting down...")
    try:
        subprocess.call(["taskkill", "/f", "/im", "ngrok.exe"])
        conn.close()
        server_socket.close()
    except:
        pass
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def create_ngrok_tcp_tunnel(port):
    print("Activating TCP tunnel...")
    command = ["ngrok", "tcp", str(port), "--log=stdout"]
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    for line in proc.stdout:
        if "msg=\"started tunnel\"" in line and "url=tcp://" in line:
            match = re.search(r'url=tcp://(.+?):(\d+)', line)
            if match:
                print("Success!")
                host, forwarded_port = match.groups()
                print(f"[NGROK] Connection address: {host}, Port: {forwarded_port}")
                return 1
        elif "ERR" in line or "error" in line:
            print("[NGROK] Error: " + line.strip())
    
    return 
        
create_ngrok_tcp_tunnel(PORT)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()
print(f"Server started. Listening on port {PORT}...")

conn, addr = server_socket.accept()
print(f"Connection received: {addr}")

clientname = conn.recv(BUFFER_SIZE).decode()
conn.send(username.encode())

end_event = threading.Event()
exit_program = threading.Event()


def receive_message():
    while True:
        try:
            data = conn.recv(BUFFER_SIZE).decode()
            if not data:
                print("\nClient closed the connection.")
                print("\nDo you want to reconnect? (y/n)")
                end_event.set()
                break
            print(f"\n\033[31m{clientname}: {data}\033[0m")
        except:
            break
def send_message():
    while True:
        try:
            if end_event.is_set():
                while True:
                    answer = input("Do you want to reconnect? (y/n): ")
                    if answer.lower() == 'n':
                         exit_program.set()
                         return
                    elif answer.lower() == 'y':
                        return  
                    else:
                        print("Please enter only 'y' or 'n'.")
            else:
                answer = input("Enter message: ")
                if end_event.is_set():
                    if answer.lower() == 'y' or 'n':
                        if answer.lower() == 'n':
                            exit_program.set()
                            return
                        elif answer.lower() == 'y':
                            return  
                    else:
                        continue
                conn.send(answer.encode())
                print(f"\033[32m{username}: {answer}\033[0m")
        except:
            break


def accept_connection():
    global conn, clientname, t_receive, t_send
    end_event.clear()
    server_socket.listen()
    print(f"Server started. Listening on port {PORT}...")
    conn, addr = server_socket.accept()
    print(f"Connection received: {addr}")
    clientname = conn.recv(BUFFER_SIZE).decode()
    conn.send(username.encode())

    t_receive = threading.Thread(target=receive_message)
    t_receive.start()
    t_send = threading.Thread(target=send_message)
    t_send.start()
    


t_receive=threading.Thread(target=receive_message,)
t_receive.start()
t_send=threading.Thread(target=send_message,)
t_send.start()

while True:
    t_receive.join()
    t_send.join()
    if exit_program.is_set():
        subprocess.call(["taskkill", "/f", "/im", "ngrok.exe"])
        sys.exit(0)
    else:
        accept_connection()