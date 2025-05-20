# SmileAdventure - Serious Game Project

Sistema interattivo per aiutare i bambini nella regolazione delle emozioni, con focus particolare sulla rabbia.

## Struttura del Progetto

Il progetto è strutturato come segue:

```
smile-adventure-project/
├── .vscode/                      # Impostazioni specifiche di VS Code (opzionale)
├── docs/                         # Documentazione del progetto
│   ├── architecture.md
│   ├── requirements_guide.md
│   └── api_contracts/
│       ├── auth_api.yaml
│       └── users_api.yaml
├── microservices/                # Microservizi backend
│   ├── Users/                    # Gestione utenti (FastAPI)
│   ├── Reports/                  # Gestione report (FastAPI)
│   ├── Auth/                     # Gestione autenticazione (FastAPI)
│   └── API-GATEWAY/              # API Gateway
├── frontend/                     # Applicazioni client
│   ├── docker-react/             # Web App per genitori/professionisti (React)
│   └── react-native-app/         # App Mobile per bambini
├── unity-smile-adventure/        # Progetto Unity del serious game
├── scripts/                      # Script di utilità e setup
├── docker-compose.yml            # Docker Compose per orchestrare i servizi
└── README.md                     # Questo file
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

### Mobile App (React Native)

```bash
cd frontend/react-native-app
npm install
npx react-native start
```

### Unity

Aprire il progetto nella cartella `unity-smile-adventure` con Unity Editor.

## Licenza

Questo progetto è sotto licenza [MIT](/LICENSE)