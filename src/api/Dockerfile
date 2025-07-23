FROM python:3.12-slim AS builder

# Définir la variable d'environnement pour désactiver les .pyc
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc \
    && rm -rf /var/lib/apt/lists/*

# Créer le répertoire de travail
WORKDIR /app

# Copier uniquement les fichiers nécessaires à l'installation des dépendances
COPY requirements.txt .


# Installer les dépendances dans un dossier séparé (pour un build optimisé)
RUN pip install --upgrade pip \
    && pip install --prefix=/install -r requirements.txt


# Installer les dépendances dans un dossier séparé (pour un build optimisé)
RUN pip install --upgrade pip \
    && pip install --prefix=/install -r requirements.txt

# Étape 2 : Runner
FROM python:3.12-slim

# Variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Installer les dépendances système minimales
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

# Créer le répertoire de travail
WORKDIR /app

# Copier les dépendances Python depuis le builder
COPY --from=builder /install /usr/local

# Copier le reste du projet
COPY . .

# Exposer le port (par défaut FastAPI tourne sur 8000)
EXPOSE 8000

# Commande pour démarrer l'application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
