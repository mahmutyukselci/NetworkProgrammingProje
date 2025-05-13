import socket
import sys
import os
import functions
import asyncio
    
username = '[CLIENT]'+socket.gethostname()
servername = ''
input_address = sys.argv[1] 
HOST, PORT = input_address.split(":")
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
    global conn
    loop = asyncio.get_running_loop()
    while not end_event.is_set():
        try:
            message = await asyncio.to_thread(input, "Enter message: ")
            file_receive_flag_event.set()
            if message.startswith("/acceptfile"):
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
            else:
                await loop.run_in_executor(None, conn.send, message.encode())
                print(f"\n\033[32m{username}: {message}\033[0m")
        except:
            return
            
async def receive_message():
    global conn
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
                global file_name
                global file_size
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
    global conn,servername
    conn.connect((HOST, PORT))
    conn.send(username.encode())
    servername = conn.recv(BUFFER_SIZE).decode()
    print("Connection successful!")
    send_task = asyncio.create_task(send_message())
    receive_task = asyncio.create_task(receive_message())
    await send_task
    await receive_task
    while True:
        if end_event.is_set():
            conn.close()
            print("Client shutting down...")
            sys.exit(0)
        else:
            pass
            
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Client shutting down...")
        conn.close()
        sys.exit(0)