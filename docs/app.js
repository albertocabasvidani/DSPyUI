// Configuration
const CONFIG = {
    // Backend URL - Update this with your Render deployment URL
    API_URL: window.location.hostname === 'localhost'
        ? 'http://localhost:8000'
        : 'https://dspyui-backend.onrender.com',

    // LocalStorage keys
    STORAGE_KEYS: {
        HISTORY: 'dspyui_history',
        LAST_REQUEST: 'dspyui_last_request'
    }
};

// DOM Elements
const elements = {
    originalPrompt: document.getElementById('original-prompt'),
    purpose: document.getElementById('purpose'),
    optimizeBtn: document.getElementById('optimize-btn'),
    resultsSection: document.getElementById('results-section'),
    optimizedPrompt: document.getElementById('optimized-prompt'),
    improvementsList: document.getElementById('improvements-list'),
    explanationText: document.getElementById('explanation-text'),
    metricsGrid: document.getElementById('metrics-grid'),
    originalComparison: document.getElementById('original-comparison'),
    optimizedComparison: document.getElementById('optimized-comparison'),
    errorMessage: document.getElementById('error-message'),
    toast: document.getElementById('toast'),
    toastMessage: document.getElementById('toast-message'),
    addExampleBtn: document.getElementById('add-example-btn'),
    examplesContainer: document.getElementById('examples-container'),
    clearHistory: document.getElementById('clear-history')
};

// State
let examples = [];
let isLoading = false;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadLastRequest();
    setupEventListeners();
    checkBackendHealth();
});

// Event Listeners
function setupEventListeners() {
    elements.optimizeBtn.addEventListener('click', optimizePrompt);
    elements.addExampleBtn.addEventListener('click', addExample);
    elements.clearHistory.addEventListener('click', clearHistory);

    // Copy buttons
    document.addEventListener('click', (e) => {
        if (e.target.classList.contains('copy-btn')) {
            copyToClipboard(e.target);
        }
    });

    // Auto-save to localStorage
    elements.originalPrompt.addEventListener('input', saveToLocalStorage);
    elements.purpose.addEventListener('input', saveToLocalStorage);
}

// Check backend health
async function checkBackendHealth() {
    try {
        const response = await fetch(`${CONFIG.API_URL}/health`);
        if (!response.ok) {
            showToast('⚠️ Backend potrebbe essere in avvio. Prima richiesta potrebbe richiedere ~30s', 'warning', 5000);
        }
    } catch (error) {
        showToast('⚠️ Backend non raggiungibile. Controllare la connessione', 'error', 5000);
    }
}

