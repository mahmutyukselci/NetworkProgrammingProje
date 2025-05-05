import socket
import sys
import threading
import signal

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

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))
client.send(username.encode())
servername = client.recv(BUFFER_SIZE).decode()
print("Connection successful!")

end_event = threading.Event()

def send_message():
    while not end_event.is_set():
        try:
            message = input("Enter message: ")
            client.send(message.encode())
            print(f"\n\033[32m{username}: {message}\033[0m")
        except:
            return
            
def receive_message():
    while not end_event.is_set():
        try:
            answer = client.recv(BUFFER_SIZE).decode()
            if answer:
                print(f"\n\033[31m{servername}: {answer}\033[0m")
        except:
            return
            
t_send = threading.Thread(target=send_message,)
t_send.start()
t_receive = threading.Thread(target=receive_message,)
t_receive.start()

while True:
    if end_event.is_set():
        client.close()
        sys.exit(0)