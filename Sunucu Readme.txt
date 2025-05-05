For Windows:

First, if you don't have Chocolatey, install it with the code below. If you don't have Python, install Python and add it to your PATH. Open PowerShell as administrator and enter this code:

```
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

For the server to work, you need to have ngrok installed on your machine and be logged in to an account with payment information added (free). To install ngrok, open PowerShell as administrator and enter this command:

```
choco install ngrok -yes
```

Answer "Y" to any questions. After the process is complete, add payment information to your account, copy your token, and run this command:

```
ngrok config add-authtoken <TOKEN>
```

sunucu.py (server.py) will now work without issues.

For more information: https://ngrok.com/docs/getting-started/