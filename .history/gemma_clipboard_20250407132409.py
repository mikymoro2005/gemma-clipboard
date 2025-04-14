import pyperclip
import time
import signal
import sys
import requests
import json

# Configurazione API Gemini
GEMINI_API_KEY = "AIzaSyBt1Y7sAhEBBR7BxYEk3YRJ6eEMDfUdTjk"

# Modello da utilizzare
MODEL_NAME = "gemini-pro"

# URL dell'API corretto secondo la documentazione più recente
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent"

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
        
        # Stampa l'URL per debug
        print(f"Chiamata API a: {API_URL}?key=API_KEY")
        
        response = requests.post(
            f"{API_URL}?key={GEMINI_API_KEY}",
            headers=headers,
            json=data
        )
        
        # Stampa lo stato della risposta
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            error_details = response.text
            print(f"Dettagli errore: {error_details}")
            return f"Errore API: {response.status_code} - {error_details}"
            
    except Exception as e:
        print(f"Errore dettagliato: {str(e)}")
        return f"Errore durante la chiamata a Gemini: {str(e)}"

def monitor_clipboard():
    """Monitora continuamente la clipboard per cambiamenti"""
    last_text = pyperclip.paste()
    print("Monitoraggio clipboard attivo. Premi Ctrl+C per terminare.")
    print(f"Contesto attuale: {CONTEXT}")
    
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