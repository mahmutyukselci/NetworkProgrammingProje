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
        subprocess.call(["taskkill", "/f", "/im", "ngrok.exe"])
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
    
    return 
        
ngrok_tcp_tunel_olustur(PORT)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()
print(f"Sunucu başlatıldı. Port {PORT} dinleniyor...")

conn, addr = server_socket.accept()
print(f"Bağlantı alındı: {addr}")

istemciadi = conn.recv(BUFFER_SIZE).decode()
conn.send(kullaniciadi.encode())

bitir_event = threading.Event()
programi_bitir = threading.Event()


def mesaj_al():
    while True:
        try:
            data = conn.recv(BUFFER_SIZE).decode()
            if not data:
                print("\nİstemci bağlantıyı kapattı.")
                print("\nYeniden bağlanmak istiyor musunuz ?(y/n)")
                bitir_event.set()
                break
            print(f"\n\033[31m{istemciadi}: {data}\033[0m")
        except:
            break
def mesaj_gonder():
    while True:
        try:
            if bitir_event.is_set():
                while True:
                    cevap = input("Yeniden bağlanmak istiyor musunuz? (y/n): ")
                    if cevap.lower() == 'n':
                         programi_bitir.set()
                         return
                    elif cevap.lower() == 'y':
                        return  
                    else:
                        print("Lütfen sadece 'y' veya 'n' girin.")
            else:
                cevap = input("Mesaj girin: ")
                if bitir_event.is_set():
                    if cevap.lower() == 'y' or 'n':
                        if cevap.lower() == 'n':
                            programi_bitir.set()
                            return
                        elif cevap.lower() == 'y':
                            return  
                    else:
                        continue
                conn.send(cevap.encode())
                print(f"\033[32m{kullaniciadi}: {cevap}\033[0m")
        except:
            break


def baglanti_al():
    global conn, istemciadi, t_al, t_ver
    bitir_event.clear()
    server_socket.listen()
    print(f"Sunucu başlatıldı. Port {PORT} dinleniyor...")
    conn, addr = server_socket.accept()
    print(f"Bağlantı alındı: {addr}")
    istemciadi = conn.recv(BUFFER_SIZE).decode()
    conn.send(kullaniciadi.encode())

    t_al = threading.Thread(target=mesaj_al)
    t_al.start()
    t_ver = threading.Thread(target=mesaj_gonder)
    t_ver.start()
    


t_al=threading.Thread(target=mesaj_al,)
t_al.start()
t_ver=threading.Thread(target=mesaj_gonder,)
t_ver.start()

while True:
    t_al.join()
    t_ver.join()
    if programi_bitir.is_set():
        subprocess.call(["taskkill", "/f", "/im", "ngrok.exe"])
        sys.exit(0)
    else:
        baglanti_al()

