import pyperclip
import time
import signal
import sys
import requests
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from collections import deque
import threading

# Configurazione API Gemini - Aggiornata con nuova API key
GEMINI_API_KEY = "AIzaSyAKeeh-23wT9hYG69Q3cJSwg_phedHis0c"
BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

# Modello da utilizzare (specifico per evitare errori)
MODEL_NAME = "gemini-2.0-flash"

# Configurazione Email
EMAIL_SENDER = "michelemoretti2025@gmail.com"
EMAIL_PASSWORD = "nqng gquj fqzx nyzq"  # Password per le app di Gmail
EMAIL_RECEIVER = "michelemoretti2024@gmail.com"

# Rate Limiting
MAX_REQUESTS_PER_MINUTE = 15
request_timestamps = deque(maxlen=MAX_REQUESTS_PER_MINUTE)
rate_limit_lock = threading.Lock()

# Contesto predefinito per Gemma
CONTEXT = """rispondi solo in italiano, per domande specifiche dai solo una risposta corta, 
per domande generiche dai una risposta media, per le domande riguardanti la programmazione, 
dai il codice, a meno che non si tratti di una domanda dove la risposta sia testuale e non codice."""

def fine_generazione():
    print("Fatto")

def signal_handler(signum, frame):
    print("\nMonitoraggio terminato.")
    sys.exit(0)

def check_rate_limit():
    """Verifica il rate limit e calcola il tempo di attesa necessario"""
    with rate_limit_lock:
        now = time.time()
        
        # Rimuovi i timestamp più vecchi di 60 secondi
        while request_timestamps and now - request_timestamps[0] > 60:
            request_timestamps.popleft()
        
        # Se abbiamo raggiunto il limite, calcola il tempo di attesa
        if len(request_timestamps) >= MAX_REQUESTS_PER_MINUTE:
            wait_time = 60 - (now - request_timestamps[0])
            return max(0, wait_time)
        
        # Aggiungi il timestamp corrente e restituisci 0 (nessuna attesa necessaria)
        request_timestamps.append(now)
        return 0

def send_email(subject, body):
    """Invia un'email con la risposta di Gemini"""
    try:
        message = MIMEMultipart()
        message["From"] = EMAIL_SENDER
        message["To"] = EMAIL_RECEIVER
        message["Subject"] = subject
        
        message.attach(MIMEText(body, "plain"))
        
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(message)
        
        print(f"Email inviata a {EMAIL_RECEIVER}")
        return True
    except Exception as e:
        print(f"Errore nell'invio dell'email: {str(e)}")
        return False

def query_gemini(text):
    """Invia il testo a Gemini e ottiene la risposta"""
    try:
        # Verifica il rate limit
        wait_time = check_rate_limit()
        if wait_time > 0:
            print(f"\nLimite di richieste raggiunto. Attendo {wait_time:.1f} secondi...")
            time.sleep(wait_time)
        
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
            gemini_response = result['candidates'][0]['content']['parts'][0]['text']
            
            # Invia la risposta via email
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            email_subject = f"Risposta Gemini - {timestamp}"
            email_body = f"Domanda: {text}\n\nRisposta di Gemini:\n{gemini_response}"
            send_email(email_subject, email_body)
            
            return gemini_response
        elif response.status_code == 429:
            error_data = response.json()
            retry_delay = 20  # Default retry delay
            
            # Estrai il retry delay dal messaggio di errore se disponibile
            if 'error' in error_data and 'details' in error_data['error']:
                for detail in error_data['error']['details']:
                    if '@type' == 'type.googleapis.com/google.rpc.RetryInfo' and 'retryDelay' in detail:
                        retry_delay = int(detail['retryDelay'].replace('s', ''))
            
            print(f"\nLimite di richieste API superato. Attendo {retry_delay} secondi prima di riprovare...")
            time.sleep(retry_delay)
            return query_gemini(text)  # Riprova dopo l'attesa
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
    print(f"Le risposte verranno inviate a: {EMAIL_RECEIVER}")
    print(f"Limite richieste: {MAX_REQUESTS_PER_MINUTE} al minuto")
    print("\nPronto a ricevere testo dalla clipboard...")
    
    while True:
        try:
            time.sleep(0.5)  # Ridotto il tempo di attesa per una risposta più veloce
            current_text = pyperclip.paste()
            
            # Debug: mostra il contenuto della clipboard
            if current_text != last_text:
                print("\nNuovo testo rilevato nella clipboard:")
                print("-" * 50)
                print(current_text[:100] + "..." if len(current_text) > 100 else current_text)
                print("-" * 50)
                
                print("\nInvio a Gemini in corso...")
                response = query_gemini(current_text)
                
                print("\nRisposta ricevuta, copio nella clipboard...")
                pyperclip.copy(response)
                print("Risposta di Gemini copiata nella clipboard!")
                fine_generazione()
                last_text = response
                
                print("\nPronto per il prossimo testo...")
            time.sleep(0.5)  # Pausa per non sovraccaricare la CPU
        except Exception as e:
            print(f"\nErrore: {str(e)}")
            print("Tipo di errore:", type(e).__name__)
            print("Dettagli errore:", str(e))
            break

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    monitor_clipboard() 