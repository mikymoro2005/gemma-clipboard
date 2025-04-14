#!/bin/bash
echo "Installing required packages..."
pip3 install -r requirements.txt
echo "Starting Gemma Clipboard Manager..."
python3 gemma_clipboard.py 