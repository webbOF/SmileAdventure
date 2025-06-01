# Guida ai Requisiti - SmileAdventure

## Panoramica del Progetto

SmileAdventure è un serious game progettato per supportare i bambini con difficoltà nella regolazione delle emozioni, in particolare concentrandosi sul riconoscimento e la gestione della rabbia. Il sistema offre:

- Un'applicazione di gioco coinvolgente per i bambini
- Strumenti di monitoraggio e valutazione per genitori e professionisti
- Un approccio basato su evidenze scientifiche nel campo della psicologia infantile

## Requisiti Funzionali

### 1. Microservizio Utenti (`service-users`)

- Registrazione e autenticazione utenti (bambini, genitori, professionisti)
- Gestione profili con diversi livelli di accesso
- Associazione bambino-genitore e bambino-professionista
- API per recuperare informazioni sui profili utente

### 2. Microservizio Report (`service-reports`)

- Raccolta dati sulle performance di gioco
- Generazione report di progresso personalizzati
- Analisi dei pattern emotivi basati sul comportamento nel gioco
- Dashboard per la visualizzazione dei progressi

### 3. Microservizio Autenticazione (`service-auth`)

- Gestione token di autenticazione JWT
- Gestione delle sessioni utente
- Autorizzazione basata su ruoli
- Processo di reset password

### 4. API Gateway

- Routing delle richieste ai microservizi appropriati
- Rate limiting per prevenire abusi
- Logging delle richieste per scopi di debug
- Gestione degli errori centralizzata

### 5. Web App per Genitori/Professionisti

- Dashboard personalizzata con statistiche e progressi
- Visualizzazione dei report generati
- Configurazione delle impostazioni del gioco per i bambini
- Comunicazione tra genitori e professionisti

### 6. Mobile App per Bambini

- Interfaccia semplice e intuitiva adatta ai bambini
- Integrazione del gioco Unity
- Meccanismi di feedback emotivo immediato
- Esercizi di respirazione e rilassamento

### 7. Unity Game

- Mini-giochi focalizzati sul riconoscimento delle emozioni
- Meccaniche di gioco che insegnano strategie di coping
- Sistema di ricompense e progressione adattivo
- Elementi narrativi che promuovono l'empatia

## Requisiti Non Funzionali

### 1. Sicurezza
- Protezione dei dati personali conforme a GDPR
- Comunicazioni criptate (HTTPS)
- Autenticazione robusta

### 2. Prestazioni
- Tempo di risposta < 2 secondi per le API
- Supporto per almeno 1000 utenti concorrenti
- Efficienza nell'uso della batteria sul dispositivo mobile

### 3. Usabilità
- Interfaccia adatta ai bambini dai 6 anni in su
- Accessibilità per utenti con diverse abilità
- Supporto multilingua (inizialmente italiano e inglese)

### 4. Scalabilità
- Architettura che permette la facile aggiunta di nuovi microservizi
- Possibilità di scalare orizzontalmente in base al carico

### 5. Manutenibilità
- Documentazione completa del codice
- Test automatici con copertura > 80%
- CI/CD pipeline per deployment continuo

## Stack Tecnologico

- **Backend**: FastAPI (Python) per i microservizi
- **Database**: PostgreSQL
- **Web Frontend**: React.js
- **Mobile App**: Export Unity for Android
- **Game Engine**: Unity
- **Containerizzazione**: Docker, Docker Compose
- **CI/CD**: GitHub Actions
