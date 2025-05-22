# SmileAdventure - Serious Game Project

Sistema interattivo per aiutare i bambini 
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
- [Python 3.11+](https://www.python.org/downloads/) (per sviluppo backend)
- [Unity](https://unity.com/download) (per sviluppo del gioco)

### Avvio in modalità sviluppo

1. Clona il repository
```bash
git clone https://github.com/yourusername/smile-adventure-project.git
cd smile-adventure-project
```

2. Copia e configura i file .env (presumendo che i file .env.example esistano in queste posizioni)
```bash
cp microservices/Users/.env.example microservices/Users/.env
cp microservices/Auth/.env.example microservices/Auth/.env
cp microservices/Reports/.env.example microservices/Reports/.env
cp microservices/API-GATEWAY/.env.example microservices/API-GATEWAY/.env
```

3. Avvia i servizi con Docker Compose
```bash
docker-compose up -d
```

4. I servizi saranno disponibili ai seguenti indirizzi:
   - Web App: http://localhost:3000
   - API Gateway: http://localhost:8000
   - Servizio utenti: http://localhost:8001 (verificare porta in docker-compose.yml)
   - Servizio auth: http://localhost:8002 (verificare porta in docker-compose.yml)
   - Servizio reports: http://localhost:8003 (verificare porta in docker-compose.yml)

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
