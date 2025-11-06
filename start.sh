#!/bin/bash

# Überprüfen, ob Python installiert ist
if ! command -v python3 &> /dev/null; then
    echo "Python 3 ist nicht installiert. Bitte installiere Python 3."
    exit 1
fi

# Überprüfen, ob eine virtuelle Umgebung existiert
if [ ! -d "venv" ]; then
    echo "Erstelle virtuelle Umgebung..."
    python3 -m venv venv
fi

# Aktiviere virtuelle Umgebung
source venv/bin/activate

# Installiere Abhängigkeiten
echo "Installiere Abhängigkeiten..."
pip install -r requirements.txt

# Überprüfe, ob .env existiert
if [ ! -f ".env" ]; then
    echo "Keine .env Datei gefunden. Kopiere .env.example zu .env..."
    cp .env.example .env
    echo "Bitte bearbeite die .env Datei mit deinen Azure-Diensteinstellungen."
    exit 1
fi

# Starte die App
echo "Starte die RAG Chat App..."
uvicorn app:app --reload
