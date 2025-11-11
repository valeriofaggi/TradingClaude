# 🤖 Context File per Claude - Trading Predictor

Questo file contiene tutte le informazioni necessarie per riprendere lo sviluppo del progetto Trading Predictor.

**Istruzioni per Claude**: Leggi questo file all'inizio della sessione per avere il contesto completo del progetto.

---

## 📋 Informazioni Progetto

### Nome Progetto
**Trading Predictor - Versione Ibrida**

### Descrizione
Sistema di analisi e previsione prezzi azionari con architettura cloud-locale ibrida:
- Raccolta dati automatica 24/7 su GitHub Actions
- Dashboard Streamlit interattiva su PC locale
- Machine Learning: Prophet + Random Forest
- 10 titoli azionari italiani (FTSE MIB)

### Versione Attuale
**2.0** - Sistema Ibrido completamente operativo ✅

### Data Ultimo Aggiornamento
**2025-11-11**

---

## 🗂️ Percorsi e Struttura

### Percorsi Principali

```
Progetto Base:
D:\Programmi2\TRADING Ibrido\

Python Interpreter:
D:\Programmi2\Pyton\python.exe

Versione Beta (Backup):
D:\Programmi2\TRADING By Claude COde\
```

### Struttura Completa Progetto

```
D:\Programmi2\TRADING Ibrido\
│
├── .github/workflows/              # GitHub Actions
│   └── data_collection.yml        # Workflow raccolta dati (ogni 15 min)
│
├── collector/                      # Script raccolta dati per cloud
│   ├── collect_data.py            # Script principale (Yahoo Finance)
│   └── requirements.txt           # Dipendenze minimali cloud
│
├── dashboard/                      # Dashboard Streamlit
│   └── app.py                     # Applicazione principale (1400+ righe)
│
├── models/                         # Modelli Machine Learning
│   ├── __init__.py
│   └── predictor.py               # Logica predizione (Prophet + RF)
│
├── utils/                          # Utilità condivise
│   ├── __init__.py
│   ├── data_collector.py          # Collezione dati locale
│   ├── technical_indicators.py    # Indicatori tecnici
│   ├── sentiment_analyzer.py      # Analisi sentiment
│   └── prediction_logger.py       # Log previsioni
│
├── config/                         # Configurazione
│   ├── __init__.py
│   └── config.py                  # Settings globali
│
├── data/                           # Dati (sync da GitHub)
│   ├── ENI_MI_historical.csv      # ~506 giorni per titolo
│   ├── ISP_MI_historical.csv
│   ├── ... (altri 8 titoli)
│   ├── predictions_history.csv    # Storico previsioni
│   └── custom_stocks.json         # Lista titoli personalizzata
│
├── logs/                           # Log sistema
│   └── collection.log             # Log raccolte GitHub Actions
│
├── sync_data.py                    # Script sincronizzazione Git
├── requirements.txt                # Dipendenze complete
├── .gitignore                      # File da ignorare
│
├── README.md                       # Documentazione completa utente
├── QUICK_START.md                  # Guida avvio rapido
├── PRESENTAZIONE_APP.md            # Presentazione sistema
├── GITHUB_SETUP_GUIDE.md           # Guida setup GitHub
├── SESSION_SUMMARY.md              # Documentazione tecnica sviluppo
└── CONTEXT_FOR_CLAUDE.md           # Questo file
```

---

## 🔗 Repository GitHub

### Informazioni Repository

```
Owner: valeriofaggi
Nome: TradingClaude
URL: https://github.com/valeriofaggi/TradingClaude
Visibilità: Private
Branch principale: main
```

### GitHub Actions

**Workflow**: Stock Data Collection
- **File**: `.github/workflows/data_collection.yml`
- **Schedule**: Ogni 15 minuti, 7:00-17:00 UTC, Lun-Ven
- **Trigger**: Push su main, workflow_dispatch (manuale)
- **Jobs**:
  1. Checkout repository
  2. Setup Python 3.11
  3. Install dependencies
  4. Run `collector/collect_data.py`
  5. Git commit + push dati
  6. Job summary

**Permessi**: Read and write (configurato)

### Token GitHub

- Token salvato in Git config (non committato)
- Scopes: repo, workflow
- Usato per push/pull automatici

---

