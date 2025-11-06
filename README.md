# RAG Chat App mit Azure AI Foundry

Eine einfache, kostengünstige Webapp für einen Chat mit deinen RAG-Daten unter Verwendung deiner bestehenden Azure-Infrastruktur (AI Foundry, OpenAI, Blob Storage, AI Search).

## Übersicht

Diese Anwendung ermöglicht es, natürliche Fragen zu deinen Dokumenten zu stellen, die bereits in Azure AI Search indexiert sind. Das System nutzt:

- Azure AI Search für semantische und Vektor-Suche
- Azure OpenAI (GPT-4o) für intelligente Antwortgenerierung
- FastAPI als Backend-Framework
- Einfaches HTML/CSS/JavaScript Frontend

## Voraussetzungen

- Python 3.8+
- Azure AI Foundry Hub mit OpenAI-Modellen (text-embedding-ada-002 und gpt-4o)
- Azure AI Search mit Vector Search
- Blob Storage mit indexierten Dokumenten

## Installation

1. **Repository klonen oder Dateien herunterladen**

2. **Virtuelle Umgebung erstellen und aktivieren:**

```bash
python -m venv venv
source venv/bin/activate  # Unter Windows: venv\Scripts\activate
```

3. **Abhängigkeiten installieren:**

```bash
pip install -r requirements.txt
```

4. **Umgebungsvariablen konfigurieren:**

Kopiere die `.env.example` Datei zu `.env`:

```bash
cp .env.example .env
```

Öffne die `.env` Datei und trage deine Azure-Diensteinstellungen ein:

```
AZURE_SEARCH_ENDPOINT=https://your-search-service.search.windows.net
AZURE_SEARCH_KEY=your-search-key
AZURE_SEARCH_INDEX=your-index-name

AZURE_OPENAI_ENDPOINT=https://your-openai-service.openai.azure.com
AZURE_OPENAI_KEY=your-openai-key
AZURE_OPENAI_DEPLOYMENT=gpt-4o
```

## Starten der Anwendung

Starte den Server mit:

```bash
uvicorn app:app --reload
```

Die Anwendung ist nun unter http://localhost:8000 verfügbar.

## Verwendung

1. Öffne die Anwendung im Browser
2. Gib eine Frage zu deinen Dokumenten ein
3. Die Antwort wird angezeigt, zusammen mit den relevantesten Quellen

## Anpassung

### Anpassung des Prompts

Du kannst den Systempromt im Backend anpassen, um die Antworten für deinen Anwendungsfall zu optimieren. Bearbeite dazu die `generate_answer`-Funktion in `app.py`.

### Styling anpassen

Das Styling kann in der Datei `static/css/styles.css` angepasst werden.

## Deployment

Für die Produktion kannst du die App auf verschiedene Weise hosten:

### Azure App Service

1. Erstelle einen App Service Plan
2. Erstelle eine Web App
3. Aktiviere die Einstellung für Python
4. Setze die Umgebungsvariablen in den App Service-Einstellungen
5. Deploye deinen Code (z.B. mit Git, Azure DevOps, oder GitHub Actions)

### Docker

Alternativ kannst du die Anwendung containerisieren:

1. Dockerfile erstellen
2. Image bauen und in eine Registry pushen
3. In Azure Container Instances oder Kubernetes deployen

## Kosten

Die Kosten für diese Anwendung sind minimal:

- **App Hosting**: Azure App Service Basic Plan (~€10/Monat) oder Free Tier für Entwicklung
- **Azure AI Search**: Bereits in deiner Infrastruktur vorhanden
- **OpenAI Nutzung**: Basierend auf Token-Verbrauch, ca. €0.03 pro 1K Input-Tokens

## Nächste Schritte

- Authentifizierung hinzufügen
- Erweiterte Filtermöglichkeiten implementieren
- Chat-Verlauf speichern
- Frontend mit React/Vue/Angular erweitern für komplexere Benutzeroberfläche
