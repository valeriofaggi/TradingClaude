# Trading Predictor - Versione Ibrida

Sistema di predizione prezzi azionari con architettura cloud-locale ibrida.

## 📊 Cos'è questo progetto?

Trading Predictor è un sistema di analisi e previsione dei prezzi azionari che combina:
- **Machine Learning** (Prophet + Random Forest) per previsioni a breve e medio termine
- **Analisi tecnica** con indicatori avanzati
- **Dashboard interattiva** Streamlit per visualizzazione
- **Storico previsioni** per valutare l'accuratezza del modello

## 🏗️ Architettura Ibrida

Questa versione utilizza un'**architettura ibrida cloud-locale** per ottimizzare costi ed efficienza:

```
┌──────────────────────────────────┐
│   GITHUB ACTIONS (Cloud 24/7)   │
│                                  │
│  ✓ Raccolta dati automatica      │
│  ✓ Esecuzione ogni 15 minuti     │
│  ✓ Storage dati storici          │
│  ✓ Backup automatico             │
│  ✓ 0€ di costo                   │
└────────────┬─────────────────────┘
             │
             │ Git Sync
             ▼
┌──────────────────────────────────┐
│   PC LOCALE (On Demand)          │
│                                  │
│  ✓ Dashboard Streamlit           │
│  ✓ Analisi ML avanzate           │
│  ✓ Visualizzazioni interattive   │
│  ✓ Acceso solo quando serve      │
└──────────────────────────────────┘
```

### Vantaggi vs Versione Beta

| Aspetto | Beta (Locale) | Ibrido (Cloud+Locale) |
|---------|---------------|------------------------|
| **Costo** | PC sempre acceso | 0€ - GitHub Actions gratuito |
| **Consumo energia** | ~10-15 kWh/mese | ~1 kWh/mese |
| **Dati sempre aggiornati** | Solo se PC acceso | ✅ Sempre (cloud) |
| **Backup** | Manuale | ✅ Automatico (git) |
| **Portabilità** | Un solo PC | ✅ Qualsiasi PC (git clone) |
| **Manutenzione** | Alta | Bassa |

## 🚀 Come Funziona

### 1. Raccolta Dati (GitHub Actions)
- **Frequenza**: Ogni 15 minuti durante orari mercato (7:00-17:00 UTC)
- **Fonte**: Yahoo Finance (gratuito, no API key)
- **Dati raccolti**:
  - Quote correnti (prezzi, volumi, variazioni)
  - Dati storici (ultimi 2 anni)
- **Output**: File CSV in cartella `data/`
- **Commit automatico**: Ogni raccolta crea un commit con i nuovi dati

### 2. Sincronizzazione Dati (PC Locale)
- **Quando**: All'avvio della dashboard
- **Come**: `git pull` automatico
- **Cosa**: Scarica ultimi dati raccolti dal cloud
- **Durata**: ~2-5 secondi

### 3. Analisi e Dashboard (PC Locale)
- **Machine Learning**: Genera previsioni con Prophet + Random Forest
- **Analisi Tecnica**: Calcola indicatori (SMA, RSI, MACD, etc.)
- **Visualizzazione**: Dashboard Streamlit interattiva
- **Orizzonti temporali**: 2h, 1d, 3d, 7d

## 📋 Prerequisiti

### Software Necessario

1. **Python 3.10+**
   - Download: https://www.python.org/downloads/

2. **Git**
   - Download: https://git-scm.com/download/win
   - Versione raccomandata: 2.40+

3. **Account GitHub** (gratuito)
   - Registrazione: https://github.com/signup

### Conoscenze Richieste
- ✅ Nessuna! Segui la guida passo-passo

## 🔧 Setup Iniziale

### Parte 1: Configurazione GitHub (Una sola volta)

Segui la guida dettagliata: [GITHUB_SETUP_GUIDE.md](./GITHUB_SETUP_GUIDE.md)

**Riassunto rapido:**
1. Crea account GitHub
2. Crea repository privato
3. Carica file del progetto
4. Attiva GitHub Actions
5. Verifica raccolta dati automatica

**Tempo stimato**: 15-20 minuti

### Parte 2: Setup PC Locale (Una sola volta)

1. **Clona il repository GitHub**
   ```bash
   cd D:\Programmi2
   git clone https://github.com/tuo-username/trading-predictor-data.git "TRADING Ibrido"
   cd "TRADING Ibrido"
   ```

2. **Installa dipendenze Python**
   ```bash
   "D:\Programmi2\Pyton\python.exe" -m pip install -r requirements.txt
   ```

