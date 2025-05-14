import sys
import subprocess
import importlib
import os

def check_and_install_dependencies():
    """Check if all required packages are installed and install them if necessary."""
    required_packages = ['socket', 'tkinter', 'asyncio', 'threading', 'queue']
    missing_packages = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✓ {package} is already installed.")
        except ImportError:
            missing_packages.append(package)
            print(f"✗ {package} is missing.")
    
    if missing_packages:
        print("\nInstalling missing packages...")
        for package in missing_packages:
            # Skip 'socket' and 'threading' as they are part of standard library
            if package not in ['socket', 'threading']:
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                    print(f"✓ Successfully installed {package}")
                except subprocess.CalledProcessError:
                    print(f"✗ Failed to install {package}. Please install it manually.")
                    return False
    
    return True

def check_ngrok():
    """Check if ngrok is installed and accessible."""
    try:
        # Try to execute ngrok to see if it's in the path
        subprocess.run(["ngrok", "--version"], 
                      stdout=subprocess.PIPE, 
                      stderr=subprocess.PIPE, 
                      check=True)
        print("✓ ngrok is installed and accessible.")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ ngrok is not installed or not in the system PATH.")
        print("Please install ngrok from https://ngrok.com/download")
        print("After installation, make sure it's in your system PATH.")
        return False

# Main application code continues below
import socket
import subprocess
import re
import os
import asyncio
import tkinter as tk
from tkinter import simpledialog
from tkinter import ttk
import threading
import time
from queue import Queue

FILE_BUFFER_SIZE = 4194304  # 4 MB

def server_main():
    HOST = '0.0.0.0'
    PORT = 80
    BUFFER_SIZE = 1024
    username = '[SERVER] ' + socket.gethostname()
    clientname = ''

    end_event = asyncio.Event()
    exit_program = asyncio.Event()
    file_confirmation = asyncio.Event()
    message_pause_event = asyncio.Event()
    file_receive_flag_event = asyncio.Event()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()


    conn = None 
    addr = None  

    file_name = ""
    file_size = ""

    async def accept_connection():
        nonlocal conn, addr, clientname
        end_event.clear()
        server_socket.listen()
        print(f"Server started. Listening on port {PORT}...")
        conn, addr = server_socket.accept()
        print(f"Connection received: {addr}")
        clientname = conn.recv(BUFFER_SIZE).decode()
        conn.send(username.encode())
        send_task = asyncio.create_task(send_message())
        receive_task = asyncio.create_task(receive_message())
        await send_task
        await receive_task

    async def create_ngrok_tcp_tunnel(port):
        if not check_ngrok():
            print("Server can't start without ngrok. Please install it and try again.")
            return False
            
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
                    break
            elif "ERR" in line or "error" in line:
                print("[NGROK] Error: " + line.strip())
                return False
                
        print(f"Server started. Listening on port {PORT}...")          
        nonlocal conn, addr, clientname
        conn, addr = server_socket.accept()
        print(f"Connection received: {addr}")
        conn.send(username.encode())
        clientname = conn.recv(BUFFER_SIZE).decode()
        return True
        
    async def send_message():
        loop = asyncio.get_running_loop()
        while True:
            try:
                if end_event.is_set():
                    while True:
                        message = await asyncio.to_thread(input,"Do you want to reconnect? (y/n): ")
                        if message.lower() == 'n':
                             exit_program.set()
                             return
                        elif message.lower() == 'y':
                            return  
                        else:
                            print("Please enter only 'y' or 'n'.")
                else:
                    message = await asyncio.to_thread(input, "Enter message: ")
                    file_receive_flag_event.set()
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
                        nonlocal file_size
                        nonlocal file_name
                        _, save_path = message.split()
                        message_pause_event.set()
                        await asyncio.sleep(0.1)
                        await loop.run_in_executor(None, conn.send, message.encode())
                        file_size = int(file_size)
                        save_path = os.path.join(save_path, file_name)
                        await receive_file(conn,save_path,file_size)
                        message_pause_event.clear()
                    elif message.startswith("/sendfile"):
                        _, file_path= message.split()
                        await send_file(file_path,conn,file_confirmation)
                        continue
                    else:
                        await loop.run_in_executor(None, conn.send, message.encode())
                        print(f"\033[32m{username}: {message}\033[0m")
            except:
                break
            
        
    async def receive_message():
        loop = asyncio.get_running_loop()
        while not end_event.is_set():
            if message_pause_event.is_set():
                await asyncio.sleep(1)
                continue
            else:
                try:
                    data = (await loop.run_in_executor(None, conn.recv, BUFFER_SIZE)).decode()
                    
                    if not data:
                        print("\nClient closed the connection.")
                        print("\nDo you want to reconnect? (y/n)")
                        end_event.set()
                        break
                    elif data.startswith("/sendfile"):
                        nonlocal file_name
                        nonlocal file_size
                        _, file_name, file_size = data.split()
                        file_size = int(file_size)
                        print(f"{clientname} wants to send a file named '{file_name}' with size '{file_size}'. " f"To accept: /acceptfile <path>,to reject type anything")
                        file_receive_flag_event.clear()
                        while not file_receive_flag_event.is_set():
                            await asyncio.sleep(0.2)
                            continue
                    elif data.startswith("/acceptfile"):
                        file_confirmation.set()
                        continue
                    else:
                        print(f"\n\033[31m{clientname}: {data}\033[0m")
                except Exception as e:
                    print(f"Socket error: {e}")
                    return
                

    async def main():
        if not await create_ngrok_tcp_tunnel(PORT):
            return
            
        send_task = asyncio.create_task(send_message())
        receive_task = asyncio.create_task(receive_message())
        await send_task
        await receive_task
        while True:
            try:
                if exit_program.is_set():
                    # Try to terminate ngrok gracefully
                    try:
                        if sys.platform == "win32":
                            subprocess.call(["taskkill", "/f", "/im", "ngrok.exe"])
                        else:
                            subprocess.call(["pkill", "ngrok"])
                    except:
                        pass
                    sys.exit(0)
                elif end_event.is_set():
                    await accept_connection()
                else:
                    pass
            except KeyboardInterrupt:
                print("Server shutting down...")
                # Try to terminate ngrok gracefully
                try:
                    if sys.platform == "win32":
                        subprocess.call(["taskkill", "/f", "/im", "ngrok.exe"])
                    else:
                        subprocess.call(["pkill", "ngrok"])
                except:
                    pass
                sys.exit(0)
    
    # Run the asyncio loop for server
    asyncio.run(main())

