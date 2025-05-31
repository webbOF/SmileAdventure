# Utilizza una base image snella di Python 3.9
FROM python:3.9-slim

# Imposta la working directory all'interno del container
WORKDIR /app

# Copia il file requirements.txt nella working directory
COPY requirements.txt .

# Installa le dipendenze di sistema necessarie per pygraphviz e le dipendenze Python
RUN apt-get update && apt-get install -y \
    g++ \
    gcc \
    graphviz \
    graphviz-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir -r requirements.txt

# Copia l'intero contenuto del progetto nella working directory
COPY . .

# Documenta la porta su cui l'applicazione ascolterà
EXPOSE 8006

# Comando di avvio: esegue Uvicorn per avviare l'applicazione FastAPI con reload per sviluppo
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8006", "--reload"]
