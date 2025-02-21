import os
import sys
import time
import subprocess
from flask import Flask
from flask_socketio import SocketIO
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

WATCHED_DIRS = ["base_dir/", "static/css/", "static/scss/", "templates/"]

class ChangeHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        if event.is_directory:
            return
        print(f"🔄 Arquivo modificado: {event.src_path}")
        socketio.emit("reload", {"message": "reload"})  # Notifica o browser
        restart_server()

def restart_server():
    global server_process
    if server_process:
        server_process.terminate()
        server_process.wait()

    print("🚀 Reiniciando Flask Server...")
    server_process = subprocess.Popen([sys.executable, "main.py"])

if __name__ == "__main__":
    observer = Observer()
    for dir_path in WATCHED_DIRS:
        observer.schedule(ChangeHandler(), path=dir_path, recursive=True)

    print("👀 Monitorando mudanças no código...")
    server_process = subprocess.Popen([sys.executable, "main.py"])

    try:
        observer.start()
        socketio.run(app, port=5001)
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        server_process.terminate()

    observer.join()
