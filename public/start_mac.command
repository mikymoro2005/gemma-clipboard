#!/bin/bash
echo "Scaricamento dello script Python..."
curl -o gemma_clipboard.py http://localhost:5000/gemma_clipboard.py
echo "Avvio dello script..."
python3 gemma_clipboard.py 