## 📊 Dashboard Streamlit

### Comando Avvio

```bash
cd "D:\Programmi2\TRADING Ibrido"
"D:\Programmi2\Pyton\python.exe" -m streamlit run dashboard/app.py
```

### URL Locale

**Default**: http://localhost:8501
**Alternative**: http://localhost:8502, 8503, ecc.

### Sezioni Dashboard (8 Tab)

1. **🌐 Panoramica Completa** - Tutti i 10 titoli
2. **📈 Titolo Selezionato** - Analisi dettagliata
3. **⏱️ 2 Ore** - Previsioni breve termine
4. **📅 1 Giorno** - Previsioni giornaliere
5. **📅 3 Giorni** - Previsioni medio termine
6. **📅 7 Giorni** - Previsioni settimanali
7. **🎯 Accuratezza Modello** - Metriche performance
8. **📊 Grafici Accuratezza** - Visualizzazioni avanzate

### Caratteristiche UI

- **Scrolling orizzontale tab** con scrollbar visibile
- **Sidebar**: Selezione titoli, gestione lista, auto-refresh
- **Sync automatico** da GitHub all'avvio
- **Color coding**: Verde (rialzi), Rosso (ribassi)
- **Grafici interattivi**: Plotly
- **Session state**: Gestione stato applicazione

---

## 🎯 Titoli Azionari Tracciati

### Lista Corrente (10 titoli)

```python
TOP_ITALIAN_STOCKS = [
    "ENI.MI",      # Eni
    "ISP.MI",      # Intesa Sanpaolo
    "UCG.MI",      # UniCredit
    "ENEL.MI",     # Enel
    "A2A.MI",      # A2A
    "TIT.MI",      # Telecom Italia
    "G.MI",        # Generali
    "RACE.MI",     # Ferrari
    "BAMI.MI",     # Banco BPM
    "TEN.MI",      # Tenaris
]
```

### Personalizzazione

Gli utenti possono aggiungere/rimuovere titoli dalla sidebar.
Lista salvata in: `data/custom_stocks.json`

---

## 🧠 Machine Learning

### Algoritmi

1. **Prophet** (Facebook)
   - Time series forecasting
   - Gestione trend e stagionalità
   - File: `models/predictor.py`

2. **Random Forest**
   - Ensemble learning
   - Features: prezzi, volumi, indicatori tecnici
   - File: `models/predictor.py`

### Orizzonti Temporali

```python
ML_CONFIG = {
    "forecast_horizons": {
        "2h": 2,    # 2 ore
        "1d": 1,    # 1 giorno
        "3d": 3,    # 3 giorni
        "7d": 7,    # 7 giorni
    }
}
```

### Indicatori Tecnici

```python
TECHNICAL_INDICATORS = [
    "SMA_20", "SMA_50", "SMA_200",  # Simple Moving Averages
    "EMA_12", "EMA_26",              # Exponential Moving Averages
    "RSI_14",                        # Relative Strength Index
    "MACD",                          # Moving Average Convergence Divergence
    "BB_UPPER", "BB_LOWER",          # Bollinger Bands
    "ATR",                           # Average True Range
    "OBV",                           # On-Balance Volume
]
```

---

## 🔧 Tecnologie e Dipendenze

### Dipendenze Principali

```
# Data & ML
pandas>=2.2.3
numpy>=1.26.4
scikit-learn>=1.5.0
prophet>=1.1.5

# Data Collection
yfinance==0.2.40
finnhub-python==2.4.19 (opzionale)

# Dashboard
streamlit>=1.40.0
plotly>=5.24.0

# Technical Analysis
ta==0.11.0
pandas-ta>=0.3.14b

# Utilities
python-dotenv==1.0.0
tqdm>=4.67.1
```

### Versione Python

**Minima**: Python 3.10+
**Raccomandata**: Python 3.11
**Attuale sistema**: Python 3.13

---

## 🚀 Comandi Essenziali

### Avvio Dashboard

```bash
cd "D:\Programmi2\TRADING Ibrido"
"D:\Programmi2\Pyton\python.exe" -m streamlit run dashboard/app.py
```

### Sincronizzazione Dati

```bash
# Manuale Git
cd "D:\Programmi2\TRADING Ibrido"
git pull

# Script automatico
"D:\Programmi2\Pyton\python.exe" sync_data.py
```

