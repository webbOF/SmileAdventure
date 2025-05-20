# Sistema Architetturale SmileAdventure

## Panoramica dell'architettura

Il sistema SmileAdventure è basato su un'architettura a microservizi che comprende:

1. **Microservizi Backend**:
   - `service-users`: Gestione utenti e profili
   - `service-reports`: Generazione e gestione dei report di progresso
   - `service-auth`: Gestione autenticazione e autorizzazione
   - `api-gateway`: Orchestrazione e routing delle richieste verso i vari microservizi

2. **Frontend Applications**:
   - Web Application React per genitori e professionisti
   - Mobile Application React Native per i bambini

3. **Componente di Gioco**:
   - Unity Game integrato nell'applicazione mobile

## Diagramma dell'architettura

```
┌─────────────────────┐     ┌───────────────────────┐
│ Web App (React)     │     │ Mobile App (React     │
│ (Genitori/Esperti)  │     │ Native + Unity)       │
└──────────┬──────────┘     └───────────┬───────────┘
           │                            │
           ▼                            ▼
┌─────────────────────────────────────────────────────┐
│                    API Gateway                      │
└───────┬───────────────┬────────────────┬───────────┘
        │               │                │
┌───────▼────────┐ ┌────▼─────┐    ┌─────▼───────┐
│ Service-Users  │ │ Service- │    │ Service-Auth │
│                │ │ Reports  │    │              │
└───────┬────────┘ └────┬─────┘    └──────────────┘
        │               │
        ▼               ▼
┌─────────────────────────────┐
│     Database PostgreSQL     │
└─────────────────────────────┘
```

## Flusso di comunicazione

1. Tutte le richieste client passano attraverso l'API Gateway
2. L'API Gateway instrada le richieste ai microservizi appropriati
3. Ciascun microservizio è responsabile per una specifica funzionalità
4. I dati persistenti vengono memorizzati nel database PostgreSQL
5. I microservizi comunicano tra loro quando necessario tramite API REST

## Considerazioni sulla scalabilità

- Ogni microservizio può essere scalato indipendentemente in base al carico
- Deployment containerizzato tramite Docker per facilitare la gestione dell'infrastruttura
- Possibilità di implementare load balancing per distribuire il traffico

## Sicurezza

- Autenticazione centralizzata mediante JWT tokens gestiti da service-auth
- HTTPS per tutte le comunicazioni client-server
- Policy di autorizzazione per controllare l'accesso alle risorse
