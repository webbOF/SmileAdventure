# SmileAdventure - Serious Game Project

Sistema interattivo per aiutare i bambini nella regolazione delle emozioni, con focus particolare sulla rabbia.

## Struttura del Progetto

```
SeriousGame/
├── docker-compose.yml          # Configurazione Docker Compose per l'intero stack
├── README.md                   # Questo file
├── docs/                       # Documentazione del progetto
│   ├── architecture.md         # Dettagli sull'architettura del sistema
│   ├── requirements_guide.md   # Guida ai requisiti funzionali e non funzionali
│   └── api_contracts/          # Contratti API (OpenAPI/Swagger)
│       ├── auth_api.yaml
│       └── users_api.yaml
├── frontend/                   # Codice sorgente per le interfacce utente
│   ├── docker-react/           # Web App React per utenti e professionisti
│   └── unity-smile-adventure/  # Gioco Android per bambini sviluppato in Unity
├── microservices/              # Backend microservizi
│   ├── API-GATEWAY/            # API Gateway (es. Kong, Ocelot, o custom Flask/FastAPI)
│   ├── Auth/                   # Servizio di Autenticazione
│   ├── Users/                  # Servizio Utenti
│   └── Reports/                # Servizio Reportistica (da definire)
├── scripts/                    # Script utili (inizializzazione DB, generazione dati, etc.)
│   ├── db_init.py              # Script per inizializzare i database
│   ├── seeds_gen.py            # Script per generare dati di seed
│   ├── er_model.py             # Script per il modello di riconoscimento delle emozioni (da definire)
│   └── requirements.txt        # Dipendenze Python per gli script
└── ...                         # Altri file e cartelle di configurazione (es. .env, config)
```

## Getting Started

### Prerequisiti

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)
- [Node.js](https://nodejs.org/) (per sviluppo frontend)
- [Python 3.11+](https://www.python.org/downloads/) (per sviluppo backend e script)
- [Unity](https://unity.com/download) (per sviluppo del gioco)
- Un client PostgreSQL (opzionale, per ispezionare il database, es. DBeaver, pgAdmin)

### Avvio in modalità sviluppo

1. Clona il repository
```bash
git clone https://github.com/yourusername/smile-adventure-project.git
cd smile-adventure-project
```

2. Crea il file `.env` nella root del progetto.
   Copia il contenuto da `.env.example` (se fornito, altrimenti crealo basandoti sulle variabili usate in `docker-compose.yml`):
   ```env
   # Esempio di .env (da creare nella root del progetto)
   POSTGRES_USER=smileadventureuser
   POSTGRES_PASSWORD=smileadventurepass # Scegli una password sicura!
   POSTGRES_DB=smileadventure
   JWT_SECRET_KEY=yoursecretkey # Scegli una chiave segreta sicura e complessa!
   ```
   **Importante:** Aggiungi `.env` al tuo file `.gitignore` per non commettere le credenziali.

3. Avvia i servizi con Docker Compose
   Assicurati che Docker Desktop sia in esecuzione.
```bash
docker-compose up -d --build
```
   Il flag `--build` è raccomandato la prima volta o dopo modifiche ai Dockerfile.

4. I servizi saranno disponibili ai seguenti indirizzi (le porte potrebbero variare in base a `docker-compose.yml`):
   - Web App React: http://localhost:3000
   - API Gateway: http://localhost:8000
   - Servizio Auth: http://localhost:8001 (punto di accesso interno `http://auth-service:8001`)
   - Servizio Users: http://localhost:8006 (punto di accesso interno `http://users-service:8006`)
   - Servizio Reports: http://localhost:8007 (punto di accesso interno `http://reports-service:8007`)
   - Database PostgreSQL: accessibile sulla porta `5432` (se esposta in `docker-compose.yml`)

## Database

Il sistema utilizza un database PostgreSQL centralizzato per tutti i microservizi.
- Le credenziali e la configurazione del database sono gestite tramite il file `.env` nella root del progetto e lette da `docker-compose.yml`.
- Gli script `scripts/db_init.py` e `scripts/seeds_gen.py` (eseguiti dal servizio `db-init` in Docker Compose) si occupano di creare le tabelle necessarie al primo avvio, utilizzando le connessioni PostgreSQL definite nei rispettivi microservizi.

## Sviluppo

### Backend (FastAPI)

Ogni microservizio è sviluppato con FastAPI. Per sviluppare localmente (esempio per il servizio Utenti):

```bash
cd microservices/Users
python -m venv venv
source venv/bin/activate  # o "venv\Scripts\activate" su Windows
pip install -r requirements.txt
uvicorn src.main:app --reload # Assumendo che main.py sia in una sottocartella src
```

### Frontend Web (React)

```bash
cd frontend/docker-react
npm install
npm start
```


### Unity

Aprire il progetto nella cartella `unity-smile-adventure` con Unity Editor.

## Licenza

Questo progetto è sotto licenza [MIT](/LICENSE)