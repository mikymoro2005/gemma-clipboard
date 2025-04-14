import pyperclip
import time
import signal
import sys
import requests
import json

# Configurazione API Gemini
GEMINI_API_KEY = "AIzaSyBt1Y7sAhEBBR7BxYEk3YRJ6eEMDfUdTjk"
BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

# Contesto predefinito per Gemma
CONTEXT = """rispondi solo in italiano, per domande specifiche dai solo una risposta corta, 
per domande generiche dai una risposta media, per le domande riguardanti la programmazione, 
dai il codice, a meno che non si tratti di una domanda dove la risposta sia testuale e non codice."""

def fine_generazione():
    print("Fatto")

def signal_handler(signum, frame):
    print("\nMonitoraggio terminato.")
    sys.exit(0)

def list_available_models():
    """Elenca tutti i modelli disponibili per l'API key"""
    try:
        response = requests.get(f"{BASE_URL}/models?key={GEMINI_API_KEY}")
        if response.status_code == 200:
            models = response.json().get('models', [])
            print("Modelli disponibili:")
            available_models = []
            for model in models:
                name = model.get('name', '').split('/')[-1]
                if name and 'generateContent' in model.get('supportedGenerationMethods', []):
                    available_models.append(name)
                    print(f"- {name}")
            return available_models
        else:
            print(f"Errore nella richiesta dei modelli: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        print(f"Errore nel recupero dei modelli: {str(e)}")
        return []

def query_gemini(text, model_name):
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
        
        api_url = f"{BASE_URL}/models/{model_name}:generateContent"
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
            return f"Errore API: {response.status_code} - {response.text}"
            
    except Exception as e:
        print(f"Errore dettagliato: {str(e)}")
        return f"Errore durante la chiamata a Gemini: {str(e)}"

def monitor_clipboard(model_name):
    """Monitora continuamente la clipboard per cambiamenti"""
    last_text = pyperclip.paste()
    print("Monitoraggio clipboard attivo. Premi Ctrl+C per terminare.")
    print(f"Contesto attuale: {CONTEXT}")
    print(f"Modello utilizzato: {model_name}")
    
    while True:
        try:
            time.sleep(1)
            current_text = pyperclip.paste()
            if current_text != last_text:
                print("\nNuovo testo rilevato, invio a Gemini...")
                response = query_gemini(current_text, model_name)
                pyperclip.copy(response)
                print("Risposta di Gemini copiata nella clipboard!")
                fine_generazione()
                last_text = response
            time.sleep(1)  # Pausa per non sovraccaricare la CPU
        except Exception as e:
            print(f"\nErrore: {str(e)}")
            break

if __name__ == "__main__":
    print("Recupero dei modelli disponibili...")
    available_models = list_available_models()
    
    if not available_models:
        print("Nessun modello disponibile trovato. Utilizzo il modello di fallback.")
        model_to_use = "gemini-pro"
    else:
        model_to_use = available_models[0]
        print(f"Utilizzo il modello: {model_to_use}")
    
    signal.signal(signal.SIGINT, signal_handler)
    monitor_clipboard(model_to_use) 