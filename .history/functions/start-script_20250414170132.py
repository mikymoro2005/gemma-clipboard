import json
import os
import subprocess
import platform

def handler(event, context):
    try:
        # Determina il comando corretto in base al sistema operativo
        if platform.system() == "Windows":
            command = ["python", "gemma_clipboard.py"]
        else:
            command = ["python3", "gemma_clipboard.py"]
        
        # Avvia il processo in background
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': json.dumps({
                'message': 'Script avviato con successo'
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