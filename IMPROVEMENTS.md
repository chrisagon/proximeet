# Améliorations pour PROXIMEET

## 1. Sécurité et validation

### Backend
- **Validation des coordonnées GPS** : Ajouter des limites sur latitude (-90 à 90) et longitude (-180 à 180)
- **Rate limiting** : Limiter les appels API par utilisateur (ex: slowapi)
- **Validation CORS** : Remplacer `["*"]` par des origines spécifiques en production
- **Gestion des erreurs JWKS** : Ajouter un retry mechanism en cas d'échec

### Frontend
- **Géolocalisation automatique** : Utiliser l'API du navigateur pour obtenir la position
- **Token refresh** : Implémenter le renouvellement automatique des tokens expirés

## 2. Fonctionnalités manquantes

### Backend
- **Pagination** : Ajouter pagination sur `/nearby`, `/restaurants`, `/meetups`
- **Filtres avancés** : Filtrer restaurants par tags cuisine, meetups par date
- ✅ **Notifications** : Système de notifications pour les invitations meetup - FAIT
- ✅ **Invitations avec date/heure** : Ajouter scheduled_at aux invitations - FAIT
- ✅ **Réponse aux invitations** : Endpoint pour accepter/refuser via lien email - FAIT
- **Historique** : Garder un historique des présences pour analytics

### Frontend
- **Carte interactive** : Intégrer Leaflet ou Google Maps pour visualiser
- **PWA** : Ajouter manifest.json et service worker pour mode offline
- **Responsive** : Améliorer l'expérience mobile
- **Loading states** : Ajouter des indicateurs de chargement
- ✅ **Date/heure invitation** : Champ datetime dans InviteModal - FAIT
- ✅ **Boutons accept/refuse** : Actions directes dans NotificationBell - FAIT
- ✅ **Page réponse email** : Page publique pour répondre via lien email - FAIT

## 3. Optimisations

### Backend
- **Indexes manquants** : Ajouter indexes sur `presence.expires_at`, `recommendations.restaurant_id`
- **Cache** : Implémenter Redis pour cache des restaurants populaires
- **Batch operations** : Permettre de récupérer plusieurs présences en une requête

### Frontend
- **Lazy loading** : Charger les composants à la demande
- **API composable** : Créer un composable réutilisable pour les appels API
- **State management** : Utiliser Pinia pour gérer l'état global

## 4. Tests et monitoring

### Backend
- **Tests unitaires** : Ajouter pytest pour tester les endpoints
- **Tests d'intégration** : Tester les workflows complets
- **Logging** : Utiliser loguru pour un meilleur logging
- **Monitoring** : Intégrer Prometheus/Grafana

### Frontend
- **Tests E2E** : Utiliser Playwright pour tests end-to-end
- **Tests unitaires** : Vitest pour les composables
- **Error tracking** : Intégrer Sentry

## 5. DevOps

### Docker
- **Multi-stage builds** : Optimiser la taille des images
- **Health checks** : Ajouter des health checks dans docker-compose
- **Secrets management** : Utiliser Docker secrets pour les credentials

### CI/CD
- **GitHub Actions** : Pipeline pour tests et déploiement
- **Pre-commit hooks** : Linting et formatting automatique
- **Semantic versioning** : Gérer les versions proprement

## 6. Documentation

- **API documentation** : Activer Swagger UI sur `/docs`
- **README détaillé** : Ajouter screenshots et guide d'installation
- **Architecture diagram** : Documenter l'architecture avec diagrams.net
- **Contributing guide** : Guide pour les contributeurs

## Implémentation prioritaire

1. ✅ **Géolocalisation auto** (UX critique) - FAIT
2. ✅ **Carte interactive** (visualisation essentielle) - FAIT
3. ✅ **Pagination** (performance) - FAIT (skip/limit sur /nearby, /restaurants, /meetups)
4. ✅ **PWA / Mode offline** - FAIT (manifest.json, service worker, offline indicator)
5. **Tests de base** (qualité)
6. **Health checks** (production readiness)