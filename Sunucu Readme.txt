Sunucunun çalışabilmesi için makinede ngrok kurulu olup kart bilgisi eklenmiş bir hesaba giriş yapılması gerekmekte(ücretsiz)

ngrok kurmak için administrator powershell açıp komutu girin :

-choco install ngrok
-yes no sorularına Y diyin

işlem tamamlandıktan sonra hesabınıza kart bilgisi ekleyip tokeninizi kopyalayın ve komutu çalıştırın:

-ngrok config add-authtoken <TOKEN>

sunucu.py artık sorunsuz çalışacaktır

https://ngrok.com/docs/getting-started/