import socket
import sys
import threading
import signal
import subprocess
import re

HOST = '0.0.0.0'
PORT = 80
BUFFER_SIZE = 1024
kullaniciadi = '[SUNUCU] ' + socket.gethostname()
istemciadi = ''

def signal_handler(sig, frame):
    print("\nServer shutting down...")
    try:
        conn.close()
        server_socket.close()
    except:
        pass
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def ngrok_tcp_tunel_olustur(port):
    print("TCP tüneli aktifleştiriliyor...")
    komut = ["ngrok", "tcp", str(port), "--log=stdout"]
    proc = subprocess.Popen(komut, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    for line in proc.stdout:
        if "msg=\"started tunnel\"" in line and "url=tcp://" in line:
            match = re.search(r'url=tcp://(.+?):(\d+)', line)
            if match:
                print("Başarılı!")
                host, forwarded_port = match.groups()
                print(f"[NGROK] Bağlantı adresi: {host}, Port: {forwarded_port}")
                return 1
        elif "ERR" in line or "error" in line:
            print("[NGROK] Hata: " + line.strip())
    
    return 0
        
ngrok_tcp_tunel_olustur(PORT)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()
print(f"Sunucu başlatıldı. Port {PORT} dinleniyor...")

conn, addr = server_socket.accept()
print(f"Bağlantı alındı: {addr}")

istemciadi = conn.recv(BUFFER_SIZE).decode()
conn.send(kullaniciadi.encode())

def mesaj_al():
    while True:
        try:
            data = conn.recv(BUFFER_SIZE).decode()
            if not data:
                print("\nİstemci bağlantıyı kapattı, yeni bağlantı bekleniyor...")
                baglanti_al()
                break
            print(f"\n{istemciadi}: {data}")
        except:
            break

def mesaj_gonder():
    while True:
        try:
            print("Mesaj girin:")
            cevap = input()
            conn.send(cevap.encode())
            print(f"\n{kullaniciadi}: {cevap}")
        except:
            break

def baglanti_al():
        server_socket.listen()
        print(f"Sunucu başlatıldı. Port {PORT} dinleniyor...")
        conn, addr = server_socket.accept()
        print(f"Bağlantı alındı: {addr}")
        istemciadi = conn.recv(BUFFER_SIZE).decode()
        conn.send(kullaniciadi.encode())

threading.Thread(target=mesaj_al,).start()
threading.Thread(target=mesaj_gonder,).start()


while True:
    pass
