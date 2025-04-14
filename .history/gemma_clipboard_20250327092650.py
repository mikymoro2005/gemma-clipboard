import pyperclip
import ollama
import time
import signal
import sys

# Contesto predefinito per Gemma
CONTEXT = """rispondi solo in italiano, per domande specifiche dai solo una risposta corta, 
per domande generiche dai una risposta media, per le domande riguardanti la programmazione, 
dai il codice, a meno che non si tratti di una domanda dove la risposta sia testuale e non codice."""

def fine_generazione():
    print("Fatto")

def signal_handler(signum, frame):
    print("\nMonitoraggio terminato.")
    sys.exit(0)

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
                print("\nNuovo testo rilevato, invio a Gemma...")
                response = query_gemma(current_text)
                pyperclip.copy(response)
                print("Risposta di Gemma copiata nella clipboard!")
                fine_generazione()
                last_text = response
            time.sleep(1)  # Pausa per non sovraccaricare la CPU
        except Exception as e:
            print(f"\nErrore: {str(e)}")
            break

def query_gemma(text):
    """Invia il testo a Gemma 3.1 e ottiene la risposta"""
    try:
        response = ollama.chat(model='gemma3:1b', messages=[
            {
                'role': 'system',
                'content': CONTEXT
            },
            {
                'role': 'user',
                'content': text
            }
        ])
        return response['message']['content']
    except Exception as e:
        print(f"Errore dettagliato: {str(e)}")  # Aggiungiamo più dettagli sull'errore
        return f"Errore durante la chiamata a Gemma: {str(e)}"

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    monitor_clipboard() 