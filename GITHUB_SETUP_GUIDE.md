# Guida Setup GitHub Actions - Trading Predictor

## Sistema Ibrido: Raccolta Dati Cloud + Analisi Locale

Questa guida ti aiuta a configurare un sistema dove:
- **GitHub Actions** (cloud, gratis) raccoglie dati automaticamente ogni 15 minuti
- **PC Locale** scarica i dati e fa analisi/previsioni quando serve

---

## 📋 PARTE 1: Creare Account GitHub (5 minuti)

### Step 1: Registrazione
1. Vai su https://github.com/signup
2. Inserisci email, password, username
3. Verifica email
4. Scegli piano **FREE** (gratuito)

### Step 2: Installare Git sul PC
**Windows:**
1. Scarica da: https://git-scm.com/download/win
2. Installa con opzioni predefinite
3. Apri "Git Bash" dal menu Start

**Verifica installazione:**
```bash
git --version
# Dovrebbe mostrare: git version 2.x.x
```

---

## 📦 PARTE 2: Creare Repository Privato

### Step 1: Nuovo Repository
1. Vai su https://github.com/new
2. **Repository name**: `trading-predictor-data`
3. **Description**: `Automated stock data collection`
4. ✅ Seleziona **Private** (importante!)
5. ✅ Seleziona "Add a README file"
6. Click **Create repository**

### Step 2: Clona Repository sul PC
```bash
# Apri Git Bash
cd D:/Programmi2/

# Clona il repository (sostituisci TUO-USERNAME)
git clone https://github.com/TUO-USERNAME/trading-predictor-data.git

# Entra nella cartella
cd trading-predictor-data
```

---

## 🔧 PARTE 3: Configurare Struttura Repository

### Step 1: Crea Cartelle
```bash
# Sei in D:/Programmi2/trading-predictor-data

mkdir -p .github/workflows
mkdir -p collector
mkdir -p data
mkdir -p logs
```

### Step 2: Copia File dal Progetto Esistente
Dopo che ho creato i file, li copierai così:

```bash
# Copia script collector
cp "../TRADING By Claude COde/collector/"* ./collector/

# Copia workflow GitHub Actions
cp "../TRADING By Claude COde/.github/workflows/"* ./.github/workflows/

# Copia lista titoli personalizzata (se esiste)
cp "../TRADING By Claude COde/data/custom_stocks.json" ./data/ 2>/dev/null || echo "File non trovato, verrà creato automaticamente"
```

---

## 🔐 PARTE 4: Configurare Secrets (API Keys)

### Step 1: Vai nelle Impostazioni Repository
1. Vai su https://github.com/TUO-USERNAME/trading-predictor-data
2. Click tab **Settings**
3. Nel menu sinistro, click **Secrets and variables** → **Actions**
4. Click **New repository secret**

### Step 2: Aggiungi Finnhub API Key (opzionale)
**Name**: `FINNHUB_API_KEY`
**Value**: La tua API key da Finnhub (o lascia vuoto se usi solo Yahoo Finance)

Click **Add secret**

---

## ⚙️ PARTE 5: Attivare GitHub Actions

### Step 1: Push dei File
```bash
# Sei in D:/Programmi2/trading-predictor-data

# Aggiungi tutti i file
git add .

# Commit
git commit -m "Initial setup: data collector and GitHub Actions workflow"

# Push al repository remoto
git push origin main
```

### Step 2: Verifica Attivazione
1. Vai su https://github.com/TUO-USERNAME/trading-predictor-data
2. Click tab **Actions**
3. Dovresti vedere "Data Collection Workflow"
4. Se non parte automaticamente, click **Run workflow** manualmente

### Step 3: Prima Esecuzione di Test
- Click sul workflow in esecuzione per vedere i log
- Verifica che completi con successo (✅ verde)
- Controlla che vengano creati file in `data/`

---

## 🖥️ PARTE 6: Configurare PC Locale

### Step 1: Configura Git User
```bash
git config --global user.name "Tuo Nome"
git config --global user.email "tua@email.com"
```

### Step 2: Crea Collegamento Simbolico ai Dati
Questo permette alla tua app locale di leggere i dati dal repository:

**Windows (Prompt dei Comandi come Amministratore):**
```cmd
mklink /D "D:\Programmi2\TRADING By Claude COde\data_cloud" "D:\Programmi2\trading-predictor-data\data"
```