3. **Verifica installazione**
   ```bash
   "D:\Programmi2\Pyton\python.exe" sync_data.py
   ```
   Dovresti vedere: `✓ Data synchronized successfully!`

## 📱 Utilizzo Quotidiano

### Avviare la Dashboard

```bash
cd "D:\Programmi2\TRADING Ibrido"
"D:\Programmi2\Pyton\python.exe" -m streamlit run dashboard/app.py
```

**Cosa succede all'avvio:**
1. ✅ Sincronizzazione automatica dati da GitHub (~5 secondi)
2. ✅ Caricamento dati storici
3. ✅ Generazione previsioni ML
4. ✅ Dashboard pronta all'uso

**La dashboard si apre in automatico nel browser**: http://localhost:8501

### Funzionalità Dashboard

#### 📊 Tab Disponibili

1. **🌐 Panoramica Completa**
   - Vista tutti i titoli
   - Prezzi e variazioni correnti
   - Previsioni 24h per tutti i titoli

2. **📈 Titolo Selezionato**
   - Analisi dettagliata titolo corrente
   - Grafici interattivi
   - Indicatori tecnici

3. **⏱️ 2 Ore / 📅 1-3-7 Giorni**
   - Previsioni per diversi orizzonti temporali
   - Confronto con dati reali
   - Metriche di confidenza

4. **🎯 Accuratezza Modello**
   - Storico previsioni vs prezzi reali
   - Metriche di errore (MAE, RMSE, MAPE)
   - Grafici prestazioni

5. **📊 Grafici Accuratezza**
   - Visualizzazioni avanzate accuratezza
   - Filtri per orizzonte temporale
   - Trend errori nel tempo

#### ⚙️ Sidebar

- **Selezione titolo**: Scegli quale azione analizzare
- **Gestione titoli**: Aggiungi/rimuovi titoli dalla watchlist
- **Auto-refresh**: Aggiornamento automatico dati
- **Intervallo refresh**: Configura frequenza aggiornamento

### Spegnere la Dashboard

1. Nel terminale: `Ctrl+C`
2. Conferma: `y` + Invio
3. Puoi spegnere il PC - i dati continuano ad aggiornarsi su GitHub!

## 🔄 Workflow Completo

```
┌─────────────────────────────────────────┐
│  GitHub Actions (sempre attivo)         │
│  ✓ Raccoglie dati ogni 15 min          │
│  ✓ Commit automatici                    │
│  ✓ Storage cloud                        │
└────────────────┬────────────────────────┘
                 │
                 │ Quando vuoi vedere i dati...
                 ▼
┌─────────────────────────────────────────┐
│  Tu:                                    │
│  1. Accendi PC                          │
│  2. Avvia dashboard                     │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  Dashboard (automatico):                │
│  1. Git pull (sync dati)               │
│  2. Carica ultimi dati                 │
│  3. Genera previsioni                  │
│  4. Mostra dashboard                    │
└────────────────┬────────────────────────┘
                 │
                 │ Quando hai finito...
                 ▼
┌─────────────────────────────────────────┐
│  Tu:                                    │
│  1. Chiudi dashboard (Ctrl+C)          │
│  2. Spegni PC                          │
│                                         │
│  GitHub Actions continua a lavorare! ✓  │
└─────────────────────────────────────────┘
```

## 📂 Struttura Progetto

```
TRADING Ibrido/
├── collector/                  # Script raccolta dati per GitHub Actions
│   ├── collect_data.py        # Script principale raccolta
│   └── requirements.txt       # Dipendenze minimali (cloud)
│
├── .github/workflows/         # Configurazione GitHub Actions
│   └── data_collection.yml    # Workflow automatizzazione
│
├── dashboard/                 # Dashboard Streamlit
│   └── app.py                 # Applicazione principale
│
├── models/                    # Modelli ML
│   └── predictor.py           # Logica predizione
│
├── utils/                     # Utilità condivise
│   ├── data_collector.py      # Collezione dati (locale)
│   ├── technical_indicators.py
│   ├── sentiment_analyzer.py
│   └── prediction_logger.py
│
├── config/                    # Configurazione
│   └── config.py              # Settings globali
│
├── data/                      # Dati (generati, in .gitignore parziale)
│   ├── *_historical.csv       # Dati storici per titolo
│   ├── predictions_history.csv # Storico previsioni
│   └── custom_stocks.json     # Lista titoli personalizzata
│
├── logs/                      # Log (generati)
│   └── collection.log         # Log raccolte dati
│
├── sync_data.py              # Script sincronizzazione Git
├── requirements.txt          # Dipendenze complete (locale)
├── README.md                 # Questo file
├── GITHUB_SETUP_GUIDE.md     # Guida setup GitHub
└── SESSION_SUMMARY.md        # Riepilogo sviluppo
```

