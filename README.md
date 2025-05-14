Onefile .exe and .app versions added Windows users can directly download 
MacOs users can download from actions artifacts https://github.com/mahmutyukselci/NetworkProgrammingProje/actions/runs/15026869358/artifacts/3124774812

For client.py to work you just need Python installed on your device.
You can use it like "python client.py <IP:PORT>"

For server.py:

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

server.py will now work without issues.

For more information: https://ngrok.com/docs/getting-started/

For other OS users you need Python installed on your device and you need to log in to your Ngrok account(also need to add card information but its free to use) from terminal and add your token by command.

Then you can use the file same.
