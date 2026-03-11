# Spécifications pour l'intégration de Leaflet

## Objectif
Ajouter une carte interactive Leaflet pour visualiser :
- Sa propre position
- Les collègues à proximité
- Les restaurants recommandés
- Les zones de confidentialité (mode bubble)

## Fonctionnalités requises

### 1. Composant carte réutilisable
- Composant Vue `<ProximeetMap>`
- Props : center, zoom, markers
- Events : @marker-click, @map-click

### 2. Page Dashboard
- Afficher sa position avec un marqueur bleu
- Afficher les collègues avec des marqueurs verts
- Mode BUBBLE : afficher un cercle flou autour de la position approximative
- Clic sur marqueur : afficher popup avec infos utilisateur

### 3. Page Restaurants  
- Afficher les restaurants sur la carte
- Marqueurs avec icônes personnalisées
- Popup avec nom, note moyenne et nombre d'avis
- Clic : ouvrir détails restaurant

### 4. Design
- Utiliser OpenStreetMap comme fond de carte
- Marqueurs personnalisés avec les couleurs de l'app
- Animations fluides
- Responsive sur mobile

## Dépendances
- @nuxtjs/leaflet ou vue-leaflet
- leaflet CSS à importer
- Types TypeScript si disponibles