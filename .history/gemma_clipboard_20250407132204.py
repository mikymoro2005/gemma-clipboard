import pyperclip
import time
import signal
import sys
import requests
import json

# Configurazione API Gemini
GEMINI_API_KEY = "AIzaSyBt1Y7sAhEBBR7BxYEk3YRJ6eEMDfUdTjk"

# Lista dei modelli gratuiti disponibili
AVAILABLE_MODELS = {
    "gemini-pro": "gemini-pro",          # Gratuito, modello di base
    "gemini-flash": "gemini-1.5-flash",  # Gratuito, versione più veloce
}

# Seleziona il modello (puoi modificare qui)
SELECTED_MODEL = "gemini-pro"

API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{AVAILABLE_MODELS[SELECTED_MODEL]}:generateContent"

# Contesto predefinito per Gemma
CONTEXT = """rispondi solo in italiano, per domande specifiche dai solo una risposta corta, 
per domande generiche dai una risposta media, per le domande riguardanti la programmazione, 
dai il codice, a meno che non si tratti di una domanda dove la risposta sia testuale e non codice."""

def fine_generazione():
    print("Fatto")

def signal_handler(signum, frame):
    print("\nMonitoraggio terminato.")
    sys.exit(0)

def query_gemini(text):
    """Invia il testo a Gemini e ottiene la risposta"""
    try:
        headers = {
            "Content-Type": "application/json"
        }
        
        data = {
            "contents": [{
                "parts":[{
                    "text": f"{CONTEXT}\n\nUser: {text}"
                }]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 1024
            }
        }
        
        print(f"Utilizzando il modello gratuito: {SELECTED_MODEL}")
        response = requests.post(
            f"{API_URL}?key={GEMINI_API_KEY}",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            result = response.json()
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            error_msg = f"Errore API: {response.status_code} - {response.text}"
            print(error_msg)
            return error_msg
            
    except Exception as e:
        print(f"Errore dettagliato: {str(e)}")
        return f"Errore durante la chiamata a Gemini: {str(e)}"

def monitor_clipboard():
    """Monitora continuamente la clipboard per cambiamenti"""
    last_text = pyperclip.paste()
    print("Monitoraggio clipboard attivo. Premi Ctrl+C per terminare.")
    print(f"Contesto attuale: {CONTEXT}")
    print(f"Modello gratuito selezionato: {SELECTED_MODEL}")
    
    while True:
        try:
            time.sleep(1)
            current_text = pyperclip.paste()
            if current_text != last_text:
                print("\nNuovo testo rilevato, invio a Gemini...")
                response = query_gemini(current_text)
                pyperclip.copy(response)
                print("Risposta di Gemini copiata nella clipboard!")
                fine_generazione()
                last_text = response
            time.sleep(1)  # Pausa per non sovraccaricare la CPU
        except Exception as e:
            print(f"\nErrore: {str(e)}")
            break

if __name__ == "__main__":
    if SELECTED_MODEL not in AVAILABLE_MODELS:
        print(f"Modello '{SELECTED_MODEL}' non disponibile. Modelli gratuiti disponibili: {', '.join(AVAILABLE_MODELS.keys())}")
        sys.exit(1)
        
    signal.signal(signal.SIGINT, signal_handler)
    monitor_clipboard() 