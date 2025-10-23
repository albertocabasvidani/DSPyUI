# DSPyUI - Ottimizzatore di Prompt 🎯

Un'interfaccia web per ottimizzare i prompt usando la libreria DSPy e OpenAI. Soluzione completamente gratuita con hosting su GitHub Pages (frontend) e Render (backend).

## 🚀 Demo Live

- **Frontend**: `https://[tuousername].github.io/DSPyUI`
- **Backend**: `https://dspyui-backend.onrender.com`

## ✨ Funzionalità

- **Ottimizzazione Automatica**: Usa DSPy per migliorare i tuoi prompt
- **Spiegazioni Dettagliate**: Comprendi perché sono state apportate modifiche
- **Metriche di Qualità**: Valutazione della chiarezza, specificità, struttura e completezza
- **Confronto Visivo**: Visualizza side-by-side originale vs ottimizzato
- **Storia Locale**: Salvataggio automatico in localStorage
- **100% Gratuito**: Nessun costo di hosting

## 🛠️ Tecnologie

- **Frontend**: HTML5, CSS3, JavaScript vanilla (GitHub Pages)
- **Backend**: Python, FastAPI, DSPy, OpenAI API (Render)
- **Deployment**: GitHub Pages + Render (entrambi gratuiti)

## 📋 Prerequisiti

- Account GitHub
- Account Render (gratuito)
- OpenAI API Key

## 🔧 Installazione

### 1. Fork e Clone

```bash
# Fork questo repository dal tuo account GitHub
# Poi clona il tuo fork
git clone https://github.com/[tuousername]/DSPyUI.git
cd DSPyUI
```

### 2. Configurazione Backend Locale (Opzionale)

```bash
# Crea ambiente virtuale
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oppure
venv\Scripts\activate  # Windows

# Installa dipendenze
cd backend
pip install -r requirements.txt

# Copia e configura .env
cp ../.env.example .env
# Modifica .env con la tua OPENAI_API_KEY

# Avvia server locale
uvicorn app:app --reload
```

### 3. Test Frontend Locale

```bash
# Dalla directory docs/
python -m http.server 8080
# Apri http://localhost:8080
```

## 🌐 Deployment

### Backend su Render

1. Crea account su [Render](https://render.com)
2. Connetti il tuo repository GitHub
3. Crea nuovo Web Service:
   - **Name**: `dspyui-backend`
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`
4. Aggiungi variabile ambiente:
   - `OPENAI_API_KEY`: La tua API key OpenAI
   - `FRONTEND_URL`: `https://[tuousername].github.io/DSPyUI`

### Frontend su GitHub Pages

1. Modifica `docs/app.js`:
   - Aggiorna `API_URL` con il tuo URL Render
2. Commit e push:
   ```bash
   git add .
   git commit -m "Setup deployment"
   git push origin main
   ```
3. Vai su GitHub Settings → Pages
4. Source: Deploy from branch
5. Branch: `main` → `/docs`
6. Salva e attendi il deploy (~2 minuti)

## 📝 Utilizzo

1. **Inserisci il Prompt Originale**: Il prompt che vuoi ottimizzare
2. **Descrivi lo Scopo**: Cosa deve fare questo prompt
3. **Aggiungi Esempi** (opzionale): Input/output attesi
4. **Clicca Ottimizza**: Ricevi il prompt migliorato con spiegazioni

## 🔍 Struttura Progetto

```
DSPyUI/
├── backend/                 # Backend FastAPI
│   ├── app.py              # Server principale
│   ├── prompt_optimizer.py # Logica DSPy
│   ├── models.py           # Modelli Pydantic
│   ├── requirements.txt    # Dipendenze Python
│   └── render.yaml         # Config Render
├── docs/                   # Frontend (GitHub Pages)
│   ├── index.html         # Pagina principale
│   ├── app.js             # Logica JavaScript
│   └── styles.css         # Stili CSS
├── .gitignore
├── .env.example           # Template variabili
├── LICENSE
└── README.md
```

## ⚠️ Limitazioni Piano Gratuito

- **Render**: Il backend "dorme" dopo 15 minuti di inattività
  - Prima richiesta dopo sleep: ~30 secondi di attesa
  - 750 ore/mese di esecuzione (più che sufficiente per uso personale)
- **GitHub Pages**: Nessun limite per siti statici

## 🤝 Contribuire

1. Fork il progetto
2. Crea feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit modifiche (`git commit -m 'Add AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Apri Pull Request

## 📄 Licenza

Distribuito sotto licenza MIT. Vedi `LICENSE` per maggiori informazioni.

## 🙏 Riconoscimenti

- [DSPy](https://github.com/stanfordnlp/dspy) - Stanford NLP
- [FastAPI](https://fastapi.tiangolo.com/)
- [OpenAI](https://openai.com/)

## 📧 Contatti

- GitHub: [@tuousername](https://github.com/tuousername)

## 🐛 Troubleshooting

### Backend non risponde
- Attendi ~30 secondi se è la prima richiesta
- Verifica che l'URL Render sia corretto in `app.js`
- Controlla i log su Render Dashboard

### Errore CORS
- Assicurati che `FRONTEND_URL` sia configurato su Render
- Verifica che l'URL nel frontend corrisponda

### Errore API Key
- Verifica che `OPENAI_API_KEY` sia configurata su Render
- Controlla che la key sia valida e abbia crediti

## 🚀 Prossime Features

- [ ] Supporto per multiple lingue
- [ ] Export/Import prompt ottimizzati
- [ ] Template predefiniti per casi comuni
- [ ] Integrazione con altri modelli LLM
- [ ] Dark mode