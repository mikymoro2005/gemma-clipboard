from flask import Flask, send_from_directory, render_template, jsonify, request
import os
import subprocess
import platform
import threading
import time
import shutil

app = Flask(__name__, static_folder='public')

# Percorso del file Python
PYTHON_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gemma_clipboard.py')
DOWNLOAD_DIR = os.path.expanduser("~/Downloads")  # Directory di download predefinita

# Variabile per tenere traccia del processo in esecuzione
running_process = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/<path:filename>')
def download_file(filename):
    return send_from_directory('public', filename)

@app.route('/open.command', methods=['POST'])
def open_command():
    """Apre il file scaricato"""
    try:
        # Determina il sistema operativo
        system = platform.system()
        
        # Percorso del file scaricato
        download_path = os.path.expanduser("~/Downloads")
        
        if system == "Windows":
            file_path = os.path.join(download_path, "start_windows.bat")
            if os.path.exists(file_path):
                subprocess.Popen(["start", file_path], shell=True)
                return jsonify({"success": True, "message": "File aperto con successo"})
        elif system == "Darwin":  # macOS
            file_path = os.path.join(download_path, "start_mac.command")
            if os.path.exists(file_path):
                # Rendi il file eseguibile
                os.chmod(file_path, 0o755)
                subprocess.Popen(["open", file_path])
                return jsonify({"success": True, "message": "File aperto con successo"})
        elif system == "Linux":
            file_path = os.path.join(download_path, "start_linux.sh")
            if os.path.exists(file_path):
                # Rendi il file eseguibile
                os.chmod(file_path, 0o755)
                subprocess.Popen(["xdg-open", file_path])
                return jsonify({"success": True, "message": "File aperto con successo"})
        
        return jsonify({"success": False, "error": "File non trovato"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/start', methods=['POST'])
def start():
    """Avvia il processo Python"""
    global running_process
    
    try:
        # Verifica se il file esiste
        if not os.path.exists(PYTHON_SCRIPT):
            return jsonify({"success": False, "error": "File Python non trovato"}), 404
        
        # Se il processo è già in esecuzione, non avviarlo di nuovo
        if running_process and running_process.poll() is None:
            return jsonify({"success": True, "message": "Processo già in esecuzione"})
        
        # Avvia il processo Python
        running_process = subprocess.Popen(
            ["python3", PYTHON_SCRIPT],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Avvia un thread per monitorare il processo
        threading.Thread(target=monitor_process, args=(running_process,), daemon=True).start()
        
        return jsonify({"success": True, "message": "Processo avviato con successo"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/stop', methods=['POST'])
def stop():
    """Ferma il processo Python"""
    global running_process
    
    try:
        if running_process and running_process.poll() is None:
            running_process.terminate()
            time.sleep(1)  # Attendi che il processo termini
            if running_process.poll() is None:
                running_process.kill()  # Forza la chiusura se necessario
            return jsonify({"success": True, "message": "Processo fermato con successo"})
        else:
            return jsonify({"success": False, "error": "Nessun processo in esecuzione"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/status')
def status():
    """Controlla lo stato del processo Python"""
    global running_process
    
    if running_process and running_process.poll() is None:
        return jsonify({"running": True})
    else:
        return jsonify({"running": False})

def monitor_process(process):
    """Monitora il processo e aggiorna lo stato"""
    while process.poll() is None:
        time.sleep(1)
    
    global running_process
    running_process = None

if __name__ == '__main__':
    # Verifica se il file Python esiste
    if not os.path.exists(PYTHON_SCRIPT):
        print("File Python non trovato:", PYTHON_SCRIPT)
        print("Assicurati che il file sia presente prima di avviare l'applicazione.")
    
    app.run(host='0.0.0.0', port=8080) 