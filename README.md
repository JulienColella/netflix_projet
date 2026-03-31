# 🎬 CinéAPI — Backend façon Netflix

Bienvenue dans ce projet fil rouge ! Tu vas construire de A à Z un backend de streaming de films, inspiré de Netflix, en utilisant **FastAPI** et **SQLite**.

---

## 🗺️ Vue d'ensemble

| Séance | Thème | Objectifs |
|--------|-------|-----------|
| 1 | Fondations | Premiers endpoints, design de la base de données |
| 2 | Fonctionnalités | Visualisation, comptes utilisateurs |
| 3 | Cybersécurité | Sécurisation de l'API + évaluation orale |

---

## 🛠️ Stack technique

- **Python 3.11+**
- **FastAPI** — framework web moderne et rapide
- **SQLite** — base de données légère, fichier local
- **Raw SQL** avec le module `sqlite3` de Python

---

## ⚙️ Installation

```bash
# Cloner le dépôt
git clone <url-du-repo>
cd cineapi

# Créer un environnement virtuel
python -m venv .venv
source .venv/bin/activate  # Windows : .venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Lancer le serveur
fastapi dev main.py
```

L'API est accessible sur `http://localhost:8000`  
La documentation interactive est disponible sur `http://localhost:8000/docs`

---

## 📅 Séance 1 — Fondations : endpoints & base de données

### Objectifs
- Comprendre la structure d'un projet FastAPI
- Concevoir le schéma de la base de données ensemble
- Implémenter les premiers endpoints CRUD

### Ce qu'on construit
- Schéma de la BDD : tables `films`, `genres`, `utilisateurs`, `visionnages`
- `GET /films` — lister tous les films
- `GET /films/{id}` — détail d'un film
- `POST /films` — ajouter un film
- `DELETE /films/{id}` — supprimer un film

### Notions abordées
- Structure d'un projet FastAPI (`main.py`, routeurs, schémas Pydantic)
- Méthodes HTTP et codes de statut (200, 201, 404…)
- Modélisation relationnelle (clés primaires, clés étrangères)

---

## 📅 Séance 2 — Visualisation & comptes utilisateurs

### Objectifs
- Gérer les utilisateurs et l'authentification de base
- Enregistrer et consulter l'historique de visionnage
- Explorer des endpoints de statistiques

### Ce qu'on construit
- `POST /utilisateurs` — créer un compte
- `GET /utilisateurs/{id}/historique` — films vus par un utilisateur
- `POST /visionnages` — enregistrer un visionnage
- `GET /films/populaires` — films les plus regardés
- `GET /genres/{id}/films` — films par genre

### Notions abordées
- Relations many-to-many en SQL
- Requêtes avec jointures et agrégations (`COUNT`, `GROUP BY`)
- Utilisation du module `sqlite3` : `cursor`, `fetchall`, `fetchone`
- Hashage des mots de passe (`bcrypt`)

---

## 📅 Séance 3 — Cybersécurité & évaluation

### Objectifs
- Comprendre les principales vulnérabilités d'une API REST
- Présenter et défendre son travail à l'oral

### Ce qu'on construit
- Middleware de rate limiting sur les endpoints sensibles
- Retour d'erreurs `429 Too Many Requests`
- Stratégies de limitation : par IP, par utilisateur

### Notions abordées
- Rate limiting : pourquoi et comment (attaques par force brute, DDoS applicatif)
- Implémentation maison : compteur de requêtes en mémoire (`dict`, timestamps)

### 🎤 Évaluation orale
Chaque étudiant présente **son code** et des questions seront posées

## 📚 Ressources utiles

- [Documentation FastAPI](https://fastapi.tiangolo.com)
- [SQLite Browser](https://sqlitebrowser.org) — visualiser ta BDD

---

*Bon courage ! 🚀*
