FROM python:3.10-slim

WORKDIR /app

# Abhängigkeiten installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Anwendungsdateien kopieren
COPY . .

# Port freigeben
EXPOSE 8000

# Anwendung starten
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
