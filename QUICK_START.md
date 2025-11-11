# 🚀 Quick Start - Trading Predictor

Guida rapida per avviare e utilizzare il sistema Trading Predictor.

---

## ⚡ Avvio Rapido Dashboard

### Comando per Avviare la Dashboard

```bash
cd "D:\Programmi2\TRADING Ibrido"
"D:\Programmi2\Pyton\python.exe" -m streamlit run dashboard/app.py
```

**La dashboard si aprirà automaticamente nel browser su:** http://localhost:8501

---

## 🔄 Sincronizzazione Dati

### Sincronizzazione Automatica

All'avvio della dashboard, i dati vengono **sincronizzati automaticamente** da GitHub.

### Sincronizzazione Manuale (Opzionale)

Se vuoi sincronizzare i dati prima di avviare la dashboard:

```bash
cd "D:\Programmi2\TRADING Ibrido"
git pull
```

Oppure usa lo script di sync:

```bash
"D:\Programmi2\Pyton\python.exe" sync_data.py
```

---

## 📊 Verifica Raccolta Dati GitHub

### Controlla Status GitHub Actions

1. Vai su: https://github.com/valeriofaggi/TradingClaude/actions
2. Verifica che il workflow "Stock Data Collection" sia in esecuzione
3. Controlla gli ultimi run (dovrebbero essere verdi ✅)

### Frequenza Raccolta

- **Automatica**: Ogni 15 minuti (7:00-17:00 UTC, Lun-Ven)
- **Manuale**: Puoi lanciare il workflow manualmente dal tab Actions

---

## 🛠️ Risoluzione Problemi Comuni

### Dashboard Non Si Avvia

**Problema**: ModuleNotFoundError

**Soluzione**:
```bash
cd "D:\Programmi2\TRADING Ibrido"
"D:\Programmi2\Pyton\python.exe" -m pip install -r requirements.txt --upgrade
```

---

### Dati Non Aggiornati

**Problema**: Dati vecchi nella dashboard

**Soluzione**:
```bash
cd "D:\Programmi2\TRADING Ibrido"
git pull
```

Poi riavvia la dashboard.

---

### GitHub Actions Non Funziona

**Verifica**:
1. Repository: https://github.com/valeriofaggi/TradingClaude
2. Tab "Actions"
3. Verifica permessi: Settings → Actions → General → Workflow permissions = "Read and write"

---

## 📁 Struttura File Importanti

```
D:\Programmi2\TRADING Ibrido\
├── dashboard/app.py          # Dashboard principale
├── sync_data.py              # Script sincronizzazione
├── collector/collect_data.py # Script raccolta dati (GitHub)
├── data/                     # Dati raccolti (sync da GitHub)
│   ├── *_historical.csv
│   └── predictions_history.csv
└── requirements.txt          # Dipendenze Python
```

---

## 🔗 Link Utili

- **Repository GitHub**: https://github.com/valeriofaggi/TradingClaude
- **GitHub Actions**: https://github.com/valeriofaggi/TradingClaude/actions
- **Dashboard Locale**: http://localhost:8501
- **Documentazione Completa**: [README.md](./README.md)

---

## 💡 Comandi Essenziali

### Avviare Dashboard
```bash
cd "D:\Programmi2\TRADING Ibrido"
"D:\Programmi2\Pyton\python.exe" -m streamlit run dashboard/app.py
```

### Fermare Dashboard
- Nel terminale: `Ctrl+C`
- Conferma: `y` + Invio

### Sync Dati
```bash
cd "D:\Programmi2\TRADING Ibrido"
git pull
```

### Vedere Log Raccolte
```bash
cd "D:\Programmi2\TRADING Ibrido"
cat logs/collection.log
```

### Verificare Versione Python
```bash
"D:\Programmi2\Pyton\python.exe" --version
```

---

## 📞 Supporto

Se incontri problemi:
1. Consulta [README.md](./README.md) - Sezione Troubleshooting
2. Controlla [SESSION_SUMMARY.md](./SESSION_SUMMARY.md) - Documentazione tecnica
3. Verifica [GITHUB_SETUP_GUIDE.md](./GITHUB_SETUP_GUIDE.md) - Setup GitHub

---

**Ultimo aggiornamento**: 2025-11-11
**Versione**: 2.0 - Sistema Ibrido
