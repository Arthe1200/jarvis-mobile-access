#!/usr/bin/env python3
"""Authenticated local bridge: starts JARVIS Flask and reverse-proxies the existing UI."""
import hmac
import json
import logging
import os
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

CONFIG_PATH = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "JARVIS" / "mobile-bridge.json"
LOG_PATH = CONFIG_PATH.parent / "mobile-bridge.log"
logging.basicConfig(filename=str(LOG_PATH), level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")
with CONFIG_PATH.open("r", encoding="utf-8-sig") as f:
    CONFIG = json.load(f)
TOKEN = str(CONFIG.get("token", ""))
ACTIONS = Path(str(CONFIG.get("actions_path", ""))).expanduser()
PYTHON = str(CONFIG.get("python_exe") or sys.executable)
HOST = "127.0.0.1"
PORT = int(CONFIG.get("port", 8765))
FLASK_URL = "http://127.0.0.1:5000"
ALLOWED_ORIGINS = {
    "capacitor://localhost",
    "http://localhost",
    "https://arthe1200.github.io",
}
server_lock = threading.Lock()
server_process = None

if len(TOKEN) < 32:
    raise SystemExit("Bridge token is missing or too short. Re-run JARVIS_Setup_Mobile_Bridge.ps1.")
if not ACTIONS.is_file():
    raise SystemExit("actions.py not found: " + str(ACTIONS))

def flask_online():
    try:
        req = urllib.request.Request(FLASK_URL + "/ping", headers={"Cache-Control": "no-cache"})
        with urllib.request.urlopen(req, timeout=1.5) as response:
            if response.status != 200:
                return False
            payload = json.loads(response.read(4096).decode("utf-8"))
            return payload.get("status") == "online"
    except Exception:
        return False

def start_flask():
    global server_process
    if flask_online():
        return True
    with server_lock:
        if flask_online():
            return True
        if server_process is None or server_process.poll() is not None:
            logging.info("Starting JARVIS Flask: %s", ACTIONS)
            log_handle = open(LOG_PATH, "a", encoding="utf-8")
            server_process = subprocess.Popen(
                [PYTHON, str(ACTIONS)],
                cwd=str(ACTIONS.parent),
                stdin=subprocess.DEVNULL,
                stdout=log_handle,
                stderr=subprocess.STDOUT,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
    for _ in range(25):
        if flask_online():
            logging.info("JARVIS Flask is online.")
            return True
        time.sleep(0.8)
    logging.error("Flask did not become online within 20 seconds.")
    return False

class Handler(BaseHTTPRequestHandler):
    server_version = "JARVISBridge/1.0"
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):
        logging.info("%s - %s", self.client_address[0], fmt % args)

    def cors(self):
        origin = self.headers.get("Origin", "")
        if origin in ALLOWED_ORIGINS:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, PATCH, DELETE, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type")
            self.send_header("Access-Control-Max-Age", "600")

    def json_response(self, code, payload):
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.cors()
        self.end_headers()
        self.wfile.write(body)

    def authorized(self):
        header = self.headers.get("Authorization", "")
        supplied = header[7:].strip() if header.lower().startswith("bearer ") else ""
        return bool(supplied) and hmac.compare_digest(supplied, TOKEN)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Content-Length", "0")
        self.cors()
        self.end_headers()

    def do_GET(self):
        path = urlsplit(self.path).path
        if path == "/bridge/status":
            if not self.authorized():
                self.json_response(401, {"error": "Clé privée invalide."})
                return
            online = flask_online()
            self.json_response(200, {"bridge": "online", "server": "online" if online else "offline"})
            return
        self.proxy()

    def do_POST(self):
        path = urlsplit(self.path).path
        if path == "/bridge/start":
            if not self.authorized():
                self.json_response(401, {"error": "Clé privée invalide."})
                return
            if start_flask():
                self.json_response(200, {"ok": True, "server": "online"})
            else:
                self.json_response(504, {"ok": False, "error": "Flask ne répond pas. Consulte mobile-bridge.log."})
            return
        self.proxy()

    def do_PUT(self): self.proxy()
    def do_PATCH(self): self.proxy()
    def do_DELETE(self): self.proxy()

    def proxy(self):
        if not flask_online():
            self.json_response(503, {"error": "JARVIS Flask est arrêté. Utilise /bridge/start via l’application."})
            return
        target = FLASK_URL + self.path
        length = int(self.headers.get("Content-Length", "0") or 0)
        body = self.rfile.read(min(length, 10_000_000)) if length else None
        headers = {}
        for key, value in self.headers.items():
            if key.lower() not in {"host", "connection", "content-length", "authorization", "origin", "accept-encoding"}:
                headers[key] = value
        req = urllib.request.Request(target, data=body, headers=headers, method=self.command)
        try:
            with urllib.request.urlopen(req, timeout=90) as response:
                data = response.read()
                self.send_response(response.status)
                for key, value in response.headers.items():
                    if key.lower() not in {"connection", "transfer-encoding", "content-length", "content-encoding", "access-control-allow-origin"}:
                        self.send_header(key, value)
                self.send_header("Content-Length", str(len(data)))
                self.send_header("Cache-Control", "no-store")
                self.cors()
                self.end_headers()
                self.wfile.write(data)
        except urllib.error.HTTPError as exc:
            data = exc.read()
            self.send_response(exc.code)
            self.send_header("Content-Type", exc.headers.get("Content-Type", "text/plain; charset=utf-8"))
            self.send_header("Content-Length", str(len(data)))
            self.cors()
            self.end_headers()
            self.wfile.write(data)
        except Exception:
            logging.exception("Proxy failure")
            self.json_response(502, {"error": "Impossible de joindre JARVIS Flask."})

def main():
    logging.info("Bridge listening on %s:%s; actions=%s", HOST, PORT, ACTIONS)
    httpd = ThreadingHTTPServer((HOST, PORT), Handler)
    httpd.serve_forever()

if __name__ == "__main__":
    main()
