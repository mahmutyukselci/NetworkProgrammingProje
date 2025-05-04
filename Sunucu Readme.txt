önce chocolatey yoksa aşağıdaki kod ile kurun eğer python yoksa python da kurun ve PATH e ekleyin, powershell i administrator açıp kodu girin:

Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

Sunucunun çalışabilmesi için makinede ngrok kurulu olup kart bilgisi eklenmiş bir hesaba giriş yapılması gerekmekte(ücretsiz)

ngrok kurmak için administrator powershell açıp komutu girin :

-choco install ngrok
-yes no sorularına Y diyin

işlem tamamlandıktan sonra hesabınıza kart bilgisi ekleyip tokeninizi kopyalayın ve komutu çalıştırın:

-ngrok config add-authtoken <TOKEN>

sunucu.py artık sorunsuz çalışacaktır

https://ngrok.com/docs/getting-started/