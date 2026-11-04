"""Español."""

STRINGS: dict[str, str] = {
    # ---- menu e finestra
    "&Account": "&Cuenta",
    "&Visualizza": "&Ver",
    "Esci dall'account Telegram": "Cerrar sesión de Telegram",
    "Apri cartella dati dell'app": "Abrir la carpeta de datos de la aplicación",
    "Esci": "Salir",
    "Tema": "Tema",
    "Come il sistema": "Igual que el sistema",
    "Chiaro": "Claro",
    "Scuro": "Oscuro",
    "Lingua": "Idioma",
    "Automatica (lingua di Windows)": "Automático (idioma de Windows)",
    "Informazioni": "Acerca de",
    "Download massivo di media e documenti da Telegram.": "Descarga masiva de archivos multimedia y documentos de Telegram.",
    "Esci dall'account": "Cerrar sesión",
    "Vuoi disconnettere questo PC dal tuo account Telegram?": "¿Quieres desconectar este PC de tu cuenta de Telegram?",
    "Download in corso": "Descargas en curso",
    "Ci sono download in corso. Chiudere comunque?\nI file parziali verranno ripresi al prossimo avvio.":
        "Hay descargas en curso. ¿Cerrar de todos modos?\nLos archivos parciales se reanudarán en el próximo inicio.",

    # ---- accesso
    "Accesso a Telegram": "Inicio de sesión en Telegram",
    "es. 1234567": "p. ej. 1234567",
    "32 caratteri esadecimali": "32 caracteres hexadecimales",
    "Salva e continua": "Guardar y continuar",
    "Telefono:": "Teléfono:",
    "Invia codice": "Enviar código",
    "Codice:": "Código:",
    "codice ricevuto nell'app Telegram": "código recibido en la aplicación Telegram",
    "Password 2FA:": "Contraseña 2FA:",
    "solo se hai attivato la verifica in due passaggi": "solo si activaste la verificación en dos pasos",
    "Accedi": "Iniciar sesión",
    "Benvenuto! Inserisci le chiavi API per iniziare.": "¡Bienvenido! Introduce tus claves API para empezar.",
    "Connessione a Telegram in corso…": "Conectando con Telegram…",
    "Connessione non riuscita: {error}": "Conexión fallida: {error}",
    "Connessione non riuscita: {error}. Controlla la rete e premi «Salva e continua».":
        "Conexión fallida: {error}. Comprueba la red y pulsa «Guardar y continuar».",
    "Controlla le chiavi: api_id è un numero, api_hash è lungo 32 caratteri.":
        "Comprueba las claves: api_id es un número y api_hash tiene 32 caracteres.",
    "Chiavi salvate. Inserisci il numero di telefono con prefisso internazionale.":
        "Claves guardadas. Introduce tu número de teléfono con el prefijo internacional.",
    "Inserisci il numero di telefono con prefisso internazionale.": "Introduce tu número de teléfono con el prefijo internacional.",
    "Inserisci il numero completo, es. +393331234567.": "Introduce el número completo, p. ej. +393331234567.",
    "Invio del codice…": "Enviando el código…",
    "Codice inviato: lo trovi nell'app Telegram (chat «Telegram»).": "Código enviado: lo encontrarás en la aplicación Telegram (chat «Telegram»).",
    "api_id o api_hash non validi: ricontrollali su my.telegram.org.": "api_id o api_hash no válidos: compruébalos en my.telegram.org.",
    "Numero di telefono non valido.": "Número de teléfono no válido.",
    "Troppi tentativi: riprova tra {seconds} secondi.": "Demasiados intentos: vuelve a intentarlo en {seconds} segundos.",
    "Errore: {error}": "Error: {error}",
    "Il tuo account ha la verifica in due passaggi: inserisci la password.":
        "Tu cuenta tiene verificación en dos pasos: introduce la contraseña.",
    "Codice errato, riprova.": "Código incorrecto, inténtalo de nuevo.",
    "Codice scaduto: premi di nuovo «Invia codice».": "Código caducado: pulsa de nuevo «Enviar código».",
    "Password errata.": "Contraseña incorrecta.",
    "Accesso effettuato.": "Sesión iniciada.",
    "Disconnesso. Puoi accedere di nuovo quando vuoi.": "Sesión cerrada. Puedes volver a entrar cuando quieras.",

    # ---- pagina principale
    "Connesso come {name}": "Conectado como {name}",
    "Accesso effettuato come {name}": "Sesión iniciada como {name}",
    "utente": "usuario",
    "Sorgente": "Origen",
    "Aggiorna": "Actualizar",
    "Chat recenti:": "Chats recientes:",
    "https://t.me/… oppure @username": "https://t.me/… o @username",
    "Se compilato ha la precedenza sulla chat selezionata sopra": "Si se rellena, tiene prioridad sobre el chat seleccionado arriba",
    "Link / @username:": "Enlace / @username:",
    "Destinazione": "Destino",
    "Cartella locale o di rete": "Carpeta local o de red",
    "Sfoglia…": "Examinar…",
    "Filtri": "Filtros",
    "Documenti": "Documentos",
    "Video": "Vídeos",
    "Immagini": "Imágenes",
    "Archivi": "Archivos comprimidos",
    "Tipi:": "Tipos:",
    "es. .epub oppure .epub, .mobi": "p. ej. .epub o .epub, .mobi",
    "Estensioni:": "Extensiones:",
    "Scarico:": "Descargo:",
    "solo {extensions}": "solo {extensions}",
    "<b>tutti i tipi di file</b> (nessun tipo selezionato)": "<b>todos los tipos de archivo</b> (ningún tipo seleccionado)",
    "nessun limite": "sin límite",
    "da": "de",
    "a": "a",
    "Dimensione:": "Tamaño:",
    "Opzioni": "Opciones",
    "Salta se già presente": "Omitir si ya existe",
    "Rinomina (file_(1).ext)": "Renombrar (file_(1).ext)",
    "Sovrascrivi": "Sobrescribir",
    "File già esistenti:": "Archivos existentes:",
    "Per sorgente": "Por origen",
    "Per tipo": "Por tipo",
    "Per data (AAAA-MM)": "Por fecha (AAAA-MM)",
    "Sottocartelle:": "Subcarpetas:",
    "Download paralleli:": "Descargas en paralelo:",
    "Salta i doppioni (stesso file ripubblicato con un altro nome)": "Omitir duplicados (mismo archivo publicado de nuevo con otro nombre)",
    "Notifiche di Windows (fine batch, errori, nuovi file)": "Notificaciones de Windows (fin del lote, errores, archivos nuevos)",
    "Spegni il PC al termine": "Apagar el PC al terminar",
    "Avvia download": "Iniciar descarga",
    "Pausa": "Pausa",
    "Riprendi": "Reanudar",
    "Annulla": "Cancelar",
    "Pronto.": "Listo.",
    "File in corso": "Archivo actual",
    "Avanzamento": "Progreso",
    "Velocità": "Velocidad",
    "Tempo rimanente": "Tiempo restante",
    "Registro": "Registro",
    "Mostra avvisi (righe gialle: file saltati, tentativi…)": "Mostrar avisos (líneas amarillas: archivos omitidos, reintentos…)",
    "— seleziona una chat —": "— selecciona un chat —",
    "Caricamento chat…": "Cargando chats…",
    "canale": "canal",
    "gruppo": "grupo",
    "chat": "chat",
    "senza nome": "sin nombre",
    "Caricate {n} chat recenti": "Cargados {n} chats recientes",
    "Telegram chiede di attendere {seconds}s prima di ricaricare le chat": "Telegram pide esperar {seconds} s antes de volver a cargar los chats",
    "Impossibile caricare le chat: {error}": "No se pueden cargar los chats: {error}",
    "Non sei ancora membro di questa chat: unisciti dal client Telegram e riprova.":
        "Todavía no eres miembro de este chat: únete desde Telegram y vuelve a intentarlo.",
    "Il link di invito è scaduto o non valido.": "El enlace de invitación ha caducado o no es válido.",
    "Sorgente non trovata: {error}": "Origen no encontrado: {error}",
    "Cartella di destinazione": "Carpeta de destino",
    "Sorgente mancante": "Falta el origen",
    "Seleziona una chat oppure inserisci un link o @username.": "Selecciona un chat o introduce un enlace o @username.",
    "Destinazione mancante": "Falta el destino",
    "Scegli la cartella in cui salvare i file.": "Elige la carpeta donde guardar los archivos.",
    "Filtro dimensione": "Filtro de tamaño",
    "La dimensione massima è inferiore alla minima.": "El tamaño máximo es inferior al mínimo.",
    "Destinazione non valida": "Destino no válido",
    "Impossibile usare la cartella:\n{error}": "No se puede usar la carpeta:\n{error}",
    "Spegnimento automatico": "Apagado automático",
    "Al termine dei download il PC verrà spento (con 2 minuti di preavviso). Confermi?":
        "Al terminar las descargas el PC se apagará (con 2 minutos de aviso). ¿Confirmas?",
    "Smetto di seguire la chat": "Dejo de seguir el chat",
    "Annullamento in corso… i file parziali verranno ripresi al prossimo avvio": "Cancelando… los archivos parciales se reanudarán en el próximo inicio",
    "Analisi della chat in corso…": "Analizando el chat…",
    "tutti i tipi": "todos los tipos",
    "Avvio batch: «{source}» → {destination} (filtro: {filter})": "Inicio del lote: «{source}» → {destination} (filtro: {filter})",
    "Errore critico: {error}": "Error crítico: {error}",
    "Errore durante il download": "Error durante la descarga",
    "{completed} scaricati ({size}), {skipped} saltati (di cui {duplicates} doppioni), {failed} non riusciti":
        "{completed} descargados ({size}), {skipped} omitidos ({duplicates} de ellos duplicados), {failed} fallidos",
    "Annullato.": "Cancelado.",
    "Completato.": "Completado.",
    "Batch terminato: {summary}": "Lote terminado: {summary}",
    "Download completati": "Descargas completadas",
    "Download terminati con errori": "Descargas terminadas con errores",
    "download completati": "descargas completadas",
    "Il PC si spegnerà tra 2 minuti. Per annullare: Win+R → «shutdown /a»": "El PC se apagará en 2 minutos. Para cancelar: Win+R → «shutdown /a»",
    "Spegnimento automatico non riuscito: {error}": "Apagado automático fallido: {error}",
    "Nuovi file in arrivo": "Llegan archivos nuevos",
    "Analisi completata ({scanned} messaggi, {found} file). Download in corso…": "Análisis completado ({scanned} mensajes, {found} archivos). Descargando…",
    "Analisi in corso: {scanned} messaggi letti, {found} file trovati — i download sono già partiti":
        "Analizando: {scanned} mensajes leídos, {found} archivos encontrados — las descargas ya han empezado",
    "{done} di {total} file  ·  {done_size} di {total_size}": "{done} de {total} archivos  ·  {done_size} de {total_size}",
    "(in aumento, analisi in corso)": "(en aumento, análisis en curso)",
    "In pausa": "En pausa",
    "Attesa limite Telegram": "Esperando el límite de Telegram",
    "{speed} MB/s · mancano {eta}": "{speed} MB/s · faltan {eta}",
    "(stima, analisi in corso)": "(estimación, análisis en curso)",
    "{done}/{total} file · {done_size} di {total_size}": "{done}/{total} archivos · {done_size} de {total_size}",
    "Limite di Telegram: ripresa automatica tra {time}": "Límite de Telegram: reanudación automática en {time}",

    # ---- motore (registro)
    "Download in pausa": "Descargas en pausa",
    "Download ripreso": "Descargas reanudadas",
    "Download paralleli: {n}": "Descargas en paralelo: {n}",
    "Durante un download si può cambiare mettendo in pausa": "Durante una descarga se puede cambiar poniéndola en pausa",
    "Limite di Telegram (FloodWait): pausa di {seconds} secondi": "Límite de Telegram (FloodWait): pausa de {seconds} segundos",
    "«{source}»: controllo dei messaggi arrivati dopo l'ultimo visto": "«{source}»: comprobando los mensajes llegados después del último visto",
    "Analisi di «{source}» avviata: i download partono man mano ({n} in parallelo)":
        "Análisis de «{source}» iniciado: las descargas empiezan sobre la marcha ({n} en paralelo)",
    "Analisi interrotta ({error}): completo i {n} file già in coda": "Análisis interrumpido ({error}): termino los {n} archivos ya en cola",
    "{name}: errore imprevisto, file saltato": "{name}: error inesperado, archivo omitido",
    "Analisi: errore ({error}), riprendo dal messaggio {msg_id} tra {seconds}s": "Análisis: error ({error}), reanudo desde el mensaje {msg_id} en {seconds} s",
    "Analisi completata: {scanned} messaggi, {found} file da scaricare ({size}), {skipped} saltati perché già presenti":
        "Análisis completado: {scanned} mensajes, {found} archivos para descargar ({size}), {skipped} omitidos por estar ya presentes",
    "In ascolto di «{source}»: i nuovi file verranno scaricati appena arrivano": "A la escucha de «{source}»: los archivos nuevos se descargarán en cuanto lleguen",
    "Controllo nuovi messaggi non riuscito ({error}), riprovo più tardi": "Comprobación de mensajes nuevos fallida ({error}), lo reintento más tarde",
    "{n} nuovi file da «{source}»": "{n} archivos nuevos de «{source}»",
    "Saltato: {name} — {reason}": "Omitido: {name} — {reason}",
    "già scaricato in precedenza": "ya descargado anteriormente",
    "doppione di «{other}» (già in coda)": "duplicado de «{other}» (ya en cola)",
    "doppione di «{other}» già scaricato": "duplicado de «{other}», ya descargado",
    "già presente nella cartella": "ya está en la carpeta",
    "annullato": "cancelado",
    "aggiornamento riferimento non riuscito: {error}": "actualización de la referencia fallida: {error}",
    "messaggio non più disponibile": "mensaje ya no disponible",
    "{name}: errore ({error}), nuovo tentativo {attempt}/{max} tra {seconds}s": "{name}: error ({error}), reintento {attempt}/{max} en {seconds} s",
    "{name}: download non riuscito ({error})": "{name}: descarga fallida ({error})",
    "dimensione {actual} diversa da quella attesa {expected}": "tamaño {actual} distinto del esperado {expected}",
    "Scartato: {name} — contenuto identico a «{other}»": "Descartado: {name} — contenido idéntico a «{other}»",
    "Completato: {name} ({size}, SHA-256 {digest}…)": "Completado: {name} ({size}, SHA-256 {digest}…)",
    "Ripresa di {name} da {size}": "Reanudando {name} desde {size}",
    "nessun dato da {seconds} secondi": "sin datos desde hace {seconds} segundos",

    # ---- scheda «Segui», filtro per nome, guida, uscita dall'account
    "<b>Download</b>: scegli la chat da «Chat recenti» (oppure incolla un link t.me o un @username), la cartella di destinazione e, se vuoi, i filtri: tipi di file, parole contenute nel nome, dimensione. Poi premi «Avvia download».<br><br><b>Segui</b>: aggiungi una o più chat da tenere d'occhio, ognuna con la sua cartella e i suoi filtri. L'app resta in ascolto e scarica i nuovi file appena arrivano, anche dopo un riavvio. Con ■ smetti di seguire una chat, con ⏸ la metti in pausa.<br><br><b>Account</b>: «Esci» in alto a destra scollega questo PC dal tuo account Telegram e, se vuoi, cancella anche le chiavi API.":
        "<b>Descarga</b>: elige el chat en «Chats recientes» (o pega un enlace t.me o un @username), la carpeta de destino y, si quieres, los filtros: tipos de archivo, palabras en el nombre, tamaño. Luego pulsa «Iniciar descarga».<br><br><b>Seguir</b>: añade uno o más chats para vigilar, cada uno con su carpeta y sus filtros. La app se queda a la escucha y descarga los archivos nuevos en cuanto llegan, incluso tras un reinicio. Con ■ dejas de seguir un chat y con ⏸ lo pausas.<br><br><b>Cuenta</b>: «Cerrar sesión» arriba a la derecha desconecta este PC de tu cuenta de Telegram y, si quieres, borra también las claves API.",
    "Per usare l'app servono le <b>chiavi API</b> personali di Telegram. Non riguardano un canale: servono all'app per entrare nel <i>tuo</i> account. Si creano una volta sola, in pochi minuti:<br><br>1. apri <a href='https://my.telegram.org/apps'>my.telegram.org/apps</a> nel browser e scrivi il tuo numero con prefisso (es. +393331234567);<br>2. Telegram ti manda un codice <b>dentro l'app Telegram</b> (chat «Telegram», non per SMS): scrivilo nel sito;<br>3. compila il modulo «Create new application»: <i>App title</i> e <i>Short name</i> a piacere (il nome breve: 5–32 lettere o numeri), <i>Platform</i> Desktop, il resto può restare vuoto;<br>4. premi «Create application» e copia qui <b>App api_id</b> (un numero) e <b>App api_hash</b> (32 caratteri);<br>5. premi «Salva e continua», poi inserisci il tuo numero: per accedere riceverai un altro codice nell'app Telegram.<br><br>Le chiavi e la sessione restano solo su questo PC, cifrate con il tuo utente Windows. Non condividere mai l'api_hash. Dal secondo avvio l'accesso è automatico.":
        "Para usar la app necesitas tus <b>claves API</b> personales de Telegram. No se refieren a un canal: sirven para que la app entre en <i>tu</i> cuenta. Se crean una sola vez, en pocos minutos:<br><br>1. abre <a href='https://my.telegram.org/apps'>my.telegram.org/apps</a> en el navegador y escribe tu número con prefijo (p. ej. +393331234567);<br>2. Telegram te envía un código <b>dentro de la app de Telegram</b> (chat «Telegram», no por SMS): escríbelo en el sitio;<br>3. rellena el formulario «Create new application»: <i>App title</i> y <i>Short name</i> a tu gusto (nombre corto: 5–32 letras o números), <i>Platform</i> Desktop, el resto puede quedar vacío;<br>4. pulsa «Create application» y copia aquí <b>App api_id</b> (un número) y <b>App api_hash</b> (32 caracteres);<br>5. pulsa «Guardar y continuar» y luego escribe tu número: para entrar recibirás otro código en la app de Telegram.<br><br>Las claves y la sesión se quedan solo en este PC, cifradas con tu usuario de Windows. No compartas nunca el api_hash. Desde el segundo inicio el acceso es automático.",
    "Aggiunge la chat alla scheda «Segui», con questa cartella e questi filtri:\nl'app scaricherà i nuovi file appena arrivano.":
        "Añade el chat a la pestaña «Seguir», con esta carpeta y estos filtros:\nla app descargará los archivos nuevos en cuanto lleguen.",
    "Aggiungi chat…":
        "Añadir chat…",
    "Al prossimo accesso dovrai inserirle di nuovo":
        "Tendrás que volver a introducirlas en el próximo acceso",
    "Analisi: {scanned} messaggi letti, {found} file":
        "Análisis: {scanned} mensajes leídos, {found} archivos",
    "Avvio…":
        "Iniciando…",
    "Cancella anche le chiavi API (api_id e api_hash) da questo PC":
        "Borrar también las claves API (api_id y api_hash) de este PC",
    "Chat":
        "Chat",
    "Chat già seguita":
        "Chat ya seguido",
    "Chat non trovata tra le chat recenti: premi «Aggiorna» nella scheda Download":
        "Chat no encontrado entre los chats recientes: pulsa «Actualizar» en la pestaña Descarga",
    "Chat:":
        "Chat:",
    "Come si usa":
        "Cómo se usa",
    "Destinazione:":
        "Destino:",
    "Disconnesso e chiavi API cancellate da questo PC.":
        "Sesión cerrada y claves API borradas de este PC.",
    "Download":
        "Descarga",
    "Ferma":
        "Detenido",
    "Guida":
        "Guía",
    "I download in corso e le chat seguite verranno fermati.":
        "Las descargas en curso y los chats seguidos se detendrán.",
    "Impostazioni aggiornate":
        "Ajustes actualizados",
    "In ascolto":
        "A la escucha",
    "In attesa: nuovo tentativo tra un minuto":
        "En espera: nuevo intento en un minuto",
    "Le chiavi API":
        "Las claves API",
    "Modifica chat seguita":
        "Editar chat seguido",
    "Modifica…":
        "Editar…",
    "Nessuna chat attiva: premi ▶ accanto a quelle da seguire.":
        "Ningún chat activo: pulsa ▶ junto a los que quieras seguir.",
    "Nessuna chat seguita. Premi «Aggiungi chat…» oppure, nella scheda Download, «Segui questa chat…». L'app scaricherà i nuovi file appena arrivano.":
        "Ningún chat seguido. Pulsa «Añadir chat…» o, en la pestaña Descarga, «Seguir este chat…». La app descargará los archivos nuevos en cuanto lleguen.",
    "Nome contiene:":
        "El nombre contiene:",
    "Nuovi file":
        "Archivos nuevos",
    "Per tutte le chat seguite insieme":
        "Para todos los chats seguidos juntos",
    "Rimuovi":
        "Quitar",
    "Rimuovi chat":
        "Quitar chat",
    "Riprendo a seguire {n} chat (recupero dei file arrivati mentre l'app era chiusa)":
        "Vuelvo a seguir {n} chats (recupero los archivos llegados mientras la app estaba cerrada)",
    "Scarica anche i file già presenti nella chat":
        "Descargar también los archivos que ya están en el chat",
    "Scarica solo i file che contengono una di queste parole (separate da virgola).\nMaiuscole e accenti non contano. Vuoto = qualsiasi nome.":
        "Descarga solo los archivos que contienen una de estas palabras (separadas por comas).\nMayúsculas y acentos no importan. Vacío = cualquier nombre.",
    "Scarico {done} di {total} file ({percent}%)":
        "Descargando {done} de {total} archivos ({percent}%)",
    "Segui":
        "Seguir",
    "Segui ({n})":
        "Seguir ({n})",
    "Segui questa chat…":
        "Seguir este chat…",
    "Segui una chat":
        "Seguir un chat",
    "Senza spunta vengono scaricati solo i file che arrivano da adesso in poi":
        "Sin marcar, solo se descargan los archivos que lleguen a partir de ahora",
    "Smettere di seguire «{source}» e toglierla dall'elenco?\nI file già scaricati restano dove sono.":
        "¿Dejar de seguir «{source}» y quitarlo de la lista?\nLos archivos ya descargados se quedan donde están.",
    "Stai seguendo {n} chat. Chiudere comunque?\nAlla riapertura l'app riprenderà da sola, recuperando i file arrivati nel frattempo.":
        "Estás siguiendo {n} chats. ¿Cerrar de todos modos?\nAl volver a abrirla, la app se reanudará sola y recuperará los archivos llegados mientras tanto.",
    "Stai seguendo {n} chat: i nuovi file vengono scaricati appena arrivano, anche dopo un riavvio dell'app.":
        "Estás siguiendo {n} chats: los archivos nuevos se descargan en cuanto llegan, incluso tras reiniciar la app.",
    "Stato":
        "Estado",
    "Ultimo controllo":
        "Última comprobación",
    "Utile per le foto, che non hanno un nome, e per i canali che descrivono il file nel messaggio":
        "Útil para las fotos, que no tienen nombre, y para los canales que describen el archivo en el mensaje",
    "cerca le parole anche nel testo del messaggio":
        "buscar las palabras también en el texto del mensaje",
    "es. fattura oppure preventivo, offerta":
        "p. ej. factura o presupuesto, oferta",
    "la chat è in download nella scheda Download: riparto quando ha finito":
        "el chat se está descargando en la pestaña Descarga: vuelvo a empezar cuando termine",
    "nome con «{words}»":
        "nombre con «{words}»",
    "«{source}» è già nell'elenco: usa «Modifica…» per cambiarne le impostazioni.":
        "«{source}» ya está en la lista: usa «Editar…» para cambiar sus ajustes.",
    "«{source}» è già seguita nella scheda «Segui», che ne scarica i file: fermala con ■ se vuoi scaricarla da qui":
        "«{source}» ya se sigue en la pestaña «Seguir», que descarga sus archivos: detenlo con ■ si quieres descargarlo desde aquí",

    # ---- scheda «Segui»: pulsanti Ferma, ripresa graduale dei sospesi
    "Analisi: Telegram chiede di rallentare, riprendo tra {seconds}s (i download continuano)":
        "Análisis: Telegram pide ir más despacio, reanudo en {seconds}s (las descargas continúan)",
    "Ferma tutte":
        "Detener todos",
    "Ripresa dei file in sospeso interrotta ({error}): riprovo al prossimo avvio":
        "Reanudación de los archivos pendientes interrumpida ({error}): lo reintento en el próximo inicio",
    "Smetto di seguire tutte le chat":
        "Dejo de seguir todos los chats",
    "{n} file rimasti in sospeso dall'ultima volta: li rimetto in coda poco alla volta":
        "{n} archivos pendientes de la última vez: los vuelvo a poner en cola poco a poco",

    # ---- conferma alla chiusura
    "Chiedi conferma alla chiusura se ci sono download in corso":
        "Pedir confirmación al cerrar si hay descargas en curso",
    "Chiudi":
        "Cerrar",
    "Conferma":
        "Confirmar",
    "Non chiedere più (si riattiva dal menu Visualizza)":
        "No volver a preguntar (se reactiva desde el menú Ver)",

    # ---- scheda «Segui»: pausa e avvio per chat
    "Avvia tutte":
        "Iniciar todos",
    "Pausa: si ferma un momento, senza smettere di seguire la chat":
        "Pausa: se detiene un momento, sin dejar de seguir el chat",
    "Ferma: smette di seguire la chat (anche ai prossimi avvii)":
        "Detener: deja de seguir el chat (también en los próximos inicios)",
    "Avvia: segue la chat e scarica i nuovi file":
        "Iniciar: sigue el chat y descarga los archivos nuevos",

    # ---- scheda «Segui»: file sospesi ancora da riprendere
    "Scarico {done} di {total} file ({percent}%) · il totale cresce: altri {left} file in sospeso da riprendere":
        "Descargando {done} de {total} archivos ({percent}%) · el total crece: otros {left} archivos pendientes por reanudar",
    "il totale cresce: altri {left} file in sospeso da riprendere":
        "el total crece: otros {left} archivos pendientes por reanudar",

    # ---- scheda «Segui»: ricontrolla da capo, opzioni dei file esistenti
    "Applicare i nuovi filtri anche ai messaggi già arrivati in «{source}»?\nL'app rilegge la chat dall'inizio e scarica i file che ora corrispondono; quelli già scaricati vengono saltati.":
        "¿Aplicar los nuevos filtros también a los mensajes ya llegados a «{source}»?\nLa app vuelve a leer el chat desde el principio y descarga los archivos que ahora coinciden; los ya descargados se omiten.",
    "Avvia":
        "Iniciar",
    "Filtri cambiati":
        "Filtros cambiados",
    "Ricontrolla":
        "Revisar",
    "Ricontrolla da capo":
        "Revisar desde el principio",
    "Ricontrolla da capo…":
        "Revisar desde el principio…",
    "Ricontrollo la chat da capo":
        "Reviso el chat desde el principio",
    "Rilegge tutta la chat dall'inizio e scarica i file che mancano\n(o tutti, se la chat è impostata per sovrascrivere i file già esistenti)":
        "Vuelve a leer todo el chat desde el principio y descarga los archivos que faltan\n(o todos, si el chat está configurado para sobrescribir los archivos existentes)",
    "Rileggo tutta «{source}» dall'inizio e riscarico TUTTI i file che corrispondono ai filtri, sovrascrivendo quelli già presenti nella cartella.\nSu una chat grande può richiedere molto tempo.":
        "Vuelvo a leer todo «{source}» desde el principio y descargo de nuevo TODOS los archivos que coinciden con los filtros, sobrescribiendo los que ya están en la carpeta.\nEn un chat grande puede tardar mucho.",
    "Rileggo tutta «{source}» dall'inizio e scarico solo i file che mancano: quelli cancellati o spostati dalla cartella e quelli che rientrano nei filtri ma non erano stati scaricati.\nI file già presenti vengono saltati. Su una chat grande la lettura richiede qualche minuto.":
        "Vuelvo a leer todo «{source}» desde el principio y descargo solo los archivos que faltan: los borrados o movidos de la carpeta y los que coinciden con los filtros pero no se habían descargado.\nLos archivos ya presentes se omiten. En un chat grande la lectura tarda unos minutos.",
    "Solo ai messaggi nuovi":
        "Solo a los mensajes nuevos",
    "Sì, ricontrolla la chat":
        "Sí, revisar el chat",
    "Riprova ora: salta l'attesa prima del prossimo tentativo, o ricomincia il download se è fermo (riparte da dove era arrivato)":
        'Reintentar ahora: omite la espera antes del próximo intento, o reinicia la descarga si está detenida (continúa desde donde se quedó)',
    'Togli dalla coda: il file non viene scaricato, nemmeno al prossimo avvio (torna solo rianalizzando tutta la chat)':
        'Quitar de la cola: el archivo no se descarga, ni siquiera en el próximo inicio (solo vuelve al reanalizar todo el chat)',
    'Tolto dalla coda: {name}':
        'Quitado de la cola: {name}',
    'in attesa di un posto libero':
        'esperando un hueco libre',
    'in pausa':
        'en pausa',
    'la rete blocca il server di Telegram che contiene il file (DC {dc}): al posto dei dati arriva una pagina web, di solito da un firewall o da un proxy':
        'la red bloquea el servidor de Telegram que contiene el archivo (DC {dc}): en lugar de los datos llega una página web, normalmente de un cortafuegos o un proxy',
    'nuovo tentativo alle {time}':
        'nuevo intento a las {time}',
    'tolto dalla coda':
        'quitado de la cola',
    '{name}: nuovo tentativo richiesto':
        '{name}: nuevo intento solicitado',
}
