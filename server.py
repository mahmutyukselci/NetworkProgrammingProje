import socket
import sys
import threading
import signal
import subprocess
import re
import os
import tkinter as tk
from tkinter import ttk
import functions
import time

HOST = '0.0.0.0'
PORT = 80
BUFFER_SIZE = 1024
FILE_BUFFER_SIZE = 4096  # 256 KB
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
    
def send_message():
    while True:
        try:
            if end_event.is_set():
                while True:
                    message = input("Do you want to reconnect? (y/n): ")
                    if message.lower() == 'n':
                         exit_program.set()
                         return
                    elif message.lower() == 'y':
                        return  
                    else:
                        print("Please enter only 'y' or 'n'.")
            else:
                message = input("Enter message: ")
                if end_event.is_set():
                    if message.lower() == 'y' or 'n':
                        if message.lower() == 'n':
                            exit_program.set()
                            return
                        elif message.lower() == 'y':
                            return  
                    else:
                        continue
                elif message.startswith("/acceptfile"):
                    _, save_path ,file_size = message.split()
                    message_pause_event.set()
                    time.sleep(0.1)
                    conn.send(message.encode())
                    functions.receive_file(conn,save_path,int(file_size))
                    message_pause_event.clear()
                elif message.startswith("/sendfile"):
                    _, file_path= message.split()
                    functions.send_file(file_path,conn,file_confirmation)
                    continue
                else:
                    conn.send(message.encode())
                    print(f"\033[32m{username}: {message}\033[0m")
        except:
            break
        
        
def receive_message():
    while not end_event.is_set():
        if message_pause_event.is_set():
            time.sleep(0.1)
            continue
        try:
            data = conn.recv(BUFFER_SIZE).decode()
            if not data:
                print("\nClient closed the connection.")
                print("\nDo you want to reconnect? (y/n)")
                end_event.set()
                break
            elif data.startswith("/sendfile"):
                _, file_name, file_size = data.split()
                file_size = int(file_size)
                print(f"{clientname} wants to send a file named '{file_name}' with size '{file_size}'. " f"To accept: /acceptfile <path> <size>,to reject type anything")
            elif data.startswith("/acceptfile"):
                file_confirmation.set()
            else:
                print(f"\n\033[31m{clientname}: {data}\033[0m")
        except:
            break
            
            
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
file_confirmation = threading.Event()
message_pause_event = threading.Event()

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