def client_main(host, port):
    username = '[CLIENT]'+socket.gethostname()
    servername = ''
    HOST, PORT = host, port
    PORT = int(PORT)  
    BUFFER_SIZE = 1024

    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servername = ""

    end_event = asyncio.Event()
    file_confirmation = asyncio.Event()
    message_pause_event = asyncio.Event()
    file_receive_flag_event = asyncio.Event()

    file_name = ""
    file_size = ""

    async def send_message():
        nonlocal conn
        loop = asyncio.get_running_loop()
        while not end_event.is_set():
            try:
                message = await asyncio.to_thread(input, "Enter message: ")
                file_receive_flag_event.set()
                if message.startswith("/acceptfile"):
                    nonlocal file_size
                    nonlocal file_name
                    _, save_path = message.split()
                    message_pause_event.set()
                    await asyncio.sleep(0.1)
                    await loop.run_in_executor(None, conn.send, message.encode())
                    file_size = int(file_size)
                    save_path = os.path.join(save_path, file_name)
                    await receive_file(conn,save_path,file_size)
                    message_pause_event.clear()
                elif message.startswith("/sendfile"):
                    _, file_path= message.split()
                    await send_file(file_path,conn,file_confirmation)
                else:
                    await loop.run_in_executor(None, conn.send, message.encode())
                    print(f"\n\033[32m{username}: {message}\033[0m")
            except:
                return
                
    async def receive_message():
        nonlocal conn
        loop = asyncio.get_running_loop()
        while not end_event.is_set():
            if message_pause_event.is_set():
                await asyncio.sleep(1)
                continue
            try:
                data = (await loop.run_in_executor(None, conn.recv, BUFFER_SIZE)).decode()
                if not data:
                    print("\nServer disconnected. Client shutting down...")
                    end_event.set()
                elif data.startswith("/sendfile"):
                    nonlocal file_name
                    nonlocal file_size
                    _, file_name, file_size = data.split()
                    file_size = int(file_size)
                    print(f"{servername} wants to send a file named '{file_name}'. " f"To accept: /acceptfile <path>,to reject type anything")
                    file_receive_flag_event.clear()
                    while not file_receive_flag_event.is_set():
                        await asyncio.sleep(0.2)
                        continue
                elif data.startswith("/acceptfile"):
                    file_confirmation.set()
                elif data:
                    print(f"\n\033[31m{servername}: {data}\033[0m")
            except Exception as e:
                print(f"Socket error: {e}")
                return
                
    async def main():
        nonlocal conn, servername
        try:
            print(f"Connecting to {HOST}:{PORT}...")
            conn.connect((HOST, PORT))
            conn.send(username.encode())
            servername = conn.recv(BUFFER_SIZE).decode()
            print("Connection successful!")
            send_task = asyncio.create_task(send_message())
            receive_task = asyncio.create_task(receive_message())
            await send_task
            await receive_task
            while True:
                try:
                    if end_event.is_set():
                        conn.close()
                        print("Client shutting down...")
                        sys.exit(0)
                    else:
                        pass
                except KeyboardInterrupt:
                    conn.close()
                    print("Client shutting down...")
                    sys.exit(0)            
        except Exception as e:
            print(f"Connection failed: {e}")
            return
    
    # Run the asyncio loop for client
    asyncio.run(main())
                
                
