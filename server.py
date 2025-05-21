import socket
import sys
import subprocess
import re
import os
import functions
import asyncio

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


conn: socket.socket = None 
addr: socket.socket = None  

file_name = ""
file_size = ""

async def accept_connection():
    global conn,addr, clientname
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
    print(f"Server started. Listening on port {PORT}...")          
    global conn, addr,clientname
    conn, addr = server_socket.accept()
    print(f"Connection received: {addr}")
    conn.send(username.encode())
    clientname = conn.recv(BUFFER_SIZE).decode()
    return 
    
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
                    global file_size
                    global file_name
                    _, save_path = message.split()
                    message_pause_event.set()
                    await asyncio.sleep(0.1)
                    await loop.run_in_executor(None, conn.send, message.encode())
                    file_size = int(file_size)
                    save_path = os.path.join(save_path, file_name)
                    await functions.receive_file(conn,save_path,file_size)
                    message_pause_event.clear()
                elif message.startswith("/sendfile"):
                    _, file_path= message.split()
                    await functions.send_file(file_path,conn,file_confirmation)
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
                    return
                elif data.startswith("/sendfile"):
                    global file_name
                    global file_size
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
    await create_ngrok_tcp_tunnel(PORT)
    send_task = asyncio.create_task(send_message())
    receive_task = asyncio.create_task(receive_message())
    await send_task
    await receive_task
    await asyncio.sleep(0.1)
    if exit_program.is_set():
        subprocess.call(["taskkill", "/f", "/im", "ngrok.exe"])
        sys.exit(0)
    elif end_event.is_set():
        await accept_connection()
    else:
        print("Unknown error occured seek help")
        return
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Server shutting down...")
        subprocess.call(["taskkill", "/f", "/im", "ngrok.exe"])
        sys.exit(0)