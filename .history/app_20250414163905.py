from flask import Flask, render_template, send_file, jsonify
import os
import subprocess
import platform
import threading
import time

app = Flask(__name__)

# Percorso del file Python
PYTHON_SCRIPT = "gemma_clipboard.py"

# Variabile per tenere traccia del processo in esecuzione
running_process = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download')
def download():
    """Scarica il file Python"""
    return send_file(PYTHON_SCRIPT, as_attachment=True)

@app.route('/start', methods=['POST'])
def start_script():
    """Avvia lo script Python"""
    global running_process
    
    if running_process and running_process.poll() is None:
        return jsonify({"status": "already_running", "message": "Lo script è già in esecuzione"})
    
    try:
        # Determina il comando corretto in base al sistema operativo
        if platform.system() == "Windows":
            command = ["python", PYTHON_SCRIPT]
        else:
            command = ["python3", PYTHON_SCRIPT]
        
        # Avvia il processo
        running_process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Avvia un thread per monitorare il processo
        threading.Thread(target=monitor_process, args=(running_process,), daemon=True).start()
        
        return jsonify({"status": "success", "message": "Script avviato con successo"})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Errore nell'avvio: {str(e)}"})

@app.route('/stop', methods=['POST'])
def stop_script():
    """Ferma lo script Python"""
    global running_process
    
    if running_process and running_process.poll() is None:
        try:
            running_process.terminate()
            time.sleep(1)  # Attendi che il processo termini
            if running_process.poll() is None:
                running_process.kill()  # Forza la chiusura se necessario
            return jsonify({"status": "success", "message": "Script fermato con successo"})
        except Exception as e:
            return jsonify({"status": "error", "message": f"Errore nell'arresto: {str(e)}"})
    else:
        return jsonify({"status": "not_running", "message": "Nessuno script in esecuzione"})

def monitor_process(process):
    """Monitora il processo e aggiorna lo stato"""
    while process.poll() is None:
        time.sleep(1)
    
    global running_process
    running_process = None

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 