### Test Collector

```bash
cd "D:\Programmi2\TRADING Ibrido"
"D:\Programmi2\Pyton\python.exe" collector/collect_data.py
```

### Git Operations

```bash
# Status
git status

# Commit
git add .
git commit -m "Descrizione modifiche"
git push

# Pull
git pull

# Log
git log --oneline -5

# Branch
git branch
```

### Gestione Dipendenze

```bash
# Installa tutte
"D:\Programmi2\Pyton\python.exe" -m pip install -r requirements.txt --upgrade

# Installa singola
"D:\Programmi2\Pyton\python.exe" -m pip install package_name

# Lista installate
"D:\Programmi2\Pyton\python.exe" -m pip list
```

---

## 🔄 Workflow Completo Sistema

### 1. Raccolta Dati (Cloud - GitHub Actions)

```
Trigger: Schedule (ogni 15 min) o Push
  ↓
GitHub Actions VM avvia
  ↓
Python 3.11 setup
  ↓
Install dependencies (collector/requirements.txt)
  ↓
Run collector/collect_data.py
  ├─ Fetch Yahoo Finance per 10 titoli
  ├─ Update *_historical.csv (data/)
  ├─ Update predictions_history.csv
  └─ Log in logs/collection.log
  ↓
Git commit automatico
  ↓
Git push su repository
  ↓
Dati disponibili nel cloud ✅
```

### 2. Utilizzo Locale (On Demand)

```
User: Avvia dashboard
  ↓
Streamlit app.py parte
  ↓
Sync automatico da GitHub (sync_data.py)
  ├─ git pull origin main
  └─ Scarica ultimi dati
  ↓
Caricamento dati CSV
  ↓
Calcolo indicatori tecnici
  ↓
Training modelli ML
  ↓
Generazione previsioni
  ↓
Rendering dashboard ✅
  ↓
User: Analizza e decide
  ↓
User: Chiude dashboard (Ctrl+C)
  ↓
GitHub Actions continua a raccogliere dati in background
```

---

## 🐛 Problemi Comuni e Soluzioni

### 1. ModuleNotFoundError

**Causa**: Dipendenze mancanti

**Soluzione**:
```bash
cd "D:\Programmi2\TRADING Ibrido"
"D:\Programmi2\Pyton\python.exe" -m pip install -r requirements.txt --upgrade
```

### 2. Config Import Error

**Causa**: Mancano `__init__.py` nei package

**Soluzione**: Verificare esistenza di:
- `config/__init__.py`
- `utils/__init__.py`
- `models/__init__.py`

### 3. Git Sync Fallisce

**Causa**: Conflitti o permessi

**Soluzione**:
```bash
cd "D:\Programmi2\TRADING Ibrido"
git stash                    # Salva modifiche locali
git pull                     # Aggiorna da remote
git stash pop               # Riapplica modifiche
```

### 4. GitHub Actions Fallisce

**Causa**: Permessi write mancanti

**Soluzione**:
1. GitHub → Repository Settings
2. Actions → General
3. Workflow permissions: "Read and write"
4. Save

### 5. Dashboard Non Aggiorna Dati

**Causa**: Sync non eseguita

**Soluzione**:
```bash
git pull
# Poi riavvia dashboard
```

---

## 📈 Metriche e Performance

### Utilizzo GitHub Actions

```
Raccolte/giorno: 36 (ogni 15 min × 9 ore mercato)
Raccolte/mese: ~792 (22 giorni lavorativi)
Durata media: 45-60 secondi per raccolta
Utilizzo mensile: 600-800 minuti
Quota gratuita: 2000 minuti/mese
Margine: 60-70% disponibile ✅
```

### Storage Dati

```
Iniziale: 5-10 MB (10 titoli × 506 giorni)
Crescita: 1-2 MB/mese
Dopo 1 anno: 15-30 MB
Quota GitHub: 100 GB repository
Utilizzo: < 0.1% ✅
```

### Accuratezza Previsioni (Stimata)

```
2 ore:   ~95% (alta precisione)
1 giorno: ~85-90%
3 giorni: ~80-85%
7 giorni: ~75-80%
```

*Migliora con accumulo dati storici*

---

## 🛠️ Possibili Sviluppi Futuri

