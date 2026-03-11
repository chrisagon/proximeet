# Spécifications - Création de compte et Onboarding PROXIMEET

## 1. Flux de création de compte

### Page d'inscription (/signup)
Formulaire simple avec :
- Email (unique, validé)
- Prénom
- Nom
- Pseudo (optionnel)
- Mot de passe (pour mode sans MSAL)
- Avatar (upload optionnel)

### Validation
- Email unique dans la base
- Format email valide
- Champs nom/prénom requis
- Redirection vers onboarding après inscription

## 2. Flux d'onboarding (/onboarding)

### Étape 1 : Bienvenue
- Message de bienvenue personnalisé
- Explication rapide de PROXIMEET
- Bouton "Commencer"

### Étape 2 : Préférences personnelles
- Restrictions alimentaires (textarea)
  * Exemples : végétarien, sans gluten, halal, etc.
- Niveau de confidentialité (radio buttons)
  * PRECISE : Position exacte visible
  * BUBBLE : Zone approximative (300m)
- Explication de chaque option

### Étape 3 : Première position
- Demander l'autorisation de géolocalisation
- Détection automatique de la position
- Partage de la première présence
- Type de localisation (CLIENT ou HOME)

### Étape 4 : Découverte
- Recherche de collègues à proximité (rayon 2km par défaut)
- Affichage sur carte
- Bouton "Terminer"

### Redirection
Après onboarding → Dashboard avec état "onboarding_completed"

## 3. Backend - Nouveaux endpoints

### POST /auth/signup
```json
{
  "email": "user@example.com",
  "first_name": "Jean",
  "last_name": "Dupont",
  "nickname": "jdupont",
  "password": "optional_for_anonymous_mode"
}
```
Retourne le user créé + token

### PATCH /me
Mise à jour du profil utilisateur :
```json
{
  "dietary_restrictions": "Végétarien, sans gluten",
  "privacy_level": "BUBBLE",
  "avatar_url": "url_or_base64"
}
```

## 4. Frontend - Nouvelles pages

### /signup 
Formulaire d'inscription simple et moderne

### /onboarding
Stepper avec 4 étapes :
- Progress bar en haut
- Navigation précédent/suivant
- Skip optionnel pour certaines étapes
- Design cohérent avec l'app

## 5. State management

Utiliser localStorage pour :
- `onboarding_completed` : boolean
- `user_preferences` : object
- Redirect automatique si déjà complété

## 6. UX/Design

- Design moderne et accueillant
- Illustrations ou icônes pour chaque étape
- Animations de transition fluides
- Messages encourageants
- Mobile-first responsive