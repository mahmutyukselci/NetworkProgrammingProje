import socket
import sys
import threading
import signal

def signal_handler(sig, frame):
    print("\nClient shutting down...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

if len(sys.argv) < 2:
    print("Kullanım: python client.py <IP:PORT>")
    sys.exit(1)

kullaniciadi = '[ISTEMCI]'+socket.gethostname()
sunucuadi = ''

giris = sys.argv[1]  # Örn: "0.tcp.ngrok.io:10942"

HOST, PORT = giris.split(":")
PORT = int(PORT)  # Port her zaman int olmalı
BUFFER_SIZE = 1024

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))
client.send(kullaniciadi.encode())
sunucuadi = client.recv(BUFFER_SIZE).decode()
print("Bağlantı başarılı!")

def mesaj_gonder():
    while True:
            print("Mesaj girin:")
            mesaj = input()
            client.send(mesaj.encode())
            print(f"\n{kullaniciadi}:{mesaj}")


def mesaj_al():
    while True:
        try:
            cevap = client.recv(BUFFER_SIZE).decode()
            if cevap:
                print(f"\n{sunucuadi}: {cevap}")
        except:
            break


threading.Thread(target=mesaj_gonder,).start()
threading.Thread(target=mesaj_al,).start()


while True:
    pass