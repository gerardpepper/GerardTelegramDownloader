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

La stessa guida è nell'app: nella pagina di accesso e, in ogni momento, nel menu **? → Guida**.

### Uscire dall'account
L'icona di uscita in alto a destra (accanto a «Connesso come…») scollega questo PC dal tuo account Telegram.
Prima ferma i download e le chat seguite. Spuntando **Cancella anche le chiavi API** vengono tolti dal PC
anche api_id e api_hash: al prossimo accesso andranno reinseriti.

## Uso

1. Scegli la chat da **Chat recenti** oppure incolla un link `https://t.me/...` / `@username`
   (per i link d'invito privati devi essere già membro).
2. Scegli la **cartella di destinazione** (anche di rete).
3. Facoltativo: filtri per tipo (preset o estensioni personalizzate), per nome e per dimensione.
4. Opzioni: gestione dei file già esistenti, sottocartelle automatiche (sorgente / tipo / data),
   download paralleli (1–8), notifiche, spegnimento a fine coda.
5. **Avvia download**. Puoi mettere in **Pausa** o **Annullare** in qualsiasi momento.

### Filtro per nome
In **Nome contiene** scrivi una o più parole separate da virgola (es. `fattura, preventivo`): vengono scaricati
solo i file che ne contengono almeno una. Maiuscole e accenti non contano, e `_ - .` valgono come spazi
(`Mario_Rossi.pdf` si trova cercando `mario rossi`). Con **cerca le parole anche nel testo del messaggio**
conta anche la didascalia: utile per le foto, che non hanno un nome. Il filtro si combina con quello per tipo;
se non scegli nessun tipo valgono tutte le estensioni.

### Ripresa dei download
I file in corso vengono scritti come `nome.ext.part` e l'avanzamento è salvato in `state.db` (SQLite).
Se la connessione cade il download riprova da solo (fino a 6 tentativi, con attesa crescente).
Nell'attesa il file lascia il posto agli altri download, quindi nella tabella dei file in corso possono
comparire più righe dei download paralleli: quelle ferme dicono perché nella colonna *Velocità*
(«nuovo tentativo alle …», «in attesa di un posto libero», «in pausa»).
Su ogni riga:
- **↻ Riprova ora** salta l'attesa, oppure ricomincia un download che sembra fermo (riparte dal punto già scaricato);
- **✕ Togli dalla coda** rinuncia al file: il pezzo scaricato viene cancellato e il file non viene ripreso
  ai prossimi avvii. Torna solo se rianalizzi tutta la chat (scheda Download o *Ricontrolla da capo…*).

Se l'errore è «758 bytes read on a total of 1347703872 expected bytes», al posto di Telegram ha risposto
una pagina web: di solito un firewall o un proxy della rete blocca il server di Telegram che contiene quel file.
Riprovare non serve, quindi il file viene segnato subito come non riuscito (con il numero del server, «DC»)
e si ritenta al prossimo avvio: da un'altra rete, o dopo aver sbloccato quel server, scende normalmente.
Se chiudi l'app o il PC si spegne, basta rilanciare lo stesso batch: i file completati vengono saltati
e quelli parziali ripartono dall'ultimo blocco salvato.
A fine download ogni file viene verificato (dimensione) e ne viene calcolato lo SHA-256, registrato nel database.

### Doppioni
Con **Salta i doppioni** attivo, lo stesso file ripubblicato nel canale con un altro nome viene saltato
(stesso documento Telegram). Se il file era stato ricaricato da capo, viene riconosciuto dopo il download
(stesso SHA-256) e scartato. Ogni file saltato compare in giallo nel registro con il motivo;
la casella **Mostra avvisi** nasconde o mostra le righe gialle.

### File spostati o archiviati
Con **Non riscaricare i file già scaricati in passato, anche se non sono più nella cartella** (attiva di serie)
puoi spostare i file altrove, per esempio in un archivio `.7z`, senza che l'app li riscarichi: ricorda in `state.db`
ogni file già scaricato e lo salta (riga gialla «già scaricato in passato, non più nella cartella»), anche con
*Ricontrolla da capo*. Vale anche per lo stesso file ripubblicato in un altro messaggio e per i file che erano
già nella cartella senza essere stati scaricati dall'app: ne ricorda nome e dimensione (tabella `known_files`),
e lo stesso elenco si può riempire con il contenuto di archivi creati a mano. Togli la spunta se
vuoi che i file cancellati dalla cartella vengano riscaricati.

### Seguire le chat (scheda «Segui»)
Nella scheda **Segui** tieni d'occhio quante chat vuoi, ognuna con la sua cartella e i suoi filtri:
l'app resta in ascolto, Telegram la avvisa dei nuovi messaggi e i file vengono scaricati subito
(più un controllo di sicurezza ogni 10 minuti).

- **Aggiungi chat…**, oppure **Segui questa chat…** nella scheda Download (usa la chat, la cartella e i filtri
  già impostati lì). Puoi scegliere se scaricare anche i file già presenti o solo quelli in arrivo da adesso.
- Su ogni riga: **⏸** mette in pausa per un momento, **■ / ▶** smette di seguire o ricomincia.
  In alto, le icone **▶** e **■** avviano o fermano tutte le chat.
- **Modifica…** (o doppio clic) cambia cartella, filtri e opzioni; **Rimuovi** toglie la chat dall'elenco
  (i file scaricati restano). Se cambi i filtri l'app chiede se applicarli anche ai messaggi già arrivati
  (rilegge la chat) o solo a quelli nuovi.
- Ogni chat ha le stesse opzioni della scheda Download: **File già esistenti** (salta / rinomina / sovrascrivi)
  e **Salta i doppioni**.
- **Ricontrolla da capo…** (anche dal tasto destro sulla riga) rilegge una volta tutta la chat e poi torna
  in ascolto. Con «Salta se già presente» scarica solo ciò che manca: i file che rientrano nei filtri ma non erano
  stati scaricati e, se togli la spunta a *Non riscaricare i file già scaricati in passato*, anche quelli
  cancellati o spostati dalla cartella; con «Sovrascrivi» riscarica tutto.
  Prima di partire chiede conferma e dice quale dei due casi si applica.
- I download paralleli indicati in questa scheda valgono per tutte le chat seguite insieme.

Se chiudi l'app, alla riapertura le chat avviate ripartono da sole e leggono solo i messaggi arrivati
nel frattempo, senza rileggere tutta la chat: i file già scaricati non vengono toccati e quelli a metà
ripartono dall'ultimo blocco salvato. I file trovati in passato ma non ancora scaricati vengono rimessi in coda
poco alla volta: per questo il totale dei file cresce, e lo stato lo indica («il totale cresce: altri N file
in sospeso»). I file che erano già falliti si riprovano per ultimi.

Una chat seguita non si può scaricare contemporaneamente dalla scheda Download: prima va fermata.

Mentre scarica o segue una chat, l'app impedisce a Windows di andare in sospensione (lo schermo può spegnersi).
Alla chiusura, se ci sono download in corso, l'app chiede conferma; con **Non chiedere più** la domanda sparisce
(si riattiva da *Visualizza → Chiedi conferma alla chiusura…*).

### Limiti di Telegram (FloodWait)
Se Telegram chiede di rallentare i download, l'app si ferma da sola e mostra il conto alla rovescia, poi riprende;
la pausa vale per tutte le schede, perché il limite è dell'account. Se lo chiede durante la lettura dei messaggi
si ferma solo la lettura: i download continuano.
Con molti download paralleli i limiti scattano più spesso: in caso di problemi usa 1–2 download alla volta.

### Lingua
Menu *Visualizza → Lingua*: italiano, English, Français, Español oppure automatica (lingua di Windows).
Il cambio è immediato; le righe già scritte nel registro restano nella lingua di prima.
Le traduzioni sono in `gtd/locales/` (il testo italiano è la chiave); `tests/test_i18n.py` segnala le frasi
non tradotte e `python tests\test_i18n.py` le elenca tutte.

## Sviluppo

```powershell
.\avvia.ps1          # lancia l'app dai sorgenti (al primo avvio crea l'ambiente Python)
.\build.ps1          # esegue i test e crea dist\GerardTelegramDownloader.exe
.venv\Scripts\python -m unittest discover -s tests -v
```

Gli script usano il primo ambiente Python del progetto che funziona per l'utente Windows corrente
(`.venv`, poi `.venv-*`). Un ambiente creato da un altro utente punta al suo Python e non si può usare:
in quel caso ne creano uno nuovo, `.venv-<utente>`. Le funzioni sono in `tools\python.ps1`.
Per i test usa l'ambiente che funziona per te (es. `.venv-<utente>\Scripts\python`).

Struttura:

| Percorso | Contenuto |
|---|---|
| `main.py` | avvio Qt + asyncio (qasync) |
| `gtd/engine.py` | scansione messaggi, filtri, download a blocchi, ripresa, FloodWait, parallelismo |
| `gtd/state.py` | database SQLite dello stato dei download |
| `gtd/telegram.py` | client Telethon e sessione cifrata |
| `gtd/dpapi.py` | cifratura Windows DPAPI |
| `gtd/config.py` | impostazioni e log (`%APPDATA%\GerardTelegramDownloader`) |
| `gtd/ui/` | finestra principale, accesso, schede Download e Segui, registro |
| `tools/python.ps1` | scelta o creazione dell'ambiente Python, usata da `avvia.ps1` e `build.ps1` |
| `tests/` | test del motore con un client Telegram simulato |

Stack: Python 3.14, Telethon, PyQt6, qasync, PyInstaller.
