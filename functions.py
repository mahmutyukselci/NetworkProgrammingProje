import socket
import sys
import threading
import signal
import os
import tkinter as tk
from tkinter import ttk
import time


FILE_BUFFER_SIZE = 4194304 #4 MB
    
def file_transfer_gui():
    window = tk.Tk()
    window.title("File Transfer")
    window.geometry("400x120")

    bar = ttk.Progressbar(window, orient="horizontal", length=300, mode="determinate")
    bar.pack(pady=20)

    speed_label = tk.Label(window, text="Speed: 0.00 MB/s")
    speed_label.pack()

    return window, bar, speed_label
    
def send_file(file_path, target_conn,file_confirmation):
    if not os.path.exists(file_path):
        print("File not found.")
        return
    
    file_size = os.path.getsize(file_path)
    file_name = os.path.basename(file_path)

    target_conn.send(f"/sendfile {file_name} {file_size}".encode())

    print(f"File sending request for '{file_name}' has been sent. Waiting for confirmation...")
    
    file_confirmation.wait()
   
    if file_confirmation.is_set():
        print("CONFIRMED!Transfer starting...")
    else:
        print("File transfer rejected!")
        return
    window, bar, speed_label = file_transfer_gui()
    
    time.sleep(1)

    with open(file_path, 'rb') as f:
        sent = 0
        
        start_time = time.time()
        last_report_time = start_time
        sent_since_last_report = 0
        
        while True:
            chunk = f.read(FILE_BUFFER_SIZE)
            if not chunk: 
                break
            target_conn.sendall(chunk)
            sent += len(chunk)
            sent_since_last_report += len(chunk)
            bar['value'] = (sent / file_size) * 100
            
            current_time = time.time()
            
            if current_time - last_report_time >= 1.0:
                speed = (sent_since_last_report / 1024 / 1024) / (current_time - last_report_time)
                speed_label.config(text=f"Speed: {speed:.2f} MB/s")
                last_report_time = current_time
                sent_since_last_report = 0
                
            window.update()

    window.destroy()
    file_confirmation.clear()
    print("File transfer completed.")
    total_time = time.time() - start_time
    average_speed = (file_size / 1024 / 1024) / total_time
    print(f"Total time: {total_time:.2f}s | Avg speed: {average_speed:.2f} MB/s")
    

        
def receive_file(conn, save_path, file_size):
    window, bar, speed_label = file_transfer_gui()
    print("Receiving file...")
    with open(save_path, 'wb') as f:
        received = 0
        start_time = time.time()
        last_report_time = start_time
        received_since_last_report = 0
        while received < file_size:
            chunk = conn.recv(FILE_BUFFER_SIZE) 
            if not chunk:
                print("DATA IS NOT VALID")
                return
            f.write(chunk)
            received += len(chunk)
            received_since_last_report += len(chunk)
            bar['value'] = (received / file_size) * 100
            
            current_time = time.time()
            
            if current_time - last_report_time >= 1.0:
                speed = (received_since_last_report / 1024 / 1024) / (current_time - last_report_time)
                speed_label.config(text=f"Speed: {speed:.2f} MB/s")
                last_report_time = current_time
                received_since_last_report = 0
                
            window.update()
    window.destroy()
    print(f"File received: {save_path}")
    total_time = time.time() - start_time
    average_speed = (file_size / 1024 / 1024) / total_time
    print(f"Total time: {total_time:.2f}s | Avg speed: {average_speed:.2f} MB/s")
