"""Français."""

STRINGS: dict[str, str] = {
    # ---- menu e finestra
    "&Account": "&Compte",
    "&Visualizza": "&Affichage",
    "Esci dall'account Telegram": "Se déconnecter de Telegram",
    "Apri cartella dati dell'app": "Ouvrir le dossier de données de l'application",
    "Esci": "Quitter",
    "Tema": "Thème",
    "Come il sistema": "Comme le système",
    "Chiaro": "Clair",
    "Scuro": "Sombre",
    "Lingua": "Langue",
    "Automatica (lingua di Windows)": "Automatique (langue de Windows)",
    "Informazioni": "À propos",
    "Download massivo di media e documenti da Telegram.": "Téléchargement en masse de médias et de documents depuis Telegram.",
    "Esci dall'account": "Se déconnecter",
    "Vuoi disconnettere questo PC dal tuo account Telegram?": "Voulez-vous déconnecter ce PC de votre compte Telegram ?",
    "Download in corso": "Téléchargements en cours",
    "Ci sono download in corso. Chiudere comunque?\nI file parziali verranno ripresi al prossimo avvio.":
        "Des téléchargements sont en cours. Fermer quand même ?\nLes fichiers partiels reprendront au prochain lancement.",

    # ---- accesso
    "Accesso a Telegram": "Connexion à Telegram",
    "es. 1234567": "ex. 1234567",
    "32 caratteri esadecimali": "32 caractères hexadécimaux",
    "Salva e continua": "Enregistrer et continuer",
    "Telefono:": "Téléphone :",
    "Invia codice": "Envoyer le code",
    "Codice:": "Code :",
    "codice ricevuto nell'app Telegram": "code reçu dans l'application Telegram",
    "Password 2FA:": "Mot de passe 2FA :",
    "solo se hai attivato la verifica in due passaggi": "uniquement si vous avez activé la validation en deux étapes",
    "Accedi": "Se connecter",
    "Benvenuto! Inserisci le chiavi API per iniziare.": "Bienvenue ! Saisissez vos clés API pour commencer.",
    "Connessione a Telegram in corso…": "Connexion à Telegram…",
    "Connessione non riuscita: {error}": "Échec de la connexion : {error}",
    "Connessione non riuscita: {error}. Controlla la rete e premi «Salva e continua».":
        "Échec de la connexion : {error}. Vérifiez le réseau et cliquez sur « Enregistrer et continuer ».",
    "Controlla le chiavi: api_id è un numero, api_hash è lungo 32 caratteri.":
        "Vérifiez les clés : api_id est un nombre, api_hash fait 32 caractères.",
    "Chiavi salvate. Inserisci il numero di telefono con prefisso internazionale.":
        "Clés enregistrées. Saisissez votre numéro de téléphone avec l'indicatif international.",
    "Inserisci il numero di telefono con prefisso internazionale.": "Saisissez votre numéro de téléphone avec l'indicatif international.",
    "Inserisci il numero completo, es. +393331234567.": "Saisissez le numéro complet, ex. +393331234567.",
    "Invio del codice…": "Envoi du code…",
    "Codice inviato: lo trovi nell'app Telegram (chat «Telegram»).": "Code envoyé : vous le trouverez dans l'application Telegram (discussion « Telegram »).",
    "api_id o api_hash non validi: ricontrollali su my.telegram.org.": "api_id ou api_hash non valides : vérifiez-les sur my.telegram.org.",
    "Numero di telefono non valido.": "Numéro de téléphone non valide.",
    "Troppi tentativi: riprova tra {seconds} secondi.": "Trop de tentatives : réessayez dans {seconds} secondes.",
    "Errore: {error}": "Erreur : {error}",
    "Il tuo account ha la verifica in due passaggi: inserisci la password.":
        "Votre compte utilise la validation en deux étapes : saisissez le mot de passe.",
    "Codice errato, riprova.": "Code incorrect, réessayez.",
    "Codice scaduto: premi di nuovo «Invia codice».": "Code expiré : cliquez à nouveau sur « Envoyer le code ».",
    "Password errata.": "Mot de passe incorrect.",
    "Accesso effettuato.": "Connecté.",
    "Disconnesso. Puoi accedere di nuovo quando vuoi.": "Déconnecté. Vous pouvez vous reconnecter quand vous voulez.",

    # ---- pagina principale
    "Connesso come {name}": "Connecté en tant que {name}",
    "Accesso effettuato come {name}": "Connecté en tant que {name}",
    "utente": "utilisateur",
    "Sorgente": "Source",
    "Aggiorna": "Actualiser",
    "Chat recenti:": "Discussions récentes :",
    "https://t.me/… oppure @username": "https://t.me/… ou @username",
    "Se compilato ha la precedenza sulla chat selezionata sopra": "S'il est rempli, il a la priorité sur la discussion sélectionnée ci-dessus",
    "Link / @username:": "Lien / @username :",
    "Destinazione": "Destination",
    "Cartella locale o di rete": "Dossier local ou réseau",
    "Sfoglia…": "Parcourir…",
    "Filtri": "Filtres",
    "Documenti": "Documents",
    "Video": "Vidéos",
    "Immagini": "Images",
    "Archivi": "Archives",
    "Tipi:": "Types :",
    "es. .epub oppure .epub, .mobi": "ex. .epub ou .epub, .mobi",
    "Estensioni:": "Extensions :",
    "Scarico:": "Téléchargement :",
    "solo {extensions}": "uniquement {extensions}",
    "<b>tutti i tipi di file</b> (nessun tipo selezionato)": "<b>tous les types de fichiers</b> (aucun type sélectionné)",
    "nessun limite": "sans limite",
    "da": "de",
    "a": "à",
    "Dimensione:": "Taille :",
    "Opzioni": "Options",
    "Salta se già presente": "Ignorer s'il existe déjà",
    "Rinomina (file_(1).ext)": "Renommer (file_(1).ext)",
    "Sovrascrivi": "Écraser",
    "File già esistenti:": "Fichiers existants :",
    "Per sorgente": "Par source",
    "Per tipo": "Par type",
    "Per data (AAAA-MM)": "Par date (AAAA-MM)",
    "Sottocartelle:": "Sous-dossiers :",
    "Download paralleli:": "Téléchargements parallèles :",
    "Salta i doppioni (stesso file ripubblicato con un altro nome)": "Ignorer les doublons (même fichier republié sous un autre nom)",
    "Notifiche di Windows (fine batch, errori, nuovi file)": "Notifications Windows (fin du lot, erreurs, nouveaux fichiers)",
    "Spegni il PC al termine": "Éteindre le PC à la fin",
    "Avvia download": "Lancer le téléchargement",
    "Pausa": "Pause",
    "Riprendi": "Reprendre",
    "Annulla": "Annuler",
    "Pronto.": "Prêt.",
    "File in corso": "Fichier en cours",
    "Avanzamento": "Progression",
    "Velocità": "Vitesse",
    "Tempo rimanente": "Temps restant",
    "Registro": "Journal",
    "Mostra avvisi (righe gialle: file saltati, tentativi…)": "Afficher les avertissements (lignes jaunes : fichiers ignorés, tentatives…)",
    "— seleziona una chat —": "— sélectionnez une discussion —",
    "Caricamento chat…": "Chargement des discussions…",
    "canale": "canal",
    "gruppo": "groupe",
    "chat": "discussion",
    "senza nome": "sans nom",
    "Caricate {n} chat recenti": "{n} discussions récentes chargées",
    "Telegram chiede di attendere {seconds}s prima di ricaricare le chat": "Telegram demande d'attendre {seconds} s avant de recharger les discussions",
    "Impossibile caricare le chat: {error}": "Impossible de charger les discussions : {error}",
    "Non sei ancora membro di questa chat: unisciti dal client Telegram e riprova.":
        "Vous n'êtes pas encore membre de cette discussion : rejoignez-la depuis Telegram et réessayez.",
    "Il link di invito è scaduto o non valido.": "Le lien d'invitation a expiré ou n'est pas valide.",
    "Sorgente non trovata: {error}": "Source introuvable : {error}",
    "Cartella di destinazione": "Dossier de destination",
    "Sorgente mancante": "Source manquante",
    "Seleziona una chat oppure inserisci un link o @username.": "Sélectionnez une discussion ou saisissez un lien ou un @username.",
    "Destinazione mancante": "Destination manquante",
    "Scegli la cartella in cui salvare i file.": "Choisissez le dossier où enregistrer les fichiers.",
    "Filtro dimensione": "Filtre de taille",
    "La dimensione massima è inferiore alla minima.": "La taille maximale est inférieure à la taille minimale.",
    "Destinazione non valida": "Destination non valide",
    "Impossibile usare la cartella:\n{error}": "Impossible d'utiliser le dossier :\n{error}",
    "Spegnimento automatico": "Arrêt automatique",
    "Al termine dei download il PC verrà spento (con 2 minuti di preavviso). Confermi?":
        "À la fin des téléchargements, le PC sera éteint (avec 2 minutes de préavis). Confirmer ?",
    "Smetto di seguire la chat": "Arrêt du suivi de la discussion",
    "Annullamento in corso… i file parziali verranno ripresi al prossimo avvio": "Annulation en cours… les fichiers partiels reprendront au prochain lancement",
    "Analisi della chat in corso…": "Analyse de la discussion en cours…",
    "tutti i tipi": "tous les types",
    "Avvio batch: «{source}» → {destination} (filtro: {filter})": "Début du lot : « {source} » → {destination} (filtre : {filter})",
    "Errore critico: {error}": "Erreur critique : {error}",
    "Errore durante il download": "Erreur pendant le téléchargement",
    "{completed} scaricati ({size}), {skipped} saltati (di cui {duplicates} doppioni), {failed} non riusciti":
        "{completed} téléchargés ({size}), {skipped} ignorés (dont {duplicates} doublons), {failed} en échec",
    "Annullato.": "Annulé.",
    "Completato.": "Terminé.",
    "Batch terminato: {summary}": "Lot terminé : {summary}",
    "Download completati": "Téléchargements terminés",
    "Download terminati con errori": "Téléchargements terminés avec des erreurs",
    "download completati": "téléchargements terminés",
    "Il PC si spegnerà tra 2 minuti. Per annullare: Win+R → «shutdown /a»": "Le PC s'éteindra dans 2 minutes. Pour annuler : Win+R → « shutdown /a »",
    "Spegnimento automatico non riuscito: {error}": "Échec de l'arrêt automatique : {error}",
    "Nuovi file in arrivo": "Nouveaux fichiers",
    "Analisi completata ({scanned} messaggi, {found} file). Download in corso…": "Analyse terminée ({scanned} messages, {found} fichiers). Téléchargement en cours…",
    "Analisi in corso: {scanned} messaggi letti, {found} file trovati — i download sono già partiti":
        "Analyse en cours : {scanned} messages lus, {found} fichiers trouvés — les téléchargements ont déjà commencé",
    "{done} di {total} file  ·  {done_size} di {total_size}": "{done} sur {total} fichiers  ·  {done_size} sur {total_size}",
    "(in aumento, analisi in corso)": "(en hausse, analyse en cours)",
    "In pausa": "En pause",
    "Attesa limite Telegram": "Attente de la limite Telegram",
    "{speed} MB/s · mancano {eta}": "{speed} Mo/s · reste {eta}",
    "(stima, analisi in corso)": "(estimation, analyse en cours)",
    "{done}/{total} file · {done_size} di {total_size}": "{done}/{total} fichiers · {done_size} sur {total_size}",
    "Limite di Telegram: ripresa automatica tra {time}": "Limite Telegram : reprise automatique dans {time}",

    # ---- motore (registro)
    "Download in pausa": "Téléchargements en pause",
    "Download ripreso": "Téléchargements repris",
    "Download paralleli: {n}": "Téléchargements parallèles : {n}",
    "Durante un download si può cambiare mettendo in pausa": "Pendant un téléchargement, modifiable après avoir mis en pause",
    "Limite di Telegram (FloodWait): pausa di {seconds} secondi": "Limite Telegram (FloodWait) : pause de {seconds} secondes",
    "«{source}»: controllo dei messaggi arrivati dopo l'ultimo visto": "« {source} » : vérification des messages arrivés après le dernier vu",
    "Analisi di «{source}» avviata: i download partono man mano ({n} in parallelo)":
        "Analyse de « {source} » lancée : les téléchargements démarrent au fur et à mesure ({n} en parallèle)",
    "Analisi interrotta ({error}): completo i {n} file già in coda": "Analyse interrompue ({error}) : je termine les {n} fichiers déjà en file",
    "{name}: errore imprevisto, file saltato": "{name} : erreur inattendue, fichier ignoré",
    "Analisi: errore ({error}), riprendo dal messaggio {msg_id} tra {seconds}s": "Analyse : erreur ({error}), reprise au message {msg_id} dans {seconds} s",
    "Analisi completata: {scanned} messaggi, {found} file da scaricare ({size}), {skipped} saltati perché già presenti":
        "Analyse terminée : {scanned} messages, {found} fichiers à télécharger ({size}), {skipped} ignorés car déjà présents",
    "In ascolto di «{source}»: i nuovi file verranno scaricati appena arrivano": "À l'écoute de « {source} » : les nouveaux fichiers seront téléchargés dès leur arrivée",
    "Controllo nuovi messaggi non riuscito ({error}), riprovo più tardi": "Échec de la vérification des nouveaux messages ({error}), nouvel essai plus tard",
    "{n} nuovi file da «{source}»": "{n} nouveaux fichiers de « {source} »",
    "Saltato: {name} — {reason}": "Ignoré : {name} — {reason}",
    "già scaricato in precedenza": "déjà téléchargé auparavant",
    "doppione di «{other}» (già in coda)": "doublon de « {other} » (déjà en file)",
    "doppione di «{other}» già scaricato": "doublon de « {other} », déjà téléchargé",
    "già presente nella cartella": "déjà présent dans le dossier",
    "annullato": "annulé",
    "aggiornamento riferimento non riuscito: {error}": "échec de la mise à jour de la référence : {error}",
    "messaggio non più disponibile": "message plus disponible",
    "{name}: errore ({error}), nuovo tentativo {attempt}/{max} tra {seconds}s": "{name} : erreur ({error}), nouvelle tentative {attempt}/{max} dans {seconds} s",
    "{name}: download non riuscito ({error})": "{name} : échec du téléchargement ({error})",
    "dimensione {actual} diversa da quella attesa {expected}": "taille {actual} différente de celle attendue {expected}",
    "Scartato: {name} — contenuto identico a «{other}»": "Écarté : {name} — contenu identique à « {other} »",
    "Completato: {name} ({size}, SHA-256 {digest}…)": "Terminé : {name} ({size}, SHA-256 {digest}…)",
    "Ripresa di {name} da {size}": "Reprise de {name} à partir de {size}",
    "nessun dato da {seconds} secondi": "aucune donnée depuis {seconds} secondes",

    # ---- scheda «Segui», filtro per nome, guida, uscita dall'account
    "<b>Download</b>: scegli la chat da «Chat recenti» (oppure incolla un link t.me o un @username), la cartella di destinazione e, se vuoi, i filtri: tipi di file, parole contenute nel nome, dimensione. Poi premi «Avvia download».<br><br><b>Segui</b>: aggiungi una o più chat da tenere d'occhio, ognuna con la sua cartella e i suoi filtri. L'app resta in ascolto e scarica i nuovi file appena arrivano, anche dopo un riavvio. Con ■ smetti di seguire una chat, con ⏸ la metti in pausa.<br><br><b>Account</b>: «Esci» in alto a destra scollega questo PC dal tuo account Telegram e, se vuoi, cancella anche le chiavi API.":
        "<b>Téléchargement</b> : choisissez la discussion dans «Discussions récentes» (ou collez un lien t.me ou un @username), le dossier de destination et, si vous le souhaitez, les filtres : types de fichiers, mots contenus dans le nom, taille. Puis appuyez sur «Lancer le téléchargement».<br><br><b>Suivre</b> : ajoutez une ou plusieurs discussions à surveiller, chacune avec son dossier et ses filtres. L'application reste à l'écoute et télécharge les nouveaux fichiers dès leur arrivée, même après un redémarrage. Avec ■ vous arrêtez de suivre une discussion, avec ⏸ vous la mettez en pause.<br><br><b>Compte</b> : «Se déconnecter» en haut à droite déconnecte ce PC de votre compte Telegram et, si vous le souhaitez, supprime aussi les clés API.",
    "Per usare l'app servono le <b>chiavi API</b> personali di Telegram. Non riguardano un canale: servono all'app per entrare nel <i>tuo</i> account. Si creano una volta sola, in pochi minuti:<br><br>1. apri <a href='https://my.telegram.org/apps'>my.telegram.org/apps</a> nel browser e scrivi il tuo numero con prefisso (es. +393331234567);<br>2. Telegram ti manda un codice <b>dentro l'app Telegram</b> (chat «Telegram», non per SMS): scrivilo nel sito;<br>3. compila il modulo «Create new application»: <i>App title</i> e <i>Short name</i> a piacere (il nome breve: 5–32 lettere o numeri), <i>Platform</i> Desktop, il resto può restare vuoto;<br>4. premi «Create application» e copia qui <b>App api_id</b> (un numero) e <b>App api_hash</b> (32 caratteri);<br>5. premi «Salva e continua», poi inserisci il tuo numero: per accedere riceverai un altro codice nell'app Telegram.<br><br>Le chiavi e la sessione restano solo su questo PC, cifrate con il tuo utente Windows. Non condividere mai l'api_hash. Dal secondo avvio l'accesso è automatico.":
        "Pour utiliser l'application, il faut vos <b>clés API</b> personnelles Telegram. Elles ne concernent pas un canal : elles permettent à l'application d'accéder à <i>votre</i> compte. Elles se créent une seule fois, en quelques minutes :<br><br>1. ouvrez <a href='https://my.telegram.org/apps'>my.telegram.org/apps</a> dans le navigateur et saisissez votre numéro avec l'indicatif (ex. +393331234567) ;<br>2. Telegram vous envoie un code <b>dans l'application Telegram</b> (discussion «Telegram», pas par SMS) : saisissez-le sur le site ;<br>3. remplissez le formulaire «Create new application» : <i>App title</i> et <i>Short name</i> au choix (nom court : 5 à 32 lettres ou chiffres), <i>Platform</i> Desktop, le reste peut rester vide ;<br>4. appuyez sur «Create application» et copiez ici <b>App api_id</b> (un nombre) et <b>App api_hash</b> (32 caractères) ;<br>5. appuyez sur «Enregistrer et continuer», puis saisissez votre numéro : pour vous connecter, vous recevrez un autre code dans l'application Telegram.<br><br>Les clés et la session restent uniquement sur ce PC, chiffrées avec votre utilisateur Windows. Ne partagez jamais l'api_hash. À partir du deuxième démarrage, la connexion est automatique.",
    "Aggiunge la chat alla scheda «Segui», con questa cartella e questi filtri:\nl'app scaricherà i nuovi file appena arrivano.":
        "Ajoute la discussion à l'onglet «Suivre», avec ce dossier et ces filtres :\nl'application téléchargera les nouveaux fichiers dès leur arrivée.",
    "Aggiungi chat…":
        "Ajouter une discussion…",
    "Al prossimo accesso dovrai inserirle di nuovo":
        "Vous devrez les saisir à nouveau lors de la prochaine connexion",
    "Analisi: {scanned} messaggi letti, {found} file":
        "Analyse : {scanned} messages lus, {found} fichiers",
    "Avvio…":
        "Démarrage…",
    "Cancella anche le chiavi API (api_id e api_hash) da questo PC":
        "Supprimer aussi les clés API (api_id et api_hash) de ce PC",
    "Chat":
        "Discussion",
    "Chat già seguita":
        "Discussion déjà suivie",
    "Chat non trovata tra le chat recenti: premi «Aggiorna» nella scheda Download":
        "Discussion introuvable parmi les discussions récentes : appuyez sur «Actualiser» dans l'onglet Téléchargement",
    "Chat:":
        "Discussion :",
    "Come si usa":
        "Mode d'emploi",
    "Destinazione:":
        "Destination :",
    "Disconnesso e chiavi API cancellate da questo PC.":
        "Déconnecté et clés API supprimées de ce PC.",
    "Download":
        "Téléchargement",
    "Ferma":
        "Arrêtée",
    "Guida":
        "Guide",
    "I download in corso e le chat seguite verranno fermati.":
        "Les téléchargements en cours et les discussions suivies seront arrêtés.",
    "Impostazioni aggiornate":
        "Paramètres mis à jour",
    "In ascolto":
        "À l'écoute",
    "In attesa: nuovo tentativo tra un minuto":
        "En attente : nouvel essai dans une minute",
    "Le chiavi API":
        "Les clés API",
    "Modifica chat seguita":
        "Modifier la discussion suivie",
    "Modifica…":
        "Modifier…",
    "Nessuna chat attiva: premi ▶ accanto a quelle da seguire.":
        "Aucune discussion active : appuyez sur ▶ à côté de celles à suivre.",
    "Nessuna chat seguita. Premi «Aggiungi chat…» oppure, nella scheda Download, «Segui questa chat…». L'app scaricherà i nuovi file appena arrivano.":
        "Aucune discussion suivie. Appuyez sur «Ajouter une discussion…» ou, dans l'onglet Téléchargement, sur «Suivre cette discussion…». L'application téléchargera les nouveaux fichiers dès leur arrivée.",
    "Nome contiene:":
        "Le nom contient :",
    "Nuovi file":
        "Nouveaux fichiers",
    "Per tutte le chat seguite insieme":
        "Pour toutes les discussions suivies ensemble",
    "Rimuovi":
        "Retirer",
    "Rimuovi chat":
        "Retirer la discussion",
    "Riprendo a seguire {n} chat (recupero dei file arrivati mentre l'app era chiusa)":
        "Reprise du suivi de {n} discussions (récupération des fichiers arrivés pendant que l'application était fermée)",
    "Scarica anche i file già presenti nella chat":
        "Télécharger aussi les fichiers déjà présents dans la discussion",
    "Scarica solo i file che contengono una di queste parole (separate da virgola).\nMaiuscole e accenti non contano. Vuoto = qualsiasi nome.":
        "Télécharge uniquement les fichiers contenant l'un de ces mots (séparés par des virgules).\nMajuscules et accents sont ignorés. Vide = n'importe quel nom.",
    "Scarico {done} di {total} file ({percent}%)":
        "Téléchargement {done} sur {total} fichiers ({percent}%)",
    "Segui":
        "Suivre",
    "Segui ({n})":
        "Suivre ({n})",
    "Segui questa chat…":
        "Suivre cette discussion…",
    "Segui una chat":
        "Suivre une discussion",
    "Senza spunta vengono scaricati solo i file che arrivano da adesso in poi":
        "Si décoché, seuls les fichiers qui arrivent à partir de maintenant sont téléchargés",
    "Smettere di seguire «{source}» e toglierla dall'elenco?\nI file già scaricati restano dove sono.":
        "Ne plus suivre «{source}» et la retirer de la liste ?\nLes fichiers déjà téléchargés restent où ils sont.",
    "Stai seguendo {n} chat. Chiudere comunque?\nAlla riapertura l'app riprenderà da sola, recuperando i file arrivati nel frattempo.":
        "Vous suivez {n} discussions. Fermer quand même ?\nÀ la réouverture, l'application reprendra d'elle-même et récupérera les fichiers arrivés entre-temps.",
    "Stai seguendo {n} chat: i nuovi file vengono scaricati appena arrivano, anche dopo un riavvio dell'app.":
        "Vous suivez {n} discussions : les nouveaux fichiers sont téléchargés dès leur arrivée, même après un redémarrage de l'application.",
    "Stato":
        "État",
    "Ultimo controllo":
        "Dernière vérification",
    "Utile per le foto, che non hanno un nome, e per i canali che descrivono il file nel messaggio":
        "Utile pour les photos, qui n'ont pas de nom, et pour les canaux qui décrivent le fichier dans le message",
    "cerca le parole anche nel testo del messaggio":
        "chercher aussi les mots dans le texte du message",
    "es. fattura oppure preventivo, offerta":
        "ex. facture ou devis, offre",
    "la chat è in download nella scheda Download: riparto quando ha finito":
        "la discussion est en cours de téléchargement dans l'onglet Téléchargement : reprise quand il sera terminé",
    "nome con «{words}»":
        "nom avec «{words}»",
    "«{source}» è già nell'elenco: usa «Modifica…» per cambiarne le impostazioni.":
        "«{source}» est déjà dans la liste : utilisez «Modifier…» pour changer ses paramètres.",
    "«{source}» è già seguita nella scheda «Segui», che ne scarica i file: fermala con ■ se vuoi scaricarla da qui":
        "«{source}» est déjà suivie dans l'onglet «Suivre», qui télécharge ses fichiers : arrêtez-la avec ■ si vous voulez la télécharger d'ici",

    # ---- scheda «Segui»: pulsanti Ferma, ripresa graduale dei sospesi
    "Analisi: Telegram chiede di rallentare, riprendo tra {seconds}s (i download continuano)":
        "Analyse : Telegram demande de ralentir, reprise dans {seconds}s (les téléchargements continuent)",
    "Ferma tutte":
        "Tout arrêter",
    "Ripresa dei file in sospeso interrotta ({error}): riprovo al prossimo avvio":
        "Reprise des fichiers en attente interrompue ({error}) : nouvel essai au prochain démarrage",
    "Smetto di seguire tutte le chat":
        "Arrêt du suivi de toutes les discussions",
    "{n} file rimasti in sospeso dall'ultima volta: li rimetto in coda poco alla volta":
        "{n} fichiers restés en attente depuis la dernière fois : je les remets en file petit à petit",

    # ---- conferma alla chiusura
    "Chiedi conferma alla chiusura se ci sono download in corso":
        "Demander confirmation à la fermeture si des téléchargements sont en cours",
    "Chiudi":
        "Fermer",
    "Conferma":
        "Confirmer",
    "Non chiedere più (si riattiva dal menu Visualizza)":
        "Ne plus demander (réactivable depuis le menu Affichage)",

    # ---- scheda «Segui»: pausa e avvio per chat
    "Avvia tutte":
        "Tout lancer",
    "Pausa: si ferma un momento, senza smettere di seguire la chat":
        "Pause : s'arrête un moment, sans cesser de suivre la discussion",
    "Ferma: smette di seguire la chat (anche ai prossimi avvii)":
        "Arrêter : ne suit plus la discussion (même aux prochains démarrages)",
    "Avvia: segue la chat e scarica i nuovi file":
        "Lancer : suit la discussion et télécharge les nouveaux fichiers",

    # ---- scheda «Segui»: file sospesi ancora da riprendere
    "Scarico {done} di {total} file ({percent}%) · il totale cresce: altri {left} file in sospeso da riprendere":
        "Téléchargement {done} sur {total} fichiers ({percent}%) · le total augmente : encore {left} fichiers en attente à reprendre",
    "il totale cresce: altri {left} file in sospeso da riprendere":
        "le total augmente : encore {left} fichiers en attente à reprendre",

    # ---- scheda «Segui»: ricontrolla da capo, opzioni dei file esistenti
    "Applicare i nuovi filtri anche ai messaggi già arrivati in «{source}»?\nL'app rilegge la chat dall'inizio e scarica i file che ora corrispondono; quelli già scaricati vengono saltati.":
        "Appliquer les nouveaux filtres aussi aux messages déjà arrivés dans «{source}» ?\nL'application relit la discussion depuis le début et télécharge les fichiers qui correspondent maintenant ; ceux déjà téléchargés sont ignorés.",
    "Avvia":
        "Lancer",
    "Filtri cambiati":
        "Filtres modifiés",
    "Ricontrolla":
        "Revérifier",
    "Ricontrolla da capo":
        "Revérifier depuis le début",
    "Ricontrolla da capo…":
        "Revérifier depuis le début…",
    "Ricontrollo la chat da capo":
        "Revérification de la discussion depuis le début",
    "Rilegge tutta la chat dall'inizio e scarica i file che mancano\n(o tutti, se la chat è impostata per sovrascrivere i file già esistenti)":
        "Relit toute la discussion depuis le début et télécharge les fichiers manquants\n(ou tous, si la discussion est réglée pour écraser les fichiers existants)",
    "Rileggo tutta «{source}» dall'inizio e riscarico TUTTI i file che corrispondono ai filtri, sovrascrivendo quelli già presenti nella cartella.\nSu una chat grande può richiedere molto tempo.":
        "Je relis tout «{source}» depuis le début et retélécharge TOUS les fichiers qui correspondent aux filtres, en écrasant ceux déjà présents dans le dossier.\nSur une grande discussion, cela peut prendre beaucoup de temps.",
    "Rileggo tutta «{source}» dall'inizio e scarico solo i file che mancano: quelli cancellati o spostati dalla cartella e quelli che rientrano nei filtri ma non erano stati scaricati.\nI file già presenti vengono saltati. Su una chat grande la lettura richiede qualche minuto.":
        "Je relis tout «{source}» depuis le début et télécharge seulement les fichiers manquants : ceux supprimés ou déplacés du dossier et ceux qui correspondent aux filtres mais n'avaient pas été téléchargés.\nLes fichiers déjà présents sont ignorés. Sur une grande discussion, la lecture prend quelques minutes.",
    "Solo ai messaggi nuovi":
        "Seulement aux nouveaux messages",
    "Sì, ricontrolla la chat":
        "Oui, revérifier la discussion",
}