def gui_thread(progress_queue: Queue, done_event: threading.Event):
    try:
        window = tk.Tk()
        window.title("File Transfer")
        window.geometry("400x120")

        bar = ttk.Progressbar(window, orient="horizontal", length=300, mode="determinate")
        bar.pack(pady=20)

        speed_label = tk.Label(window, text="Speed: 0.00 MB/s")
        speed_label.pack()

        def update_gui():
            if done_event.is_set():
                window.destroy()
                return
            try:
                while True:
                    progress, speed = progress_queue.get_nowait()
                    bar['value'] = progress
                    speed_label.config(text=f"Speed: {speed:.2f} MB/s")
            except:
                pass
            window.after(100, update_gui)

        update_gui()
        window.mainloop()
    except Exception as e:
        print(f"GUI error: {e}")
        done_event.set()

async def send_file(file_path, target_conn, file_confirmation):
    if not os.path.exists(file_path):
        print("File not found.")
        return

    file_size = os.path.getsize(file_path)
    file_name = os.path.basename(file_path)

    loop = asyncio.get_running_loop()
    
    await loop.run_in_executor(None, target_conn.setsockopt, socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    await loop.run_in_executor(None, target_conn.send, f"/sendfile {file_name} {file_size}".encode())
    
    print(f"File sending request for '{file_name}' has been sent. Waiting for confirmation...")

    await file_confirmation.wait()

    if not file_confirmation.is_set():
        print("File transfer rejected!")
        return

    print("CONFIRMED! Transfer starting...")

    progress_queue = Queue()
    done_event = threading.Event()
    gui = threading.Thread(target=gui_thread, args=(progress_queue, done_event), daemon=True)
    gui.start()

    await asyncio.sleep(1)

    with open(file_path, 'rb') as f:
        sent = 0
        start_time = time.time()
        last_report_time = start_time
        sent_since_last_report = 0

        while True:
            chunk = f.read(FILE_BUFFER_SIZE)
            if not chunk:
                break
            await loop.run_in_executor(None, target_conn.sendall, chunk)
            sent += len(chunk)
            sent_since_last_report += len(chunk)

            progress = (sent / file_size) * 100
            current_time = time.time()

            if current_time - last_report_time >= 1.0:
                speed = (sent_since_last_report / 1024 / 1024) / (current_time - last_report_time)
                progress_queue.put((progress, speed))
                last_report_time = current_time
                sent_since_last_report = 0

    file_confirmation.clear()
    print("File transfer completed.")
    total_time = time.time() - start_time
    average_speed = (file_size / 1024 / 1024) / total_time
    print(f"Total time: {total_time:.2f}s | Avg speed: {average_speed:.2f} MB/s")
    done_event.set()
    gui.join()
    return

async def receive_file(conn, save_path, file_size):

    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, conn.setsockopt, socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    
    progress_queue = Queue()
    done_event = threading.Event()
    gui = threading.Thread(target=gui_thread, args=(progress_queue, done_event), daemon=True)
    gui.start()

    print("Receiving file...")

    with open(save_path, 'wb') as f:
        received = 0
        start_time = time.time()
        last_report_time = start_time
        received_since_last_report = 0

        while received < file_size:
            chunk = await loop.run_in_executor(None, conn.recv, FILE_BUFFER_SIZE)
            if not chunk:
                print("DATA IS NOT VALID")
                return
            f.write(chunk)
            received += len(chunk)
            received_since_last_report += len(chunk)

            progress = (received / file_size) * 100
            current_time = time.time()

            if current_time - last_report_time >= 1.0:
                speed = (received_since_last_report / 1024 / 1024) / (current_time - last_report_time)
                progress_queue.put((progress, speed))
                last_report_time = current_time
                received_since_last_report = 0

    print(f"File received: {save_path}")
    total_time = time.time() - start_time
    average_speed = (file_size / 1024 / 1024) / total_time
    print(f"Total time: {total_time:.2f}s | Avg speed: {average_speed:.2f} MB/s")
    done_event.set()
    gui.join()
    return


# ----------------------
# GUI Interface
def show_interface():
    # First, try to load tkinter
    try:
        root = tk.Tk()
        root.title("Chat Program")
        root.geometry("300x150")
    except Exception as e:
        print(f"Error initializing GUI: {e}")
        print("Falling back to console interface...")
        return show_console_interface()

    def start_server():
        root.destroy()
        server_main()

    def start_client():
        def confirm_connection():
            host = ip_entry.get()
            port = port_entry.get()
            connection_window.destroy()
            root.destroy()
            client_main(host, port)
            
        connection_window = tk.Toplevel(root)
        connection_window.title("Connection Details")
        connection_window.geometry("250x150")
        
        tk.Label(connection_window, text="Host:").grid(row=0, column=0, padx=10, pady=10)
        ip_entry = tk.Entry(connection_window)
        ip_entry.grid(row=0, column=1, padx=10, pady=10)
        ip_entry.insert(0, "localhost")
        
        tk.Label(connection_window, text="Port:").grid(row=1, column=0, padx=10, pady=10)
        port_entry = tk.Entry(connection_window)
        port_entry.grid(row=1, column=1, padx=10, pady=10)
        port_entry.insert(0, "80")
        
        tk.Button(connection_window, text="Connect", command=confirm_connection).grid(row=2, column=0, columnspan=2, pady=10)
        
        connection_window.transient(root)
        connection_window.grab_set()
        root.wait_window(connection_window)

    frame = tk.Frame(root)
    frame.pack(expand=True, fill=tk.BOTH)

    tk.Label(frame, text="Select mode:", font=("Arial", 14)).pack(pady=10)
    
    button_frame = tk.Frame(frame)
    button_frame.pack(pady=10)
    
    server_btn = tk.Button(button_frame, text="Server", command=start_server, width=10, height=2)
    server_btn.grid(row=0, column=0, padx=10)
    
    client_btn = tk.Button(button_frame, text="Client", command=start_client, width=10, height=2)
    client_btn.grid(row=0, column=1, padx=10)

    root.mainloop()

def show_console_interface():
    """Fallback console interface if GUI is not available"""
    print("===== Chat Program =====")
    print("1. Start Server")
    print("2. Start Client")
    print("Q. Quit")
    
    choice = input("Enter your choice: ")
    
    if choice == "1":
        server_main()
    elif choice == "2":
        host = input("Enter host (default: localhost): ") or "localhost"
        port = input("Enter port (default: 80): ") or "80"
        client_main(host, port)
    elif choice.lower() == "q":
        print("Exiting...")
        sys.exit(0)
    else:
        print("Invalid choice. Please try again.")
        show_console_interface()

if __name__ == "__main__":
    # Check dependencies before starting the program
    if not check_and_install_dependencies():
        print("Failed to install required dependencies. The program cannot run.")
        sys.exit(1)
        
    if len(sys.argv) > 1:
        if sys.argv[1] == "server":
            server_main()
        elif sys.argv[1] == "client":
            host, port = sys.argv[2].split(":")
            client_main(host, port)
    else:
        show_interface()