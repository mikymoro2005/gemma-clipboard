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

# Configurazione API Gemini - Aggiornata con nuova API key
GEMINI_API_KEY = "AIzaSyAKeeh-23wT9hYG69Q3cJSwg_phedHis0c"
BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

# Modello da utilizzare (specifico per evitare errori)
MODEL_NAME = "gemini-2.0-flash"

# Configurazione Email
EMAIL_SENDER = "michelemoretti2025@gmail.com"
EMAIL_PASSWORD = "nqng gquj fqzx nyzq"  # Password per le app di Gmail
EMAIL_RECEIVER = "michelemoretti2024@gmail.com"

# Contesto predefinito per Gemma
CONTEXT = """rispondi solo in italiano, per domande specifiche dai solo una risposta corta, 
per domande generiche dai una risposta media, per le domande riguardanti la programmazione, 
dai il codice, a meno che non si tratti di una domanda dove la risposta sia testuale e non codice."""

def fine_generazione():
    print("Fatto")

def signal_handler(signum, frame):
    print("\nMonitoraggio terminato.")
    sys.exit(0)

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