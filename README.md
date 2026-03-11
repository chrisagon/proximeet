# PROXIMEET 🍽️

Application pour faciliter l'organisation de déjeuners entre consultants travaillant sur le même site client.

## 🚀 Fonctionnalités

- **Partage de présence éphémère** : Position expire après 6h
- **Mode confidentialité** : PRECISE ou BUBBLE (zone approximative)
- **Recherche de proximité** : Trouver des collègues dans un rayon de 1-5 km
- **Recommandations de restaurants** : Noter et partager les bonnes adresses
- **Organisation de meetups** : Créer des invitations déjeuner
- **Authentification Microsoft** : Intégration Entra ID (Azure AD)

## 🛠️ Stack technique

- **Backend** : Python FastAPI + SQLAlchemy + SQLite
- **Frontend** : Vue.js 3 + Nuxt 3 + MSAL
- **Auth** : Microsoft Entra ID avec validation JWT
- **Déploiement** : Docker Compose
- **API externe** : Google Places API (optionnel)

## 📦 Installation rapide

### 1. Cloner le projet
```bash
git clone https://github.com/votre-org/proximeet.git
cd proximeet
```

### 2. Configuration
```bash
cp .env.example .env
# Éditer .env avec vos clés Microsoft Entra ID
```

### 3. Lancer avec Docker
```bash
docker compose up --build
```

- **Frontend** : http://localhost:3000
- **Backend API** : http://localhost:8000
- **API Docs** : http://localhost:8000/docs

### 4. Données de test (optionnel)
```bash
docker compose exec backend python init_data.py
```

## 🔧 Configuration

### Variables d'environnement requises

#### Backend
- `ENTRA_TENANT_ID` : ID du tenant Microsoft (ou "common")
- `ENTRA_CLIENT_ID` : ID de l'application Azure AD
- `ENTRA_AUDIENCE` : Audience du token (souvent = CLIENT_ID)
- `GOOGLE_PLACES_API_KEY` : Clé API Google Places (optionnel)
- `ALLOW_ANONYMOUS` : Autoriser le mode anonyme (dev only)

#### Frontend
- `NUXT_PUBLIC_MSAL_CLIENT_ID` : ID de l'application Azure AD
- `NUXT_PUBLIC_MSAL_TENANT_ID` : ID du tenant Microsoft
- `NUXT_PUBLIC_MSAL_REDIRECT_URI` : URI de redirection (http://localhost:3000)
- `NUXT_PUBLIC_MSAL_SCOPES` : Scopes demandés (User.Read par défaut)

## 📋 Endpoints API principaux

### Authentification
- `GET /me` - Infos utilisateur connecté
- `GET /health` - Status de l'API

### Présence
- `POST /presence` - Partager sa position
- `GET /presence/me` - Ma position active
- `GET /nearby?radius_km=2` - Collègues à proximité

### Restaurants
- `GET /restaurants` - Liste des restaurants
- `GET /restaurants/search?query=pizza` - Recherche Google Places
- `POST /restaurants` - Ajouter un restaurant
- `POST /restaurants/{id}/recommendations` - Noter un restaurant
- `GET /restaurants/{id}/recommendations` - Voir les avis

### Meetups
- `POST /meetups` - Créer un déjeuner
- `GET /meetups?status=PENDING` - Liste des meetups
- `PATCH /meetups/{id}` - Mettre à jour le statut

## 🧪 Développement local

### Backend seul
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend seul
```bash
cd frontend
npm install
npm run dev
```

## 🐛 Problèmes courants

### "MSAL client id missing"
→ Configurer `NUXT_PUBLIC_MSAL_CLIENT_ID` dans .env

### "No active presence"
→ Partager d'abord votre position dans le dashboard

### CORS errors
→ Vérifier que l'URL frontend est dans les origines autorisées

## 📝 Licence

MIT - Voir LICENSE

## 🤝 Contribution

Les PRs sont bienvenues ! Voir CONTRIBUTING.md pour les guidelines.

---

Développé avec ❤️ pour faciliter les déjeuners entre collègues