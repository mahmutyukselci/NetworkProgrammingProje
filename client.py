import socket
import sys
import threading
import signal
import os
import tkinter as tk
from tkinter import ttk
import functions


def signal_handler(sig, frame):
    print("\nClient shutting down...")
    end_event.set()
    
signal.signal(signal.SIGINT, signal_handler)
if len(sys.argv) < 2:
    print("Usage: python client.py <IP:PORT>")
    sys.exit(1)
    
username = '[CLIENT]'+socket.gethostname()
servername = ''
input_address = sys.argv[1]  # Example: "0.tcp.ngrok.io:10942"
HOST, PORT = input_address.split(":")
PORT = int(PORT)  
BUFFER_SIZE = 1024


conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
conn.connect((HOST, PORT))
conn.send(username.encode())
servername = conn.recv(BUFFER_SIZE).decode()
print("Connection successful!")

end_event = threading.Event()
file_confirmation = threading.Event()
message_pause_event = threading.Event()

def send_message():
    while not end_event.is_set():
        try:
            message = input("Enter message: ")
            if message.startswith("/acceptfile"):
                _, save_path ,file_size = message.split()
                message_pause_event.set()
                time.sleep(0.1)
                conn.send(message.encode())
                functions.receive_file(conn,save_path,int(file_size))
                message_pause_event.clear()
            elif message.startswith("/sendfile"):
                _, file_path= message.split()
                functions.send_file(file_path,conn,file_confirmation)
            else:
                conn.send(message.encode())
                print(f"\n\033[32m{username}: {message}\033[0m")
        except:
            return
            
def receive_message():
    while not end_event.is_set():
        if message_pause_event.is_set():
            time.sleep(0.1)
            continue
        try:
            data = conn.recv(BUFFER_SIZE).decode()
            if data.startswith("/sendfile"):
                _, file_name, file_size = data.split()
                file_size = int(file_size)
                print(f"{servername} wants to send a file named '{file_name}'. " f"To accept: /acceptfile <path>,to reject type anything")
            elif data.startswith("/acceptfile"):
                file_confirmation.set()
            elif data:
                print(f"\n\033[31m{servername}: {data}\033[0m")
        except:
            return
            
t_send = threading.Thread(target=send_message,)
t_send.start()
t_receive = threading.Thread(target=receive_message,)
t_receive.start()

while True:
    if end_event.is_set():
        conn.close()
        sys.exit(0)