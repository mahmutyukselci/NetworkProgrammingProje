import socket
import sys
import threading
import signal

def signal_handler(sig, frame):
    print("\nClient shutting down...")
    bitir_event.set()

signal.signal(signal.SIGINT, signal_handler)

if len(sys.argv) < 2:
    print("Kullanım: python client.py <IP:PORT>")
    sys.exit(1)

kullaniciadi = '[ISTEMCI]'+socket.gethostname()
sunucuadi = ''

giris = sys.argv[1]  # Örn: "0.tcp.ngrok.io:10942"

HOST, PORT = giris.split(":")
PORT = int(PORT)  
BUFFER_SIZE = 1024

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))
client.send(kullaniciadi.encode())
sunucuadi = client.recv(BUFFER_SIZE).decode()
print("Bağlantı başarılı!")

bitir_event = threading.Event()

def mesaj_gonder():
    while not bitir_event.is_set():
        try:
            mesaj = input("Mesaj girin: ")
            client.send(mesaj.encode())
            print(f"\n\033[32m{kullaniciadi}: {mesaj}\033[0m")
        except:
            return

def mesaj_al():
    while not bitir_event.is_set():
        try:
            cevap = client.recv(BUFFER_SIZE).decode()
            if cevap:
                print(f"\n\033[31m{sunucuadi}: {cevap}\033[0m")
        except:
            return


t_ver = threading.Thread(target=mesaj_gonder,)
t_ver.start()
t_al = threading.Thread(target=mesaj_al,)
t_al.start()

while True:
    if bitir_event.is_set():
        client.close()
        sys.exit(0) 