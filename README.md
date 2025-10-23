# DSPyUI - Prompt Optimizer 🎯

A web interface to optimize prompts using the DSPy library and OpenAI. Completely free solution with hosting on GitHub Pages (frontend) and Render (backend).

## 🚀 Live Demo

- **Frontend**: `https://albertocabasvidani.github.io/DSPyUI`
- **Backend**: `https://dspyui-backend.onrender.com` (to be configured)

## ✨ Features

- **Automatic Optimization**: Uses DSPy with advanced features to improve your prompts
  - **Base Mode**: ChainOfThought with custom signature
  - **Few-Shot Mode**: BootstrapFewShot when you provide examples (optional)
- **Intelligent Validation**: DSPy Assert and Suggest to ensure output quality
- **LM-Based Metrics**: AI evaluation of clarity, specificity, structure, and completeness
- **Detailed Explanations**: Understand why changes were made
- **Visual Comparison**: View original vs optimized side-by-side
- **Local History**: Automatic saving in localStorage
- **100% Free**: No hosting costs

## 🛠️ Technologies

- **Frontend**: HTML5, CSS3, Vanilla JavaScript (GitHub Pages)
- **Backend**: Python, FastAPI, DSPy, OpenAI API (Render)
- **Deployment**: GitHub Pages + Render (both free)

## 📋 Prerequisites

- GitHub Account
- Render Account (free)
- OpenAI API Key

## 🔧 Installation

### 1. Fork and Clone

```bash
# Clone the repository
git clone https://github.com/albertocabasvidani/DSPyUI.git
cd DSPyUI
```

### 2. Local Backend Configuration (Optional)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
cd backend
pip install -r requirements.txt

# Copy and configure .env
cp ../.env.example .env
# Edit .env with your OPENAI_API_KEY

# Start local server
uvicorn app:app --reload
```

### 3. Test Frontend Locally

```bash
# From docs/ directory
python -m http.server 8080
# Open http://localhost:8080
```

## 🌐 Deployment

### Backend on Render

1. Create account on [Render](https://render.com)
2. Connect your GitHub repository
3. Create new Web Service:
   - **Name**: `dspyui-backend`
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`
4. Add environment variables:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `FRONTEND_URL`: `https://albertocabasvidani.github.io/DSPyUI`

### Frontend on GitHub Pages

1. Edit `docs/app.js`:
   - Update `API_URL` with your Render URL
2. Commit and push:
   ```bash
   git add .
   git commit -m "Setup deployment"
   git push origin main
   ```
3. Go to GitHub Settings → Pages
4. Source: Deploy from branch
5. Branch: `main` → `/docs`
6. Save and wait for deployment (~2 minutes)

## 📝 Usage

1. **Enter Original Prompt**: The prompt you want to optimize
2. **Describe Purpose**: What this prompt should do
3. **Add Examples** (optional): Expected input/output
4. **Click Optimize**: Receive improved prompt with explanations

## 🔍 Project Structure

```
DSPyUI/
├── backend/                 # FastAPI Backend
│   ├── app.py              # Main server
│   ├── prompt_optimizer.py # DSPy logic
│   ├── models.py           # Pydantic models
│   ├── requirements.txt    # Python dependencies
│   └── render.yaml         # Render config
├── docs/                   # Frontend (GitHub Pages)
│   ├── index.html         # Main page
│   ├── app.js             # JavaScript logic
│   └── styles.css         # CSS styles
├── .gitignore
├── .env.example           # Environment variables template
├── LICENSE
└── README.md
```

## ⚠️ Free Tier Limitations

- **Render**: Backend "sleeps" after 15 minutes of inactivity
  - First request after sleep: ~30 seconds wait time
  - 750 hours/month execution (more than enough for personal use)
- **GitHub Pages**: No limits for static sites

## 🤝 Contributing

1. Fork the project
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 License

Distributed under MIT License. See `LICENSE` for more information.

## 🙏 Acknowledgments

- [DSPy](https://github.com/stanfordnlp/dspy) - Stanford NLP
- [FastAPI](https://fastapi.tiangolo.com/)
- [OpenAI](https://openai.com/)

## 📧 Contact

- GitHub: [@albertocabasvidani](https://github.com/albertocabasvidani)

## 🐛 Troubleshooting

### Backend not responding
- Wait ~30 seconds if it's the first request
- Verify that the Render URL is correct in `app.js`
- Check logs on Render Dashboard

### CORS Error
- Make sure `FRONTEND_URL` is configured on Render
- Verify that the URL in frontend matches

### API Key Error
- Verify that `OPENAI_API_KEY` is configured on Render
- Check that the key is valid and has credits

## 🚀 Upcoming Features

- [x] Few-shot learning with examples (✓ Implemented)
- [x] Validation with DSPy Assertions (✓ Implemented)
- [x] LM-based metrics (✓ Implemented)
- [ ] Multi-language support
- [ ] Export/Import optimized prompts
- [ ] Predefined templates for common cases
- [ ] Integration with other LLM models (Anthropic, Gemini, etc.)
- [ ] Dark mode