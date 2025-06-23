# Backend - API Utilisateurs

## Prérequis

- Python 3.11+
- Docker & Docker Compose
- Accès à un terminal
- (Optionnel) MySQL local si vous ne souhaitez pas utiliser Docker

## Installation & Lancement

### 1. Cloner le dépôt

```bash
git clone <repo-url>
cd Backend
```

### 2. Variables d'environnement

Créez un fichier `.env` à la racine du dossier `Backend` (exemple de variables par défaut) :

```
SECRET_KEY=une_clé_secrète
MYSQL_HOST=mysql
MYSQL_USER=admin
MYSQL_PASSWORD=password
MYSQL_DATABASE=users_db
```

### 3. Lancer avec Docker

```bash
docker compose up --build
```

- L’API sera disponible sur `http://localhost:8000`
- MySQL sur le port `3306`
- PhpMyAdmin sur `http://localhost:8081`

### 4. Lancer en local (hors Docker)

Installez les dépendances Python :

```bash
pip install -r requirements.txt
```

Lancez le serveur :

```bash
python hello.py
```

⚠️ Assurez-vous que MySQL tourne et que les variables d’environnement sont correctes.

### 5. Initialisation de la base

Les scripts SQL d’initialisation sont dans `mysql_data/`.

---

## Tests

Ce projet utilise `pytest` pour les tests unitaires et d'intégration. Les tests couvrent les principaux endpoints de l'API et les cas d'erreur courants.

### Liste des tests existants

- **test_health_check** : Vérifie que l'endpoint `/health` répond correctement (statut 200, message 'healthy').
- **test_create_user** : Teste la création d'un utilisateur avec des données valides.
- **test_get_users** : Vérifie que la récupération de la liste des utilisateurs fonctionne.
- **test_delete_user_unauthorized** : Vérifie qu'une suppression sans authentification renvoie une erreur 401.
- **test_get_user_unauthorized** : Vérifie qu'une récupération d'utilisateur sans authentification renvoie une erreur 401.
- **test_admin_login** : Teste la connexion d'un administrateur (succès ou échec selon les credentials).
- **test_create_user_missing_fields** : Vérifie la gestion d'un utilisateur créé sans mot de passe (erreur 400).
- **test_create_user_weak_password** : Vérifie la gestion d'un mot de passe trop faible (erreur 400).
- **test_create_user_duplicate_email** : Vérifie la gestion d'un email déjà existant (erreur 409).
- **test_login_missing_fields** : Vérifie la gestion d'une tentative de login sans tous les champs requis (erreur 400).
- **test_login_invalid_credentials** : Vérifie la gestion d'un login avec de mauvais identifiants (erreur 401).
- **test_create_admin_unauthorized** : Vérifie qu'on ne peut pas créer d'admin sans authentification (erreur 401).
- **test_create_admin_missing_fields** : Vérifie la gestion d'une création d'admin avec des champs manquants (erreur 400 ou 401).
- **test_get_user_not_found** : Vérifie la gestion de la récupération d'un utilisateur inexistant (erreur 401 ou 404).
- **test_delete_user_not_found** : Vérifie la gestion de la suppression d'un utilisateur inexistant (erreur 401 ou 404).

Pour lancer tous les tests :

```bash
pytest
```

---

## Développement

- Le code principal est dans `hello.py`
- Les middlewares sont dans `middleware.py`
- Les tests sont dans `test_hello.py`
- Les dépendances sont dans `requirements.txt`
- Le build Docker est dans `Dockerfile` et `docker-compose.yml`

---
## Déploiement

Le déploiement est automatisé lors du push d'un tag, l'application est déployé sur ce lien : https://vercel.com/hugogoncalves06s-projects/integration-continue-backend

---
## TODOs techniques

- Améliorer les chemins & middlewares
- Intégrer Pytest + Codecov
- Ajouter des tags sur l’image Docker
- Scanner l’image Docker avec Trivy et sauvegarder en artefacts
