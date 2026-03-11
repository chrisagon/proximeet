#!/bin/bash
# Script pour initialiser les données de test via API

API_BASE="http://localhost:8000"

echo "🔧 Initialisation des données de test PROXIMEET..."

# Créer quelques présences (mode anonyme)
echo "📍 Création de présences..."
curl -s -X POST "$API_BASE/presence" \
  -H "Content-Type: application/json" \
  -H "X-User-Id: alice" \
  -H "X-User-Email: alice@example.com" \
  -d '{
    "latitude": 48.8924,
    "longitude": 2.2360,
    "location_type": "CLIENT",
    "expires_in_hours": 6
  }' | jq -r '.user_id'

curl -s -X POST "$API_BASE/presence" \
  -H "Content-Type: application/json" \
  -H "X-User-Id: bob" \
  -H "X-User-Email: bob@example.com" \
  -d '{
    "latitude": 48.8914,
    "longitude": 2.2380,
    "location_type": "CLIENT",
    "expires_in_hours": 6
  }' | jq -r '.user_id'

# Créer des restaurants
echo "🍽️  Création de restaurants..."
curl -s -X POST "$API_BASE/restaurants" \
  -H "Content-Type: application/json" \
  -d '{
    "place_id": "resto_1",
    "name": "Le Bistrot du Coin",
    "cuisine_tags": "Français,Bistro",
    "is_official_habit": true
  }' | jq -r '.name'

curl -s -X POST "$API_BASE/restaurants" \
  -H "Content-Type: application/json" \
  -d '{
    "place_id": "resto_2",
    "name": "Sushi Sakura",
    "cuisine_tags": "Japonais,Sushi",
    "is_official_habit": false
  }' | jq -r '.name'

echo "✅ Données de test créées !"
echo ""
echo "🌐 Accès à l'application :"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
