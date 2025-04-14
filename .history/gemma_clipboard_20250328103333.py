import pyperclip
import time
import signal
import sys
import google.generativeai as genai

# Configurazione API Gemini
GEMINI_API_KEY = "AIzaSyBt1Y7sAhEBBR7BxYEk3YRJ6eEMDfUdTjk"
genai.configure(api_key=GEMINI_API_KEY)

# Verifica dei modelli disponibili
try:
    model = genai.GenerativeModel('gemini-2.0-flash')  # Prova il modello flash
except Exception:
    try:
        model = genai.GenerativeModel('gemini-1.0-pro')  # Fallback al modello pro
    except Exception as e:
        print(f"Errore nella configurazione del modello: {str(e)}")
        sys.exit(1)

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
        # Combina il contesto con l'input dell'utente
        prompt = f"{CONTEXT}\n\nUser: {text}"
        response = model.generate_content(prompt)
        if response.text:
            return response.text
        return "Nessuna risposta generata"
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