Ora la cartella `D:\Programmi2\TRADING By Claude COde\data_cloud` punta ai dati di GitHub!

### Step 3: Script Automatico per Sincronizzazione
Ho creato uno script `sync_data.py` nella tua app che:
- Fa git pull automaticamente all'avvio della dashboard
- Scarica ultimi dati
- Parte trasparentemente

---

## 🚀 PARTE 7: Usare il Sistema

### Workflow Completo

**1. GitHub Actions lavora 24/7 (automatico):**
- Ogni 15 minuti (solo orari di mercato)
- Raccoglie dati Yahoo Finance
- Aggiorna file CSV nel repository
- Commit automatico

**2. Quando vuoi vedere dashboard:**
```bash
cd "D:\Programmi2\TRADING By Claude COde"
streamlit run dashboard/app.py
```

L'app:
- Fa automaticamente `git pull` dei nuovi dati
- Carica dati aggiornati
- Mostra dashboard con info fresche!

**3. Spegni PC quando non serve:**
- GitHub Actions continua a raccogliere dati
- Alla prossima apertura, scarichi tutto lo storico

---

## 🔍 PARTE 8: Monitoraggio

### Controllare GitHub Actions
1. Vai su https://github.com/TUO-USERNAME/trading-predictor-data/actions
2. Vedi lista esecuzioni:
   - ✅ Verde = Successo
   - ❌ Rosso = Errore
3. Click su esecuzione per vedere log dettagliati

### Verificare Dati Raccolti
1. Vai su https://github.com/TUO-USERNAME/trading-predictor-data/tree/main/data
2. Dovresti vedere:
   - `predictions_history.csv`
   - `ENI_MI_historical.csv`
   - Altri file CSV per ogni titolo

### Log di Raccolta
- File `logs/collection.log` contiene log dettagliati
- Aggiornato ad ogni esecuzione

---

## 🐛 PARTE 9: Troubleshooting

### GitHub Actions non parte
**Problema**: Workflow non si avvia
**Soluzione**:
1. Vai su Settings → Actions → General
2. Verifica che "Allow all actions" sia selezionato
3. Salva

### Errore "Authentication failed"
**Problema**: Non riesce a fare git push/pull
**Soluzione**:
```bash
# Usa GitHub Personal Access Token
# Vai su https://github.com/settings/tokens
# Genera nuovo token con scope "repo"
# Usa token come password quando richiesto
```

### File non si sincronizzano
**Problema**: Dati non aggiornati sul PC
**Soluzione**:
```bash
cd "D:\Programmi2\trading-predictor-data"
git pull origin main --force
```

### GitHub Actions supera limite minuti
**Problema**: Messaggio "Quota exceeded"
**Soluzione**:
- Riduci frequenza raccolta (es. ogni 30 min invece di 15)
- Raccogli solo durante orari di mercato (già configurato)
- 2000 min/mese dovrebbero bastare ampiamente

---

## 📊 PARTE 10: Statistiche e Limiti

### Uso Previsto GitHub Actions
```
Raccolta ogni 15 minuti, 9:00-18:00, Lun-Ven:
- 36 raccolte/giorno × 22 giorni lavorativi = 792 raccolte/mese
- 30 secondi per raccolta = 396 minuti/mese
- Limite free: 2000 minuti/mese
- Margine: 1600+ minuti (80% disponibile)
```

### Spazio Repository
- File CSV: ~10-50MB totali
- Limite GitHub: 100GB repository
- **Nessun problema di spazio**

---

## ✅ Checklist Finale

Dopo aver completato tutti i passaggi:

- [ ] Account GitHub creato
- [ ] Git installato sul PC
- [ ] Repository privato creato
- [ ] File collector e workflow copiati
- [ ] Finnhub API key configurata (opzionale)
- [ ] GitHub Actions attivato e funzionante
- [ ] Collegamento simbolico creato
- [ ] Prima sincronizzazione completata
- [ ] Dashboard avviata e funzionante
- [ ] Dati visibili e aggiornati

---

## 🎉 Fine Setup!

Ora hai un sistema completamente automatico:
- **0€ di costo**
- Raccolta dati 24/7
- PC acceso solo quando serve
- Backup automatico su GitHub
- Accessibile da qualsiasi PC

Per domande o problemi, controlla i log in:
- GitHub Actions: https://github.com/TUO-USERNAME/trading-predictor-data/actions
- Log locali: `D:\Programmi2\trading-predictor-data\logs\collection.log`
