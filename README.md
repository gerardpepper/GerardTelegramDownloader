# Gerard Telegram Downloader

App desktop per Windows 10/11 che scarica in blocco media e documenti da canali, gruppi e chat di Telegram.

## Primo avvio: come ottenere le chiavi API

Le chiavi si creano **una volta sola** e sono legate al tuo account Telegram.

1. Apri <https://my.telegram.org/apps> nel browser.
2. Inserisci il tuo numero con prefisso (es. `+393331234567`) e premi *Next*.
3. Telegram ti manda un codice **dentro l'app Telegram** (chat "Telegram", non per SMS): copialo nel sito.
4. Compila il modulo *Create new application*:
   - **App title**: `Gerard Downloader` (a piacere)
   - **Short name**: `gerarddl` (a piacere, solo lettere/numeri, 5–32 caratteri)
   - **Platform**: *Desktop*
   - il resto può restare vuoto.
5. Premi *Create application*: compaiono **App api_id** (un numero) e **App api_hash** (32 caratteri).
6. Avvia l'app, incolla i due valori e premi **Salva e continua**.
7. Inserisci il numero di telefono → **Invia codice** → scrivi il codice ricevuto in Telegram → **Accedi**.
   Se hai la verifica in due passaggi ti verrà chiesta anche la password.

Dal secondo avvio in poi l'accesso è automatico.
Chiavi e sessione sono salvate in `%APPDATA%\GerardTelegramDownloader`, cifrate con il tuo utente Windows (DPAPI):
non funzionano se copiate su un altro PC o un altro utente. **Non condividere mai api_hash né la cartella dati.**

## Uso

1. Scegli la chat da **Chat recenti** oppure incolla un link `https://t.me/...` / `@username`
   (per i link d'invito privati devi essere già membro).
2. Scegli la **cartella di destinazione** (anche di rete).
3. Facoltativo: filtri per tipo (preset o estensioni personalizzate) e per dimensione.
4. Opzioni: gestione dei file già esistenti, sottocartelle automatiche (sorgente / tipo / data),
   download paralleli (1–4), notifiche, spegnimento a fine coda.
5. **Avvia download**. Puoi mettere in **Pausa** o **Annullare** in qualsiasi momento.

### Ripresa dei download
I file in corso vengono scritti come `nome.ext.part` e l'avanzamento è salvato in `state.db` (SQLite).
Se la connessione cade il download riprova da solo (fino a 6 tentativi, con attesa crescente).
Se chiudi l'app o il PC si spegne, basta rilanciare lo stesso batch: i file completati vengono saltati
e quelli parziali ripartono dall'ultimo blocco salvato.
A fine download ogni file viene verificato (dimensione) e ne viene calcolato lo SHA-256, registrato nel database.

### Doppioni
Con **Salta i doppioni** attivo, lo stesso file ripubblicato nel canale con un altro nome viene saltato
(stesso documento Telegram). Se il file era stato ricaricato da capo, viene riconosciuto dopo il download
(stesso SHA-256) e scartato. Ogni file saltato compare in giallo nel registro con il motivo;
la casella **Mostra avvisi** nasconde o mostra le righe gialle.

### Seguire una chat
Con **Continua a seguire la chat**, finito il download l'app resta in ascolto: Telegram la avvisa dei nuovi
messaggi e i file vengono scaricati subito (più un controllo di sicurezza ogni 10 minuti).
Se chiudi l'app mentre segue una chat, alla riapertura riprende da sola e recupera solo i messaggi
arrivati nel frattempo, senza rileggere tutta la chat. «Smetti di seguire» la ferma.

Mentre scarica o segue una chat, l'app impedisce a Windows di andare in sospensione (lo schermo può spegnersi).

### Limiti di Telegram (FloodWait)
Se Telegram chiede di rallentare, l'app si ferma da sola e mostra il conto alla rovescia, poi riprende.
Con molti download paralleli i limiti scattano più spesso: in caso di problemi usa 1–2 download alla volta.

### Lingua
Menu *Visualizza → Lingua*: italiano, English, Français, Español oppure automatica (lingua di Windows).
Il cambio è immediato; le righe già scritte nel registro restano nella lingua di prima.
Le traduzioni sono in `gtd/locales/` (il testo italiano è la chiave); `tests/test_i18n.py` segnala le frasi
non tradotte e `python tests\test_i18n.py` le elenca tutte.

## Sviluppo

```powershell
.\avvia.ps1          # crea .venv (al primo avvio) e lancia l'app dai sorgenti
.\build.ps1          # esegue i test e crea dist\GerardTelegramDownloader.exe
.venv\Scripts\python -m unittest discover -s tests -v
```

Struttura:

| Percorso | Contenuto |
|---|---|
| `main.py` | avvio Qt + asyncio (qasync) |
| `gtd/engine.py` | scansione messaggi, filtri, download a blocchi, ripresa, FloodWait, parallelismo |
| `gtd/state.py` | database SQLite dello stato dei download |
| `gtd/telegram.py` | client Telethon e sessione cifrata |
| `gtd/dpapi.py` | cifratura Windows DPAPI |
| `gtd/config.py` | impostazioni e log (`%APPDATA%\GerardTelegramDownloader`) |
| `gtd/ui/` | finestra principale, pagina di login, pagina di download |
| `tests/` | test del motore con un client Telegram simulato |

Stack: Python 3.14, Telethon, PyQt6, qasync, PyInstaller.
