Autenticazione alternativa (attach)

Questa integrazione ora supporta un flusso alternativo di autenticazione "attach" dove si possono fornire esplicitamente le credenziali del gateway.

Come usare via UI di Home Assistant:
- Durante la configurazione dell'integrazione, nella schermata "Manual" verranno mostrati i campi standard (Gateway Name, Gateway IP Address, Gateway Device ID, Setup Code).
- Sono ora disponibili campi opzionali: username, useruid, password.
- Inserire username/useruid/password se si vuole eseguire l'associazione direttamente con credenziali esistenti.

Cosa succede internamente:
- Se username e password sono forniti, le credenziali vengono salvate localmente (DB per gateway) e verranno usate dalla fase "attach" per inviare il payload al gateway.
- I campi sensibili non vengono salvati nella ConfigEntry (rimossi prima di creare la voce di configurazione).

Note di sicurezza:
- Le credenziali vengono memorizzate localmente nel DB del componente. Assicurarsi che il sistema sia protetto.
- Evitare di committare credenziali in repo pubblici.

Se serve, posso aggiungere istruzioni per caricare queste credenziali via YAML o endpoint API personalizzato.