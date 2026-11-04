"""English."""

STRINGS: dict[str, str] = {
    # ---- menu e finestra
    "&Account": "&Account",
    "&Visualizza": "&View",
    "Esci dall'account Telegram": "Log out of Telegram",
    "Apri cartella dati dell'app": "Open app data folder",
    "Esci": "Exit",
    "Tema": "Theme",
    "Come il sistema": "Same as system",
    "Chiaro": "Light",
    "Scuro": "Dark",
    "Lingua": "Language",
    "Automatica (lingua di Windows)": "Automatic (Windows language)",
    "Informazioni": "About",
    "Download massivo di media e documenti da Telegram.": "Bulk download of media and documents from Telegram.",
    "Esci dall'account": "Log out",
    "Vuoi disconnettere questo PC dal tuo account Telegram?": "Do you want to disconnect this PC from your Telegram account?",
    "Download in corso": "Downloads in progress",
    "Ci sono download in corso. Chiudere comunque?\nI file parziali verranno ripresi al prossimo avvio.":
        "Downloads are in progress. Close anyway?\nPartial files will be resumed next time.",

    # ---- accesso
    "Accesso a Telegram": "Telegram login",
    "es. 1234567": "e.g. 1234567",
    "32 caratteri esadecimali": "32 hexadecimal characters",
    "Salva e continua": "Save and continue",
    "Telefono:": "Phone:",
    "Invia codice": "Send code",
    "Codice:": "Code:",
    "codice ricevuto nell'app Telegram": "code received in the Telegram app",
    "Password 2FA:": "2FA password:",
    "solo se hai attivato la verifica in due passaggi": "only if you enabled two-step verification",
    "Accedi": "Log in",
    "Benvenuto! Inserisci le chiavi API per iniziare.": "Welcome! Enter your API keys to get started.",
    "Connessione a Telegram in corso…": "Connecting to Telegram…",
    "Connessione non riuscita: {error}": "Connection failed: {error}",
    "Connessione non riuscita: {error}. Controlla la rete e premi «Salva e continua».":
        "Connection failed: {error}. Check your network and press «Save and continue».",
    "Controlla le chiavi: api_id è un numero, api_hash è lungo 32 caratteri.":
        "Check your keys: api_id is a number, api_hash is 32 characters long.",
    "Chiavi salvate. Inserisci il numero di telefono con prefisso internazionale.":
        "Keys saved. Enter your phone number with the international prefix.",
    "Inserisci il numero di telefono con prefisso internazionale.": "Enter your phone number with the international prefix.",
    "Inserisci il numero completo, es. +393331234567.": "Enter the full number, e.g. +393331234567.",
    "Invio del codice…": "Sending the code…",
    "Codice inviato: lo trovi nell'app Telegram (chat «Telegram»).": "Code sent: you will find it in the Telegram app («Telegram» chat).",
    "api_id o api_hash non validi: ricontrollali su my.telegram.org.": "Invalid api_id or api_hash: check them again on my.telegram.org.",
    "Numero di telefono non valido.": "Invalid phone number.",
    "Troppi tentativi: riprova tra {seconds} secondi.": "Too many attempts: try again in {seconds} seconds.",
    "Errore: {error}": "Error: {error}",
    "Il tuo account ha la verifica in due passaggi: inserisci la password.":
        "Your account has two-step verification: enter your password.",
    "Codice errato, riprova.": "Wrong code, please try again.",
    "Codice scaduto: premi di nuovo «Invia codice».": "Code expired: press «Send code» again.",
    "Password errata.": "Wrong password.",
    "Accesso effettuato.": "Logged in.",
    "Disconnesso. Puoi accedere di nuovo quando vuoi.": "Logged out. You can log in again whenever you like.",

    # ---- pagina principale
    "Connesso come {name}": "Logged in as {name}",
    "Accesso effettuato come {name}": "Logged in as {name}",
    "utente": "user",
    "Sorgente": "Source",
    "Aggiorna": "Refresh",
    "Chat recenti:": "Recent chats:",
    "https://t.me/… oppure @username": "https://t.me/… or @username",
    "Se compilato ha la precedenza sulla chat selezionata sopra": "If filled in, it takes precedence over the chat selected above",
    "Link / @username:": "Link / @username:",
    "Destinazione": "Destination",
    "Cartella locale o di rete": "Local or network folder",
    "Sfoglia…": "Browse…",
    "Filtri": "Filters",
    "Documenti": "Documents",
    "Video": "Videos",
    "Immagini": "Images",
    "Archivi": "Archives",
    "Tipi:": "Types:",
    "es. .epub oppure .epub, .mobi": "e.g. .epub or .epub, .mobi",
    "Estensioni:": "Extensions:",
    "Scarico:": "Downloading:",
    "solo {extensions}": "only {extensions}",
    "<b>tutti i tipi di file</b> (nessun tipo selezionato)": "<b>all file types</b> (no type selected)",
    "nessun limite": "no limit",
    "da": "from",
    "a": "to",
    "Dimensione:": "Size:",
    "Opzioni": "Options",
    "Salta se già presente": "Skip if already present",
    "Rinomina (file_(1).ext)": "Rename (file_(1).ext)",
    "Sovrascrivi": "Overwrite",
    "File già esistenti:": "Existing files:",
    "Per sorgente": "By source",
    "Per tipo": "By type",
    "Per data (AAAA-MM)": "By date (YYYY-MM)",
    "Sottocartelle:": "Subfolders:",
    "Download paralleli:": "Parallel downloads:",
    "Salta i doppioni (stesso file ripubblicato con un altro nome)": "Skip duplicates (same file reposted under another name)",
    "Notifiche di Windows (fine batch, errori, nuovi file)": "Windows notifications (batch end, errors, new files)",
    "Spegni il PC al termine": "Shut down the PC when finished",
    "Avvia download": "Start download",
    "Pausa": "Pause",
    "Riprendi": "Resume",
    "Annulla": "Cancel",
    "Pronto.": "Ready.",
    "File in corso": "Current file",
    "Avanzamento": "Progress",
    "Velocità": "Speed",
    "Tempo rimanente": "Time left",
    "Registro": "Log",
    "Mostra avvisi (righe gialle: file saltati, tentativi…)": "Show warnings (yellow lines: skipped files, retries…)",
    "— seleziona una chat —": "— select a chat —",
    "Caricamento chat…": "Loading chats…",
    "canale": "channel",
    "gruppo": "group",
    "chat": "chat",
    "senza nome": "unnamed",
    "Caricate {n} chat recenti": "Loaded {n} recent chats",
    "Telegram chiede di attendere {seconds}s prima di ricaricare le chat": "Telegram asks to wait {seconds}s before reloading the chats",
    "Impossibile caricare le chat: {error}": "Unable to load chats: {error}",
    "Non sei ancora membro di questa chat: unisciti dal client Telegram e riprova.":
        "You are not a member of this chat yet: join it from the Telegram app and try again.",
    "Il link di invito è scaduto o non valido.": "The invite link has expired or is invalid.",
    "Sorgente non trovata: {error}": "Source not found: {error}",
    "Cartella di destinazione": "Destination folder",
    "Sorgente mancante": "Missing source",
    "Seleziona una chat oppure inserisci un link o @username.": "Select a chat or enter a link or @username.",
    "Destinazione mancante": "Missing destination",
    "Scegli la cartella in cui salvare i file.": "Choose the folder where files will be saved.",
    "Filtro dimensione": "Size filter",
    "La dimensione massima è inferiore alla minima.": "The maximum size is lower than the minimum.",
    "Destinazione non valida": "Invalid destination",
    "Impossibile usare la cartella:\n{error}": "Unable to use the folder:\n{error}",
    "Spegnimento automatico": "Automatic shutdown",
    "Al termine dei download il PC verrà spento (con 2 minuti di preavviso). Confermi?":
        "When the downloads finish the PC will shut down (with 2 minutes' notice). Confirm?",
    "Smetto di seguire la chat": "Stopping following the chat",
    "Annullamento in corso… i file parziali verranno ripresi al prossimo avvio": "Cancelling… partial files will be resumed next time",
    "Analisi della chat in corso…": "Scanning the chat…",
    "tutti i tipi": "all types",
    "Avvio batch: «{source}» → {destination} (filtro: {filter})": "Starting batch: «{source}» → {destination} (filter: {filter})",
    "Errore critico: {error}": "Critical error: {error}",
    "Errore durante il download": "Error while downloading",
    "{completed} scaricati ({size}), {skipped} saltati (di cui {duplicates} doppioni), {failed} non riusciti":
        "{completed} downloaded ({size}), {skipped} skipped ({duplicates} of them duplicates), {failed} failed",
    "Annullato.": "Cancelled.",
    "Completato.": "Completed.",
    "Batch terminato: {summary}": "Batch finished: {summary}",
    "Download completati": "Downloads completed",
    "Download terminati con errori": "Downloads finished with errors",
    "download completati": "downloads completed",
    "Il PC si spegnerà tra 2 minuti. Per annullare: Win+R → «shutdown /a»": "The PC will shut down in 2 minutes. To cancel: Win+R → «shutdown /a»",
    "Spegnimento automatico non riuscito: {error}": "Automatic shutdown failed: {error}",
    "Nuovi file in arrivo": "New files arriving",
    "Analisi completata ({scanned} messaggi, {found} file). Download in corso…": "Scan completed ({scanned} messages, {found} files). Downloading…",
    "Analisi in corso: {scanned} messaggi letti, {found} file trovati — i download sono già partiti":
        "Scanning: {scanned} messages read, {found} files found — downloads have already started",
    "{done} di {total} file  ·  {done_size} di {total_size}": "{done} of {total} files  ·  {done_size} of {total_size}",
    "(in aumento, analisi in corso)": "(growing, scan in progress)",
    "In pausa": "Paused",
    "Attesa limite Telegram": "Waiting for Telegram limit",
    "{speed} MB/s · mancano {eta}": "{speed} MB/s · {eta} left",
    "(stima, analisi in corso)": "(estimate, scan in progress)",
    "{done}/{total} file · {done_size} di {total_size}": "{done}/{total} files · {done_size} of {total_size}",
    "Limite di Telegram: ripresa automatica tra {time}": "Telegram limit: resuming automatically in {time}",

    # ---- motore (registro)
    "Download in pausa": "Downloads paused",
    "Download ripreso": "Downloads resumed",
    "Download paralleli: {n}": "Parallel downloads: {n}",
    "Durante un download si può cambiare mettendo in pausa": "During a download you can change it by pausing first",
    "Limite di Telegram (FloodWait): pausa di {seconds} secondi": "Telegram limit (FloodWait): pausing for {seconds} seconds",
    "«{source}»: controllo dei messaggi arrivati dopo l'ultimo visto": "«{source}»: checking messages that arrived after the last one seen",
    "Analisi di «{source}» avviata: i download partono man mano ({n} in parallelo)":
        "Scan of «{source}» started: downloads begin as files are found ({n} in parallel)",
    "Analisi interrotta ({error}): completo i {n} file già in coda": "Scan interrupted ({error}): finishing the {n} files already queued",
    "{name}: errore imprevisto, file saltato": "{name}: unexpected error, file skipped",
    "Analisi: errore ({error}), riprendo dal messaggio {msg_id} tra {seconds}s": "Scan: error ({error}), resuming from message {msg_id} in {seconds}s",
    "Analisi completata: {scanned} messaggi, {found} file da scaricare ({size}), {skipped} saltati perché già presenti":
        "Scan completed: {scanned} messages, {found} files to download ({size}), {skipped} skipped because already present",
    "In ascolto di «{source}»: i nuovi file verranno scaricati appena arrivano": "Listening to «{source}»: new files will be downloaded as soon as they arrive",
    "Controllo nuovi messaggi non riuscito ({error}), riprovo più tardi": "Check for new messages failed ({error}), will retry later",
    "{n} nuovi file da «{source}»": "{n} new files from «{source}»",
    "Saltato: {name} — {reason}": "Skipped: {name} — {reason}",
    "già scaricato in precedenza": "already downloaded before",
    "doppione di «{other}» (già in coda)": "duplicate of «{other}» (already queued)",
    "doppione di «{other}» già scaricato": "duplicate of «{other}», already downloaded",
    "già presente nella cartella": "already in the folder",
    "annullato": "cancelled",
    "aggiornamento riferimento non riuscito: {error}": "reference refresh failed: {error}",
    "messaggio non più disponibile": "message no longer available",
    "{name}: errore ({error}), nuovo tentativo {attempt}/{max} tra {seconds}s": "{name}: error ({error}), retry {attempt}/{max} in {seconds}s",
    "{name}: download non riuscito ({error})": "{name}: download failed ({error})",
    "dimensione {actual} diversa da quella attesa {expected}": "size {actual} differs from the expected {expected}",
    "Scartato: {name} — contenuto identico a «{other}»": "Discarded: {name} — same content as «{other}»",
    "Completato: {name} ({size}, SHA-256 {digest}…)": "Completed: {name} ({size}, SHA-256 {digest}…)",
    "Ripresa di {name} da {size}": "Resuming {name} from {size}",
    "nessun dato da {seconds} secondi": "no data for {seconds} seconds",

    # ---- scheda «Segui», filtro per nome, guida, uscita dall'account
    "<b>Download</b>: scegli la chat da «Chat recenti» (oppure incolla un link t.me o un @username), la cartella di destinazione e, se vuoi, i filtri: tipi di file, parole contenute nel nome, dimensione. Poi premi «Avvia download».<br><br><b>Segui</b>: aggiungi una o più chat da tenere d'occhio, ognuna con la sua cartella e i suoi filtri. L'app resta in ascolto e scarica i nuovi file appena arrivano, anche dopo un riavvio. Con ■ smetti di seguire una chat, con ⏸ la metti in pausa.<br><br><b>Account</b>: «Esci» in alto a destra scollega questo PC dal tuo account Telegram e, se vuoi, cancella anche le chiavi API.":
        "<b>Download</b>: choose the chat from «Recent chats» (or paste a t.me link or an @username), the destination folder and, if you like, the filters: file types, words in the name, size. Then press «Start download».<br><br><b>Follow</b>: add one or more chats to keep an eye on, each with its own folder and filters. The app keeps listening and downloads new files as soon as they arrive, even after a restart. Use ■ to stop following a chat and ⏸ to pause it.<br><br><b>Account</b>: «Log out» at the top right disconnects this PC from your Telegram account and, if you want, also deletes the API keys.",
    "Per usare l'app servono le <b>chiavi API</b> personali di Telegram. Non riguardano un canale: servono all'app per entrare nel <i>tuo</i> account. Si creano una volta sola, in pochi minuti:<br><br>1. apri <a href='https://my.telegram.org/apps'>my.telegram.org/apps</a> nel browser e scrivi il tuo numero con prefisso (es. +393331234567);<br>2. Telegram ti manda un codice <b>dentro l'app Telegram</b> (chat «Telegram», non per SMS): scrivilo nel sito;<br>3. compila il modulo «Create new application»: <i>App title</i> e <i>Short name</i> a piacere (il nome breve: 5–32 lettere o numeri), <i>Platform</i> Desktop, il resto può restare vuoto;<br>4. premi «Create application» e copia qui <b>App api_id</b> (un numero) e <b>App api_hash</b> (32 caratteri);<br>5. premi «Salva e continua», poi inserisci il tuo numero: per accedere riceverai un altro codice nell'app Telegram.<br><br>Le chiavi e la sessione restano solo su questo PC, cifrate con il tuo utente Windows. Non condividere mai l'api_hash. Dal secondo avvio l'accesso è automatico.":
        "To use the app you need your personal Telegram <b>API keys</b>. They are not about a channel: they let the app sign in to <i>your</i> account. You create them only once, in a few minutes:<br><br>1. open <a href='https://my.telegram.org/apps'>my.telegram.org/apps</a> in your browser and enter your phone number with the prefix (e.g. +393331234567);<br>2. Telegram sends you a code <b>inside the Telegram app</b> («Telegram» chat, not by SMS): type it on the website;<br>3. fill in the «Create new application» form: any <i>App title</i> and <i>Short name</i> (short name: 5–32 letters or digits), <i>Platform</i> Desktop, the rest can stay empty;<br>4. press «Create application» and copy <b>App api_id</b> (a number) and <b>App api_hash</b> (32 characters) here;<br>5. press «Save and continue», then enter your phone number: to log in you will receive another code in the Telegram app.<br><br>Keys and session stay on this PC only, encrypted with your Windows user. Never share the api_hash. From the second start on, login is automatic.",
    "Aggiunge la chat alla scheda «Segui», con questa cartella e questi filtri:\nl'app scaricherà i nuovi file appena arrivano.":
        "Adds the chat to the «Follow» tab, with this folder and these filters:\nthe app will download new files as soon as they arrive.",
    "Aggiungi chat…":
        "Add chat…",
    "Al prossimo accesso dovrai inserirle di nuovo":
        "You will have to enter them again next time you log in",
    "Analisi: {scanned} messaggi letti, {found} file":
        "Scanning: {scanned} messages read, {found} files",
    "Avvio…":
        "Starting…",
    "Cancella anche le chiavi API (api_id e api_hash) da questo PC":
        "Also delete the API keys (api_id and api_hash) from this PC",
    "Chat":
        "Chat",
    "Chat già seguita":
        "Chat already followed",
    "Chat non trovata tra le chat recenti: premi «Aggiorna» nella scheda Download":
        "Chat not found among recent chats: press «Refresh» in the Download tab",
    "Chat:":
        "Chat:",
    "Come si usa":
        "How to use it",
    "Destinazione:":
        "Destination:",
    "Disconnesso e chiavi API cancellate da questo PC.":
        "Logged out and API keys deleted from this PC.",
    "Download":
        "Download",
    "Ferma":
        "Stopped",
    "Guida":
        "Guide",
    "I download in corso e le chat seguite verranno fermati.":
        "Running downloads and followed chats will be stopped.",
    "Impostazioni aggiornate":
        "Settings updated",
    "In ascolto":
        "Listening",
    "In attesa: nuovo tentativo tra un minuto":
        "Waiting: retrying in a minute",
    "Le chiavi API":
        "The API keys",
    "Modifica chat seguita":
        "Edit followed chat",
    "Modifica…":
        "Edit…",
    "Nessuna chat attiva: premi ▶ accanto a quelle da seguire.":
        "No active chat: press ▶ next to the ones you want to follow.",
    "Nessuna chat seguita. Premi «Aggiungi chat…» oppure, nella scheda Download, «Segui questa chat…». L'app scaricherà i nuovi file appena arrivano.":
        "No followed chats. Press «Add chat…» or, in the Download tab, «Follow this chat…». The app will download new files as soon as they arrive.",
    "Nome contiene:":
        "Name contains:",
    "Nuovi file":
        "New files",
    "Per tutte le chat seguite insieme":
        "For all followed chats together",
    "Rimuovi":
        "Remove",
    "Rimuovi chat":
        "Remove chat",
    "Riprendo a seguire {n} chat (recupero dei file arrivati mentre l'app era chiusa)":
        "Resuming {n} followed chats (fetching the files that arrived while the app was closed)",
    "Scarica anche i file già presenti nella chat":
        "Also download the files already in the chat",
    "Scarica solo i file che contengono una di queste parole (separate da virgola).\nMaiuscole e accenti non contano. Vuoto = qualsiasi nome.":
        "Download only files containing one of these words (comma separated).\nCase and accents don't matter. Empty = any name.",
    "Scarico {done} di {total} file ({percent}%)":
        "Downloading {done} of {total} files ({percent}%)",
    "Segui":
        "Follow",
    "Segui ({n})":
        "Follow ({n})",
    "Segui questa chat…":
        "Follow this chat…",
    "Segui una chat":
        "Follow a chat",
    "Senza spunta vengono scaricati solo i file che arrivano da adesso in poi":
        "If unticked, only files arriving from now on are downloaded",
    "Smettere di seguire «{source}» e toglierla dall'elenco?\nI file già scaricati restano dove sono.":
        "Stop following «{source}» and remove it from the list?\nFiles already downloaded stay where they are.",
    "Stai seguendo {n} chat. Chiudere comunque?\nAlla riapertura l'app riprenderà da sola, recuperando i file arrivati nel frattempo.":
        "You are following {n} chats. Close anyway?\nWhen reopened, the app will resume on its own and fetch the files that arrived in the meantime.",
    "Stai seguendo {n} chat: i nuovi file vengono scaricati appena arrivano, anche dopo un riavvio dell'app.":
        "You are following {n} chats: new files are downloaded as soon as they arrive, even after the app restarts.",
    "Stato":
        "Status",
    "Ultimo controllo":
        "Last check",
    "Utile per le foto, che non hanno un nome, e per i canali che descrivono il file nel messaggio":
        "Useful for photos, which have no name, and for channels that describe the file in the message",
    "cerca le parole anche nel testo del messaggio":
        "also look for the words in the message text",
    "es. fattura oppure preventivo, offerta":
        "e.g. invoice or quote, offer",
    "la chat è in download nella scheda Download: riparto quando ha finito":
        "the chat is being downloaded in the Download tab: I'll start again when it's done",
    "nome con «{words}»":
        "name with «{words}»",
    "«{source}» è già nell'elenco: usa «Modifica…» per cambiarne le impostazioni.":
        "«{source}» is already in the list: use «Edit…» to change its settings.",
    "«{source}» è già seguita nella scheda «Segui», che ne scarica i file: fermala con ■ se vuoi scaricarla da qui":
        "«{source}» is already followed in the «Follow» tab, which downloads its files: stop it there with ■ if you want to download it from here",

    # ---- scheda «Segui»: pulsanti Ferma, ripresa graduale dei sospesi
    "Analisi: Telegram chiede di rallentare, riprendo tra {seconds}s (i download continuano)":
        "Scanning: Telegram asks to slow down, resuming in {seconds}s (downloads continue)",
    "Ferma tutte":
        "Stop all",
    "Ripresa dei file in sospeso interrotta ({error}): riprovo al prossimo avvio":
        "Resuming pending files was interrupted ({error}): I'll try again next start",
    "Smetto di seguire tutte le chat":
        "Stopping following all chats",
    "{n} file rimasti in sospeso dall'ultima volta: li rimetto in coda poco alla volta":
        "{n} files left pending from last time: queuing them again a few at a time",

    # ---- conferma alla chiusura
    "Chiedi conferma alla chiusura se ci sono download in corso":
        "Ask for confirmation on exit if downloads are running",
    "Chiudi":
        "Close",
    "Conferma":
        "Confirm",
    "Non chiedere più (si riattiva dal menu Visualizza)":
        "Don't ask again (can be turned back on from the View menu)",

    # ---- scheda «Segui»: pausa e avvio per chat
    "Avvia tutte":
        "Start all",
    "Pausa: si ferma un momento, senza smettere di seguire la chat":
        "Pause: stops for a moment, without unfollowing the chat",
    "Ferma: smette di seguire la chat (anche ai prossimi avvii)":
        "Stop: stops following the chat (also on next starts)",
    "Avvia: segue la chat e scarica i nuovi file":
        "Start: follows the chat and downloads new files",

    # ---- scheda «Segui»: file sospesi ancora da riprendere
    "Scarico {done} di {total} file ({percent}%) · il totale cresce: altri {left} file in sospeso da riprendere":
        "Downloading {done} of {total} files ({percent}%) · the total is growing: {left} more pending files to resume",
    "il totale cresce: altri {left} file in sospeso da riprendere":
        "the total is growing: {left} more pending files to resume",

    # ---- scheda «Segui»: ricontrolla da capo, opzioni dei file esistenti
    "Applicare i nuovi filtri anche ai messaggi già arrivati in «{source}»?\nL'app rilegge la chat dall'inizio e scarica i file che ora corrispondono; quelli già scaricati vengono saltati.":
        "Apply the new filters to the messages already in «{source}» too?\nThe app reads the chat again from the start and downloads the files that now match; those already downloaded are skipped.",
    "Avvia":
        "Start",
    "Filtri cambiati":
        "Filters changed",
    "Ricontrolla":
        "Recheck",
    "Ricontrolla da capo":
        "Recheck from the start",
    "Ricontrolla da capo…":
        "Recheck from the start…",
    "Ricontrollo la chat da capo":
        "Rechecking the chat from the start",
    "Rilegge tutta la chat dall'inizio e scarica i file che mancano\n(o tutti, se la chat è impostata per sovrascrivere i file già esistenti)":
        "Reads the whole chat again from the start and downloads the missing files\n(or all of them, if the chat is set to overwrite existing files)",
    "Rileggo tutta «{source}» dall'inizio e riscarico TUTTI i file che corrispondono ai filtri, sovrascrivendo quelli già presenti nella cartella.\nSu una chat grande può richiedere molto tempo.":
        "I'll read all of «{source}» again from the start and download ALL files matching the filters again, overwriting those already in the folder.\nOn a large chat this can take a long time.",
    "Rileggo tutta «{source}» dall'inizio e scarico solo i file che mancano: quelli cancellati o spostati dalla cartella e quelli che rientrano nei filtri ma non erano stati scaricati.\nI file già presenti vengono saltati. Su una chat grande la lettura richiede qualche minuto.":
        "I'll read all of «{source}» again from the start and download only the missing files: those deleted or moved from the folder and those matching the filters that weren't downloaded.\nFiles already there are skipped. On a large chat reading takes a few minutes.",
    "Solo ai messaggi nuovi":
        "Only to new messages",
    "Sì, ricontrolla la chat":
        "Yes, recheck the chat",
    "Riprova ora: salta l'attesa prima del prossimo tentativo, o ricomincia il download se è fermo (riparte da dove era arrivato)":
        'Retry now: skips the wait before the next attempt, or restarts the download if it is stuck (it resumes where it left off)',
    'Togli dalla coda: il file non viene scaricato, nemmeno al prossimo avvio (torna solo rianalizzando tutta la chat)':
        'Remove from queue: the file is not downloaded, not even at the next start (it comes back only by rescanning the whole chat)',
    'Tolto dalla coda: {name}':
        'Removed from queue: {name}',
    'in attesa di un posto libero':
        'waiting for a free slot',
    'in pausa':
        'paused',
    'la rete blocca il server di Telegram che contiene il file (DC {dc}): al posto dei dati arriva una pagina web, di solito da un firewall o da un proxy':
        'the network blocks the Telegram server that holds the file (DC {dc}): a web page arrives instead of the data, usually from a firewall or a proxy',
    'nuovo tentativo alle {time}':
        'next attempt at {time}',
    'tolto dalla coda':
        'removed from queue',
    '{name}: nuovo tentativo richiesto':
        '{name}: new attempt requested',
}
