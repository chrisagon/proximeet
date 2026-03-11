# PROXIMEET - Spécifications de l'application

## Vue d'ensemble
Application pour faciliter l'organisation de déjeuners entre consultants travaillant sur le même site client ou zone géographique.

## Fonctionnalités principales

### 1. Authentification
- Authentification via Microsoft Entra ID (ex-Azure AD)
- Rôles : ADMIN, PROXIMEETER, CONSULTANT

### 2. Gestion de la présence
- Partage de position éphémère (expire après 6h par défaut)
- Types de localisation : CLIENT ou HOME
- Confidentialité : mode PRECISE (position exacte) ou BUBBLE (zone approximative)

### 3. Recherche de collègues
- Trouver des consultants à proximité pour déjeuner
- Filtrer par rayon (1, 2, 3, 5 km)
- Respect de la confidentialité (mode BUBBLE)

### 4. Restaurants
- Recommander des restaurants
- Noter et commenter (1-5 étoiles)
- Habitudes officielles et favorites personnelles
- Tags de cuisine

### 5. Organisation de meetups
- Créer des invitations déjeuner
- Définir un rayon d'invitation
- Statuts : PENDING, COMPLETED, CANCELLED

## Architecture technique
- Frontend : Vue.js/Nuxt.js
- Backend : API Python (FastAPI recommandé)
- Base de données : SQLite
- Authentification : Microsoft Entra ID
- API externe : Google Places API

## Schéma de base de données

```sql
-- 1. Table des utilisateurs (Profil et Confidentialité)
CREATE TABLE users (
    id TEXT PRIMARY KEY, -- ID unique (ex: Microsoft Entra ID)
    email TEXT UNIQUE NOT NULL,
    first_name TEXT,
    last_name TEXT,
    nickname TEXT,
    avatar_url TEXT,
    dietary_restrictions TEXT,
    teams_id TEXT,
    role TEXT CHECK(role IN ('ADMIN', 'PROXIMEETER', 'CONSULTANT')) DEFAULT 'CONSULTANT',
    privacy_level TEXT CHECK(privacy_level IN ('PRECISE', 'BUBBLE')) DEFAULT 'BUBBLE',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. Table de présence (Données éphémères)
CREATE TABLE presence (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT REFERENCES users(id),
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    location_type TEXT CHECK(location_type IN ('CLIENT', 'HOME')) NOT NULL,
    expires_at DATETIME NOT NULL,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 3. Table des Restaurants & Habitudes
CREATE TABLE restaurants (
    place_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    cuisine_tags TEXT,
    is_official_habit BOOLEAN DEFAULT 0,
    vote_count INTEGER DEFAULT 0,
    average_rating REAL DEFAULT 0
);

-- 4. Table des Recommandations (Détail des votes)
CREATE TABLE recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    restaurant_id TEXT REFERENCES restaurants(place_id),
    user_id TEXT REFERENCES users(id),
    rating INTEGER CHECK(rating BETWEEN 1 AND 5),
    comment TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 5. Table des Meetups (Organisation de déjeuners)
CREATE TABLE meetups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    organizer_id TEXT REFERENCES users(id),
    restaurant_id TEXT REFERENCES restaurants(place_id),
    radius_km INTEGER DEFAULT 1, -- Rayon d'invitation (1, 2, 3, 5)
    scheduled_at DATETIME NOT NULL,
    status TEXT CHECK(status IN ('PENDING', 'COMPLETED', 'CANCELLED')) DEFAULT 'PENDING'
);

-- Index pour la performance
CREATE INDEX idx_presence_expiry ON presence(expires_at);
CREATE INDEX idx_recommendations_resto ON recommendations(restaurant_id);

-- Trigger pour l'automatisation des statistiques restaurants
CREATE TRIGGER update_restaurant_stats
AFTER INSERT ON recommendations
BEGIN
    UPDATE restaurants
    SET vote_count = (SELECT COUNT(*) FROM recommendations WHERE restaurant_id = NEW.restaurant_id),
        average_rating = (SELECT AVG(rating) FROM recommendations WHERE restaurant_id = NEW.restaurant_id)
    WHERE place_id = NEW.restaurant_id;
END;
```

## Règles de gestion

1. **Présence éphémère** : Les positions expirent automatiquement après 6h
2. **Confidentialité** : Mode BUBBLE masque la position exacte (zone approximative)
3. **Rayon de recherche** : 1, 2, 3 ou 5 km autour de la position actuelle
4. **Restaurants** : Intégration Google Places API + recommandations communautaires
5. **Meetups** : Invitations envoyées aux consultants dans le rayon défini