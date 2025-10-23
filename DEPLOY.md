# 🚀 Guida Deploy DSPyUI

## Passaggio 1: Crea Repository GitHub

1. Vai su [GitHub.com](https://github.com) e fai login
2. Clicca sul `+` in alto a destra → **New repository**
3. Configura:
   - **Repository name**: `DSPyUI`
   - **Description**: "Ottimizzatore di prompt con DSPy e OpenAI"
   - **Visibility**: Public (richiesto per GitHub Pages gratuito)
   - **NON** inizializzare con README, .gitignore o license
4. Clicca **Create repository**

## Passaggio 2: Push del Codice

Copia e incolla questi comandi nel terminale:

```bash
# Aggiungi il remote GitHub (sostituisci 'tuousername' con il tuo username GitHub)
git remote add origin https://github.com/tuousername/DSPyUI.git

# Push del codice
git push -u origin main
```

Se usi autenticazione SSH:
```bash
git remote add origin git@github.com:tuousername/DSPyUI.git
git push -u origin main
```

## Passaggio 3: Configura GitHub Pages

1. Vai su **Settings** del repository
2. Scorri fino a **Pages** (menu laterale)
3. In **Source**, seleziona:
   - **Deploy from a branch**
   - Branch: `main`
   - Folder: `/docs`
4. Clicca **Save**
5. Attendi 2-3 minuti per il deploy
6. Il tuo sito sarà disponibile su: `https://tuousername.github.io/DSPyUI`

## Passaggio 4: Deploy Backend su Render

### Preparazione
1. Aggiorna `docs/app.js`:
   - Trova la riga con `API_URL`
   - Cambierà da `https://dspyui-backend.onrender.com` al tuo URL Render (lo otterrai dopo il deploy)

### Deploy su Render
1. Vai su [Render.com](https://render.com) e registrati/login
2. Clicca **New +** → **Web Service**
3. Connetti il tuo account GitHub
4. Seleziona il repository `DSPyUI`
5. Configura il servizio:
   - **Name**: `dspyui-backend` (o qualsiasi nome)
   - **Region**: Scegli la più vicina
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`
6. Seleziona **Free** plan
7. Clicca **Advanced** e aggiungi Environment Variables:
   - `OPENAI_API_KEY`: [La tua API key OpenAI]
   - `FRONTEND_URL`: `https://tuousername.github.io/DSPyUI`
8. Clicca **Create Web Service**

### Post-Deploy
1. Copia l'URL del tuo servizio Render (es: `https://dspyui-backend-xyz.onrender.com`)
2. Aggiorna `docs/app.js` con questo URL
3. Commit e push:
   ```bash
   git add docs/app.js
   git commit -m "Update backend URL"
   git push
   ```

## Passaggio 5: Verifica

1. **Backend**: Visita `https://tuo-backend.onrender.com/health`
   - Dovresti vedere: `{"status":"healthy",...}`

2. **Frontend**: Visita `https://tuousername.github.io/DSPyUI`
   - L'interfaccia dovrebbe caricarsi correttamente

3. **Test completo**:
   - Inserisci un prompt di test
   - Inserisci uno scopo
   - Clicca "Ottimizza Prompt"
   - Prima richiesta potrebbe richiedere ~30s (risveglio backend)

## 🔧 Troubleshooting

### "Permission denied" durante git push
```bash
# Configura credenziali GitHub
git config --global user.name "Tuo Nome"
git config --global user.email "tua-email@example.com"
```

### GitHub Pages non funziona
- Verifica che il repository sia pubblico
- Controlla Settings → Pages per vedere lo stato del deploy
- Potrebbe richiedere fino a 10 minuti la prima volta

### Backend non risponde
- Controlla i log su Render Dashboard
- Verifica che OPENAI_API_KEY sia configurata
- Attendi 30 secondi se è la prima richiesta

### Errore CORS
- Assicurati che FRONTEND_URL su Render corrisponda esattamente al tuo URL GitHub Pages
- Non dimenticare `https://` nel URL

## 📝 Note Importanti

- **Piano Gratuito Render**: Il backend "dorme" dopo 15 minuti di inattività
- **Prima Richiesta**: Può richiedere ~30 secondi per risvegliare il backend
- **API Key**: Non condividere mai la tua OPENAI_API_KEY pubblicamente
- **Crediti OpenAI**: Assicurati di avere crediti sufficienti

## ✅ Checklist Finale

- [ ] Repository GitHub creato e codice pushato
- [ ] GitHub Pages attivo e funzionante
- [ ] Backend Render deployato con API key configurata
- [ ] URL backend aggiornato in `docs/app.js`
- [ ] Test end-to-end completato con successo

Congratulazioni! Il tuo DSPyUI è ora live e accessibile pubblicamente! 🎉