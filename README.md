# SmileAdventure - Serious Game Project

Sistema interattivo per aiutare i bambini nella regolazione delle emozioni, con focus particolare sulla rabbia.

## Struttura del Progetto

Il progetto è strutturato come segue:

```
smile-adventure-project/
├── .vscode/                      # Impostazioni specifiche di VS Code
├── docs/                         # Documentazione del progetto
├── microservices/                # Microservizi backend
│   ├── service-users/            # Gestione utenti (FastAPI)
│   ├── service-reports/          # Gestione report (FastAPI)
│   ├── service-auth/             # Gestione autenticazione (FastAPI)
│   └── api-gateway/              # API Gateway
├── frontend/                     # Applicazioni client
│   ├── react-web-app/            # Web App per genitori/professionisti
│   └── react-native-app/         # App Mobile per bambini
├── unity-smile-adventure/        # Progetto Unity del serious game
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

2. Copia e configura i file .env
```bash
cp microservices/service-users/.env.example microservices/service-users/.env
cp microservices/service-auth/.env.example microservices/service-auth/.env
cp microservices/service-reports/.env.example microservices/service-reports/.env
cp microservices/api-gateway/.env.example microservices/api-gateway/.env
```

3. Avvia i servizi con Docker Compose
```bash
docker-compose up -d
```

4. I servizi saranno disponibili ai seguenti indirizzi:
   - Web App: http://localhost:3000
   - API Gateway: http://localhost:8000
   - Servizio utenti: http://localhost:8001
   - Servizio auth: http://localhost:8002
   - Servizio reports: http://localhost:8003

## Sviluppo

### Backend (FastAPI)

Ogni microservizio è sviluppato con FastAPI. Per sviluppare localmente:

```bash
cd microservices/service-users
python -m venv venv
source venv/bin/activate  # o "venv\Scripts\activate" su Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Web (React)

```bash
cd frontend/react-web-app
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