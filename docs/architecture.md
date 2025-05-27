# Sistema Architetturale SmileAdventure

## Panoramica dell'architettura

Il sistema SmileAdventure è basato su un'architettura a microservizi che comprende:

1.  **Microservizi Backend (Python/FastAPI)**:
    *   `auth-service`: Gestione autenticazione (JWT), registrazione utenti.
    *   `users-service`: Gestione profili utente (genitori, professionisti), dettagli professionali, ricerche.
    *   `reports-service`: Gestione e analisi dei dati delle sessioni di gioco, generazione report.
    *   `api-gateway`: Punto di ingresso unico per tutte le richieste client, routing verso i microservizi appropriati, aggregazione di risposte (se necessario).

2.  **Database Unificato**:
    *   Un singolo database **PostgreSQL** centralizzato, utilizzato da tutti i microservizi. Ogni microservizio potrebbe gestire il proprio schema o tabelle specifiche all'interno di questo database.

3.  **Applicazioni Frontend**:
    *   **Web Application (React)**: Interfaccia per genitori e professionisti per la gestione degli account, visualizzazione dei report, ricerca professionisti, ecc.
    *   **Gioco Mobile (Unity)**: Applicazione Android per bambini, focalizzata sul gioco per la regolazione delle emozioni. Comunica con il backend tramite l'API Gateway.

4.  **Servizi di Supporto (gestiti con Docker Compose)**:
    *   `postgres-db`: Il servizio database PostgreSQL.
    *   `db-init`: Un servizio one-shot per inizializzare le tabelle del database al primo avvio, eseguendo script Python.
    *   `er-diagrams`: Un servizio one-shot per generare diagrammi ER (opzionale, per documentazione).

## Diagramma dell'architettura

```mermaid
graph TD
    WebApp[Web App React<br>(Genitori/Professionisti)] --> APIGateway
    MobileApp[Gioco Mobile Unity<br>(Bambini)] --> APIGateway

    subgraph Backend Microservices
        APIGateway(API Gateway) --> AuthService[Auth Service]
        APIGateway --> UsersService[Users Service]
        APIGateway --> ReportsService[Reports Service]
    end

    AuthService --> PostgresDB[(PostgreSQL Database)]
    UsersService --> PostgresDB
    ReportsService --> PostgresDB

    subgraph Support Services (Docker)
        DBInit[DB Init Script] -.-> PostgresDB
        ERDiagrams[ER Diagram Gen Script] -.-> PostgresDB
    end

    style WebApp fill:#f9f,stroke:#333,stroke-width:2px
    style MobileApp fill:#f9f,stroke:#333,stroke-width:2px
    style APIGateway fill:#ccf,stroke:#333,stroke-width:2px
    style AuthService fill:#cdf,stroke:#333,stroke-width:2px
    style UsersService fill:#cdf,stroke:#333,stroke-width:2px
    style ReportsService fill:#cdf,stroke:#333,stroke-width:2px
    style PostgresDB fill:#dbf,stroke:#333,stroke-width:4px
    style DBInit fill:#eee,stroke:#333,stroke-width:1px
    style ERDiagrams fill:#eee,stroke:#333,stroke-width:1px
```
*Diagramma aggiornato per riflettere PostgreSQL come database centrale e i servizi di supporto.* 

## Flusso di comunicazione

1.  Le richieste dalle applicazioni client (Web React, Mobile Unity) arrivano all'**API Gateway**.
2.  L'API Gateway autentica la richiesta (potenzialmente interagendo con `auth-service` per validare i token JWT) e la instrada al microservizio backend appropriato (`auth-service`, `users-service`, `reports-service`).
3.  Ciascun microservizio esegue la logica di business specifica, interagendo con il database **PostgreSQL** per la persistenza dei dati.
4.  I microservizi possono comunicare tra loro tramite chiamate HTTP dirette (meno preferibile, aumenta l'accoppiamento) o, idealmente, tramite l'API Gateway o un message broker (non attualmente in scope) se è richiesta una comunicazione asincrona o disaccoppiata.

## Database

Si è passati da database SQLite individuali per microservizio a un **singolo database PostgreSQL centralizzato**. 
- **Vantaggi**: Semplifica la gestione, il backup, e le query cross-servizio (sebbene queste ultime dovrebbero essere minimizzate in un'architettura a microservizi pura). Facilita l'uso di tool di amministrazione DB standard.
- **Considerazioni**: Ogni servizio è responsabile della gestione del proprio schema (set di tabelle) all'interno del database condiviso. È importante evitare conflitti di nomi di tabelle e gestire le migrazioni dello schema con attenzione (es. usando Alembic per ogni servizio che gestisce una porzione dello schema).
- Le credenziali e l'URL di connessione sono forniti ai microservizi e al servizio `db-init` tramite variabili d'ambiente gestite da Docker Compose e un file `.env`.

## Considerazioni sulla scalabilità

- Ogni microservizio può essere scalato indipendentemente in base al carico
- Deployment containerizzato tramite Docker per facilitare la gestione dell'infrastruttura
- Possibilità di implementare load balancing per distribuire il traffico

## Sicurezza

- Autenticazione centralizzata mediante JWT tokens gestiti da service-auth
- HTTPS per tutte le comunicazioni client-server
- Policy di autorizzazione per controllare l'accesso alle risorse