### Feature da Implementare

#### Alta Priorità
1. **Notifiche Email/Telegram**
   - Alert prezzi target
   - Notifiche RSI ipercomprato/venduto
   - Crossover Moving Averages

2. **Espansione Titoli**
   - USA (S&P 500)
   - Europa (DAX, CAC40)
   - Supporto simboli multipli mercati

3. **Miglioramenti UI**
   - Dark mode
   - Mobile responsive
   - Export PDF report

#### Media Priorità
4. **Portfolio Tracking**
   - Tracciamento portafoglio personale
   - P&L calculator
   - Suggerimenti diversificazione

5. **Sentiment Analysis Avanzato**
   - News scraping automatico
   - NLP sentiment da news
   - Integrazione sentiment in previsioni

6. **Backtesting**
   - Test strategie su dati storici
   - Simulazione trading
   - Performance metrics

#### Bassa Priorità (Advanced)
7. **Trading Automatico**
   - Integrazione broker API
   - Paper trading
   - Risk management automatico

8. **Criptovalute**
   - Bitcoin, Ethereum, etc.
   - Exchange integration
   - 24/7 tracking

### Miglioramenti Tecnici

- [ ] Unit tests (pytest)
- [ ] CI/CD pipeline
- [ ] Database (PostgreSQL/SQLite) invece CSV
- [ ] API REST per dati
- [ ] Docker containerization
- [ ] Multi-language support
- [ ] Caching avanzato (Redis)

---

## 📝 Note Tecniche Importanti

### Architettura

**Pattern**: Hybrid Cloud-Local
- **Cloud**: Stateless data collection (GitHub Actions)
- **Local**: Stateful analysis & visualization (Streamlit)
- **Sync**: Git-based (bi-directional possibile)

### Vantaggi Architettura Scelta

✅ Zero costi operativi (GitHub Free Tier)
✅ Scalabile (GitHub infra robusta)
✅ Disaster recovery (Git history)
✅ Multi-device access (git clone)
✅ Low latency analisi (locale)
✅ Privacy (repository privato)

### Limitazioni Attuali

⚠️ Solo orari mercato (7-17 UTC, Lun-Ven)
⚠️ Yahoo Finance rate limits (1 req/sec)
⚠️ Nessuna autenticazione dashboard (localhost only)
⚠️ Single user (no multi-tenancy)
⚠️ Finnhub API opzionale (non attiva)

### File Importanti da NON Modificare

❌ `.git/` - Directory Git
❌ `data/*.csv` - Gestiti da GitHub Actions
❌ `.github/workflows/data_collection.yml` - Workflow critico
❌ `config/__init__.py`, `utils/__init__.py`, `models/__init__.py` - Import package

### File Modificabili Liberamente

✅ `dashboard/app.py` - UI e logica dashboard
✅ `models/predictor.py` - Algoritmi ML
✅ `utils/*.py` - Utilità
✅ `config/config.py` - Configurazioni
✅ `README.md`, documentazione varia
✅ `requirements.txt` - Dipendenze
✅ `sync_data.py` - Logica sync

---

## 🔐 Sicurezza

### Dati Sensibili

**Non committare**:
- Token GitHub (già in git config locale)
- API keys (se aggiunte)
- Password
- Dati personali

**File `.gitignore` include**:
```
.env
*.key
secrets.toml
credentials.json
```

### Repository Privato

✅ Repository è **privato**
✅ Solo owner (valeriofaggi) ha accesso
✅ GitHub Actions ha permessi limitati al repository

---

## 📞 Riferimenti Esterni

### Documentazione

- **Yahoo Finance**: https://pypi.org/project/yfinance/
- **Prophet**: https://facebook.github.io/prophet/
- **Streamlit**: https://docs.streamlit.io/
- **GitHub Actions**: https://docs.github.com/actions
- **Plotly**: https://plotly.com/python/

### Repository Simili (Ispirazione)

- Stock prediction with ML
- Financial dashboard projects
- Automated trading systems

---

## ✅ Checklist Stato Sistema

### Infrastruttura
- [x] Repository GitHub creato e configurato
- [x] GitHub Actions attivo e funzionante
- [x] Permessi write configurati
- [x] Workflow schedule configurato (ogni 15 min)
- [x] Git configurato localmente