// Optimize prompt
async function optimizePrompt() {
    if (isLoading) return;

    const originalPrompt = elements.originalPrompt.value.trim();
    const purpose = elements.purpose.value.trim();

    if (!originalPrompt || !purpose) {
        showError('Per favore inserisci sia il prompt che lo scopo');
        return;
    }

    isLoading = true;
    setLoadingState(true);
    hideError();

    const requestData = {
        original_prompt: originalPrompt,
        purpose: purpose,
        examples: examples.length > 0 ? examples : null,
        temperature: 0.7
    };

    try {
        const response = await fetch(`${CONFIG.API_URL}/optimize`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        displayResults(data);
        saveToHistory(requestData, data);

    } catch (error) {
        console.error('Error:', error);
        if (error.message.includes('Failed to fetch')) {
            showError('Impossibile connettersi al backend. Il servizio potrebbe essere in avvio (attendi ~30s e riprova)');
        } else {
            showError(`Errore durante l'ottimizzazione: ${error.message}`);
        }
    } finally {
        isLoading = false;
        setLoadingState(false);
    }
}

// Display results
function displayResults(data) {
    // Show results section
    elements.resultsSection.classList.remove('hidden');

    // Optimized prompt
    elements.optimizedPrompt.textContent = data.optimized_prompt;

    // Improvements list
    elements.improvementsList.innerHTML = '';
    data.improvements.forEach(improvement => {
        const li = document.createElement('li');
        li.textContent = improvement;
        elements.improvementsList.appendChild(li);
    });

    // Explanation
    elements.explanationText.textContent = data.explanation;

    // Metrics
    if (data.metrics) {
        displayMetrics(data.metrics);
    }

    // Comparison
    elements.originalComparison.textContent = data.original_prompt;
    elements.optimizedComparison.textContent = data.optimized_prompt;

    // Scroll to results
    elements.resultsSection.scrollIntoView({ behavior: 'smooth' });

    showToast('✅ Prompt ottimizzato con successo!', 'success');
}

// Display metrics
function displayMetrics(metrics) {
    elements.metricsGrid.innerHTML = '';

    const metricNames = {
        clarity_score: 'Chiarezza',
        specificity_score: 'Specificità',
        structure_score: 'Struttura',
        completeness_score: 'Completezza'
    };

    for (const [key, value] of Object.entries(metrics)) {
        const metricDiv = document.createElement('div');
        metricDiv.className = 'metric-item';

        const label = document.createElement('span');
        label.className = 'metric-label';
        label.textContent = metricNames[key] || key;

        const progressBar = document.createElement('div');
        progressBar.className = 'progress-bar';

        const progress = document.createElement('div');
        progress.className = 'progress';
        progress.style.width = `${value * 100}%`;
        progress.style.backgroundColor = getColorForScore(value);

        const valueSpan = document.createElement('span');
        valueSpan.className = 'metric-value';
        valueSpan.textContent = `${(value * 100).toFixed(0)}%`;

        progressBar.appendChild(progress);
        metricDiv.appendChild(label);
        metricDiv.appendChild(progressBar);
        metricDiv.appendChild(valueSpan);

        elements.metricsGrid.appendChild(metricDiv);
    }
}

// Get color for score
function getColorForScore(score) {
    if (score >= 0.8) return '#10b981';
    if (score >= 0.6) return '#3b82f6';
    if (score >= 0.4) return '#f59e0b';
    return '#ef4444';
}

// Add example
function addExample() {
    const exampleDiv = document.createElement('div');
    exampleDiv.className = 'example-item';
    exampleDiv.innerHTML = `
        <div class="example-inputs">
            <input type="text" placeholder="Input esempio" class="example-input">
            <input type="text" placeholder="Output atteso" class="example-output">
            <button type="button" class="remove-example-btn">✕</button>
        </div>
    `;

    const removeBtn = exampleDiv.querySelector('.remove-example-btn');
    removeBtn.addEventListener('click', () => {
        exampleDiv.remove();
        updateExamples();
    });

    const inputs = exampleDiv.querySelectorAll('input');
    inputs.forEach(input => {
        input.addEventListener('input', updateExamples);
    });

    elements.examplesContainer.appendChild(exampleDiv);
}

// Update examples array
function updateExamples() {
    examples = [];
    const exampleItems = document.querySelectorAll('.example-item');

    exampleItems.forEach(item => {
        const inputField = item.querySelector('.example-input').value.trim();
        const outputField = item.querySelector('.example-output').value.trim();

        if (inputField || outputField) {
            examples.push({
                input: inputField,
                output: outputField
            });
        }
    });
}

// Copy to clipboard
async function copyToClipboard(button) {
    const targetId = button.getAttribute('data-target');
    const targetElement = document.getElementById(targetId);
    const text = targetElement.textContent;

    try {
        await navigator.clipboard.writeText(text);
        showToast('📋 Copiato negli appunti!', 'success');
    } catch (err) {
        console.error('Failed to copy:', err);
        showToast('Errore nella copia', 'error');
    }
}

// LocalStorage functions
function saveToLocalStorage() {
    const data = {
        originalPrompt: elements.originalPrompt.value,
        purpose: elements.purpose.value,
        examples: examples
    };
    localStorage.setItem(CONFIG.STORAGE_KEYS.LAST_REQUEST, JSON.stringify(data));
}

function loadLastRequest() {
    const savedData = localStorage.getItem(CONFIG.STORAGE_KEYS.LAST_REQUEST);
    if (savedData) {
        try {
            const data = JSON.parse(savedData);
            elements.originalPrompt.value = data.originalPrompt || '';
            elements.purpose.value = data.purpose || '';

            if (data.examples && data.examples.length > 0) {
                data.examples.forEach(example => {
                    addExample();
                    const lastItem = elements.examplesContainer.lastElementChild;
                    lastItem.querySelector('.example-input').value = example.input || '';
                    lastItem.querySelector('.example-output').value = example.output || '';
                });
                updateExamples();
            }
        } catch (error) {
            console.error('Error loading saved data:', error);
        }
    }
}

function saveToHistory(request, response) {
    const history = getHistory();
    const entry = {
        timestamp: new Date().toISOString(),
        request: request,
        response: response
    };

    history.unshift(entry);
    // Keep only last 10 entries
    if (history.length > 10) {
        history.pop();
    }

    localStorage.setItem(CONFIG.STORAGE_KEYS.HISTORY, JSON.stringify(history));
}

function getHistory() {
    const saved = localStorage.getItem(CONFIG.STORAGE_KEYS.HISTORY);
    return saved ? JSON.parse(saved) : [];
}

function clearHistory(e) {
    e.preventDefault();
    if (confirm('Vuoi davvero cancellare la cronologia?')) {
        localStorage.removeItem(CONFIG.STORAGE_KEYS.HISTORY);
        localStorage.removeItem(CONFIG.STORAGE_KEYS.LAST_REQUEST);
        elements.originalPrompt.value = '';
        elements.purpose.value = '';
        elements.examplesContainer.innerHTML = '';
        examples = [];
        elements.resultsSection.classList.add('hidden');
        showToast('🗑️ Cronologia cancellata', 'info');
    }
}

// UI Helper functions
function setLoadingState(loading) {
    if (loading) {
        elements.optimizeBtn.classList.add('loading');
        elements.optimizeBtn.disabled = true;
    } else {
        elements.optimizeBtn.classList.remove('loading');
        elements.optimizeBtn.disabled = false;
    }
}

function showError(message) {
    elements.errorMessage.textContent = message;
    elements.errorMessage.classList.remove('hidden');
}

function hideError() {
    elements.errorMessage.classList.add('hidden');
}

function showToast(message, type = 'info', duration = 3000) {
    elements.toastMessage.textContent = message;
    elements.toast.className = `toast ${type}`;
    elements.toast.classList.remove('hidden');

    setTimeout(() => {
        elements.toast.classList.add('hidden');
    }, duration);
}