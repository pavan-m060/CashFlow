
pythonimport socket
import threading
import time
from collections import defaultdict
from datetime import datetime
import mysql.connector

HOST = '0.0.0.0'
PORT = 9999
THRESHOLD     = 10
TIME_WINDOW   = 5
BLOCK_DURATION = 30

request_log   = defaultdict(list)
blocked_ips   = {}
total_requests = 0
blocked_count  = 0
lock = threading.Lock()

def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="dos_project"
    )

def log_to_db(ip, status):
    try:
        db     = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO socket_logs (ip_address, status) VALUES (%s, %s)",
            (ip, status)
        )
        db.commit()
        cursor.close()
        db.close()
    except Exception as e:
        print(f"DB Error: {e}")

def is_blocked(ip):
    if ip in blocked_ips:
        if time.time() - blocked_ips[ip] < BLOCK_DURATION:
            return True
        else:
            del blocked_ips[ip]
    return False

def is_attack(ip):
    now = time.time()
    with lock:
        request_log[ip] = [t for t in request_log[ip] if now - t < TIME_WINDOW]
        request_log[ip].append(now)
        return len(request_log[ip]) > THRESHOLD

def handle_client(conn, addr):
    global total_requests, blocked_count
    ip = addr[0]

    with lock:
        total_requests += 1

    if is_blocked(ip):
        conn.send(b"BLOCKED: Your IP is blocked.\n")
        log_to_db(ip, "BLOCKED")
        conn.close()
        return

    if is_attack(ip):
        with lock:
            blocked_ips[ip] = time.time()
            blocked_count  += 1
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"ATTACK [{ts}] from {ip} -- BLOCKED")
        log_to_db(ip, "ATTACK_DETECTED")
        conn.send(b"BLOCKED: Too many requests.\n")
        conn.close()
        return

    try:
        conn.recv(1024)
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"OK    [{ts}] from {ip}")
        log_to_db(ip, "ALLOWED")
        conn.send(b"OK: Request processed.\n")
    except:
        pass
    conn.close()

def dashboard():
    while True:
        time.sleep(5)
        print(f"\n{'='*52}")
        print(f"  LIVE DASHBOARD   {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'='*52}")
        print(f"  Total requests : {total_requests}")
        print(f"  Attack events  : {blocked_count}")
        print(f"  Blocked IPs    : {len(blocked_ips)}")
        if blocked_ips:
            for ip in blocked_ips:
                print(f"    BLOCKED -> {ip}")
        print(f"{'='*52}\n")

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(500)
    print(f"Server running on port {PORT}")
    print(f"Threshold : {THRESHOLD} requests / {TIME_WINDOW} seconds")
    print(f"Block time: {BLOCK_DURATION} seconds\n")
    threading.Thread(target=dashboard, daemon=True).start()
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

start_server()