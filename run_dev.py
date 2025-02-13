import subprocess
import time

def run_process(command):
    """Executa um comando em subprocesso"""
    return subprocess.Popen(command, shell=True)

if __name__ == "__main__":
    print("🚀 Iniciando modo de desenvolvimento...")

    flask_watch = run_process("python auto_reload.py")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Encerrando processos...")
        flask_watch.terminate()
