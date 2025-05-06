import socket
import sys
import threading
import signal
import os
import tkinter as tk
from tkinter import ttk
import time


FILE_BUFFER_SIZE = 4096  # 256 KB
    
def file_transfer_gui():
    window = tk.Tk()
    window.title("File Transfer")
    window.geometry("300x100")
    ttk.Label(window, text="Sending file...").pack(pady=10)
    progress = ttk.Progressbar(window, length=250, mode='determinate')
    progress.pack(pady=10)
    window.update()
    return window, progress
    
def send_file(file_path, target_conn,file_confirmation):
    if not os.path.exists(file_path):
        print("File not found.")
        return
    
    file_size = os.path.getsize(file_path)
    file_name = os.path.basename(file_path)

    # First send request to receiver
    target_conn.send(f"/sendfile {file_name} {file_size}".encode())

    print(f"File sending request for '{file_name}' has been sent. Waiting for confirmation...")
    
        
    file_confirmation.wait()
    

    if file_confirmation.is_set():
        print("CONFIRMED!Transfer starting...")
    else:
        print("File transfer rejected!")
        return
    window, bar = file_transfer_gui()

    with open(file_path, 'rb') as f:
        sent = 0
        while True:
            chunk = f.read(FILE_BUFFER_SIZE)
            if not chunk:
                break
            target_conn.send(chunk)
            sent += len(chunk)
            bar['value'] = (sent / file_size) * 100
            window.update()
    
    window.destroy()
    file_confirmation.clear()
    print("File transfer completed.")

        
def receive_file(conn, save_path, file_size):
    print("Receiving file...")
    with open(save_path, 'wb') as f:
        received = 0
        while received < file_size:
            chunk = conn.recv(min(FILE_BUFFER_SIZE, file_size - received))
            if not chunk:
                break
            f.write(chunk)
            received += len(chunk)
    print(f"File received: {save_path}")