## 🐛 Troubleshooting

### Dashboard non si avvia

**Errore**: `ModuleNotFoundError`
```bash
# Soluzione: Reinstalla dipendenze
"D:\Programmi2\Pyton\python.exe" -m pip install -r requirements.txt --upgrade
```

**Errore**: `git pull failed`
```bash
# Soluzione: Verifica configurazione Git
cd "D:\Programmi2\TRADING Ibrido"
git remote -v  # Deve mostrare il tuo repository GitHub
git status     # Controlla stato repository
```

### Sincronizzazione non funziona

1. **Verifica connessione Internet**
2. **Controlla repository GitHub**:
   ```bash
   git remote -v
   ```
3. **Test manuale sync**:
   ```bash
   "D:\Programmi2\Pyton\python.exe" sync_data.py
   ```

### GitHub Actions non funziona

1. Vai su GitHub.com → tuo repository
2. Tab "Actions"
3. Verifica:
   - ✅ Actions attivato (pulsante verde "I understand my workflows...")
   - ✅ Workflow "Stock Data Collection" presente
   - ✅ Nessun errore nei log

4. Test manuale:
   - Tab "Actions"
   - Workflow "Stock Data Collection"
   - Pulsante "Run workflow"

### Dati non aggiornati

```bash
# Forza sync manuale
cd "D:\Programmi2\TRADING Ibrido"
git pull

# Riavvia dashboard
"D:\Programmi2\Pyton\python.exe" -m streamlit run dashboard/app.py
```

## 📊 Monitoraggio

### Verifica Raccolta Dati GitHub

1. Vai su: `https://github.com/tuo-username/tuo-repo/actions`
2. Controlla workflow "Stock Data Collection"
3. Ogni esecuzione mostra:
   - Timestamp
   - Durata
   - File aggiornati
   - Eventuali errori

### Verifica Dati Locali

```bash
# Controlla file dati
ls "D:\Programmi2\TRADING Ibrido\data"

# Controlla log raccolte
cat "D:\Programmi2\TRADING Ibrido\logs\collection.log"

# Ultimo commit (ultimo aggiornamento)
git log -1
```

## 💰 Costi e Limiti

### GitHub Actions (Gratuito)
- **Limite mensile**: 2000 minuti/mese
- **Utilizzo stimato**: 400-800 minuti/mese (~20-40%)
- **Storage**: 500MB (sufficiente per anni di dati)
- **Repository**: 100GB (usato: ~10MB)

### Calcolo Utilizzo
```
Raccolta ogni 15 min, 9:00-18:00, Lun-Ven:
- 36 raccolte/giorno × 22 giorni = 792 raccolte/mese
- 60 secondi/raccolta = 792 minuti/mese
- Margine sicurezza: 1208 minuti (60% disponibile)
```

## 🔐 Sicurezza

- ✅ Repository **privato** (raccomandato)
- ✅ Nessuna API key necessaria (usa Yahoo Finance gratuito)
- ✅ Dati personali non condivisi
- ✅ Commit firmati da GitHub Actions Bot

## 🆚 Confronto Versioni

### Quando usare Beta (Locale)
- ✅ Hai PC sempre acceso
- ✅ Consumi energetici non preoccupano
- ✅ Non vuoi configurare GitHub
- ✅ Vuoi massima semplicità

### Quando usare Ibrido (Questo)
- ✅ Vuoi risparmiare energia
- ✅ PC spento spesso
- ✅ Vuoi dati sempre aggiornati
- ✅ Vuoi backup automatico
- ✅ Vuoi accesso da più PC

## 📚 Risorse

- **Guida Setup GitHub**: [GITHUB_SETUP_GUIDE.md](./GITHUB_SETUP_GUIDE.md)
- **Riepilogo Sviluppo**: [SESSION_SUMMARY.md](./SESSION_SUMMARY.md)
- **Yahoo Finance API**: https://pypi.org/project/yfinance/
- **GitHub Actions Docs**: https://docs.github.com/actions
- **Streamlit Docs**: https://docs.streamlit.io

## 🤝 Supporto

Per problemi o domande:
1. Consulta sezione [Troubleshooting](#-troubleshooting)
2. Verifica [GITHUB_SETUP_GUIDE.md](./GITHUB_SETUP_GUIDE.md)
3. Controlla log: `logs/collection.log`

## 📄 Licenza

Progetto personale - Uso educativo e di ricerca.

---

**Versione**: 2.0 - Architettura Ibrida
**Ultimo aggiornamento**: 2025-11-11
**Stato**: ✅ Produzione