### Codice
- [x] Collector script funzionante
- [x] Dashboard Streamlit completa (8 tab)
- [x] Sync automatico implementato
- [x] Modelli ML implementati
- [x] Indicatori tecnici implementati
- [x] UI scrolling tab risolto
- [x] Package `__init__.py` creati

### Dati
- [x] 10 titoli configurati
- [x] Dati storici raccolti (506 giorni)
- [x] Predictions history inizializzata
- [x] Logs collection attivi

### Documentazione
- [x] README.md completo
- [x] QUICK_START.md per ripartenza
- [x] PRESENTAZIONE_APP.md overview
- [x] GITHUB_SETUP_GUIDE.md setup
- [x] SESSION_SUMMARY.md tecnico
- [x] CONTEXT_FOR_CLAUDE.md (questo file)

### Testing
- [x] Dashboard avvia correttamente
- [x] Sync funziona
- [x] GitHub Actions raccoglie dati
- [x] Commit automatici funzionano
- [x] Dati visualizzati correttamente

---

## 🎯 Obiettivi Completati

✅ Sistema ibrido cloud-locale operativo
✅ Zero costi operativi
✅ Raccolta dati automatica 24/7
✅ Dashboard professionale e interattiva
✅ Machine Learning integrato
✅ Documentazione completa
✅ Git workflow automatizzato
✅ 10 titoli azionari tracciati
✅ Previsioni multi-orizzonte
✅ Grafici accuratezza

---

## 💡 Suggerimenti per Claude (Prossima Sessione)

### Se l'utente chiede:

**"Continua lo sviluppo"**
→ Chiedi quale feature implementare (vedi sezione "Possibili Sviluppi Futuri")

**"La dashboard non funziona"**
→ Chiedi errore specifico, poi segui sezione "Problemi Comuni"

**"Aggiungi un titolo"**
→ Modifica `config/config.py` lista `TOP_ITALIAN_STOCKS`

**"Cambia frequenza raccolta"**
→ Modifica `.github/workflows/data_collection.yml` cron expression

**"Migliora le previsioni"**
→ Modifica `models/predictor.py` hyperparameters o algoritmi

**"Nuova visualizzazione"**
→ Aggiungi tab in `dashboard/app.py` metodo `run()`

### Best Practices

1. **Leggi sempre** questo file all'inizio sessione
2. **Verifica git status** prima di modifiche
3. **Testa localmente** prima di commit
4. **Commit frequenti** con messaggi chiari
5. **Documenta** modifiche sostanziali
6. **Backup** dati importanti prima modifiche drastiche

---

## 📄 File di Log da Controllare

```bash
# Log raccolte GitHub Actions
cat "D:\Programmi2\TRADING Ibrido\logs\collection.log"

# Git log
git log --oneline -10

# Python errors (se crash)
# Visibili nel terminale dove gira Streamlit
```

---

## 🔗 Link Rapidi

- **Repository**: https://github.com/valeriofaggi/TradingClaude
- **Actions**: https://github.com/valeriofaggi/TradingClaude/actions
- **Dashboard**: http://localhost:8501 (quando attiva)

---

## 📅 Storia Versioni

### v2.0 (2025-11-11) - Sistema Ibrido ✅
- Architettura cloud-locale implementata
- GitHub Actions per raccolta dati
- Dashboard Streamlit completa
- Sync automatico
- 10 titoli italiani
- ML Prophet + Random Forest
- Documentazione completa

### v1.0 (Precedente) - Versione Beta
- Sistema completamente locale
- PC sempre acceso
- Raccolta dati manuale
- Dashboard base

---

**Ultimo aggiornamento**: 2025-11-11
**Versione Context File**: 1.0
**Stato Progetto**: ✅ Produzione - Pienamente Operativo

---

## 🚀 Per Claude: Prompt Suggerito per Ripartire

```
Ciao Claude! Ho un progetto Python chiamato "Trading Predictor"
che voglio continuare a sviluppare.

Leggi questo file per avere il contesto completo:
D:\Programmi2\TRADING Ibrido\CONTEXT_FOR_CLAUDE.md

Dopo averlo letto, fammi sapere che hai capito il progetto e
chiedimi cosa voglio fare oggi.
```

---

**Fine del Context File** ✅
