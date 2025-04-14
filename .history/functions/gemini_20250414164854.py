import json
import os
import requests
from datetime import datetime

def handler(event, context):
    # Verifica il metodo della richiesta
    if event['httpMethod'] != 'POST':
        return {
            'statusCode': 405,
            'body': json.dumps({'error': 'Method not allowed'})
        }

    try:
        # Ottieni il corpo della richiesta
        body = json.loads(event['body'])
        text = body.get('text', '')

        # Configurazione API Gemini
        GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
        BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
        MODEL_NAME = "gemini-2.0-flash"

        # Contesto predefinito
        CONTEXT = """rispondi solo in italiano, per domande specifiche dai solo una risposta corta, 
        per domande generiche dai una risposta media, per le domande riguardanti la programmazione, 
        dai il codice, a meno che non si tratti di una domanda dove la risposta sia testuale e non codice."""

        # Prepara la richiesta per Gemini
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
        
        # Invia la richiesta a Gemini
        response = requests.post(
            f"{api_url}?key={GEMINI_API_KEY}",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            result = response.json()
            gemini_response = result['candidates'][0]['content']['parts'][0]['text']
            
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS'
                },
                'body': json.dumps({
                    'response': gemini_response
                })
            }
        else:
            return {
                'statusCode': response.status_code,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS'
                },
                'body': json.dumps({
                    'error': response.text
                })
            }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': json.dumps({
                'error': str(e)
            })
        } 