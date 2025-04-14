import pyperclip
import time
import signal
import sys
import requests
import json

# Configurazione API Gemini - Aggiornata con nuova API key
GEMINI_API_KEY = "AIzaSyAKeeh-23wT9hYG69Q3cJSwg_phedHis0c"
BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

# Modello da utilizzare (specifico per evitare errori)
MODEL_NAME = "gemini-2.0-flash"

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
            }]
        }
        
        api_url = f"{BASE_URL}/models/{MODEL_NAME}:generateContent"
        print(f"Chiamata API a: {api_url}")
        
        response = requests.post(
            f"{api_url}?key={GEMINI_API_KEY}",
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
        error_msg = f"Errore dettagliato: {str(e)}"
        print(error_msg)
        return error_msg

def monitor_clipboard():
    """Monitora continuamente la clipboard per cambiamenti"""
    last_text = pyperclip.paste()
    print("Monitoraggio clipboard attivo. Premi Ctrl+C per terminare.")
    print(f"Contesto attuale: {CONTEXT}")
    print(f"Modello utilizzato: {MODEL_NAME}")
    
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
    signal.signal(signal.SIGINT, signal_handler)
    monitor_clipboard() 