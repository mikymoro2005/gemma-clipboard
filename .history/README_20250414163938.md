# Gemma Clipboard Manager

Un'applicazione web che permette di scaricare e avviare automaticamente lo script Gemma Clipboard.

## Funzionalità

- Interfaccia web per gestire lo script
- Download del file Python
- Avvio automatico dello script
- Monitoraggio della clipboard
- Integrazione con Google Gemini API
- Invio delle risposte via email

## Requisiti

- Python 3.6+
- Flask
- pyperclip
- requests

## Installazione

1. Clona o scarica questo repository
2. Installa le dipendenze:
   ```
   pip install -r requirements.txt
   ```

## Utilizzo

1. Avvia il server web:
   ```
   python app.py
   ```
2. Apri il browser e vai a `http://localhost:5000`
3. Clicca su "Scarica Script" per scaricare il file Python
4. Clicca su "Avvia Script" per eseguire il programma
5. Il programma monitorerà la tua clipboard
6. Quando copi un testo, verrà inviato a Gemini e la risposta verrà copiata nella clipboard
7. Clicca su "Ferma Script" per terminare il programma

## Configurazione

Puoi modificare le seguenti variabili nel file `gemma_clipboard.py`:

- `GEMINI_API_KEY`: La tua API key di Google Gemini
- `EMAIL_SENDER`: L'indirizzo email mittente
- `EMAIL_PASSWORD`: La password per le app di Gmail
- `EMAIL_RECEIVER`: L'indirizzo email destinatario

## Note

- Assicurati di avere Python installato sul tuo sistema
- Per l'invio di email, è necessario utilizzare una password per app di Gmail
- Lo script deve essere eseguito con privilegi sufficienti per accedere alla clipboard 