#!/usr/bin/env python3
"""Script d'initialisation avec données de test pour PROXIMEET"""

import os
import sys
from datetime import datetime, timedelta

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlmodel import Session, select
from backend.app.db import engine, init_db
from backend.app.models import User, Restaurant, Presence, LocationType, PrivacyLevel, Role

def init_test_data():
    """Initialise la base de données avec des données de test"""
    
    # Créer les tables
    init_db()
    
    with Session(engine) as session:
        # Créer des utilisateurs de test
        users = [
            User(
                id="user1",
                email="alice@example.com",
                first_name="Alice",
                last_name="Martin",
                privacy_level=PrivacyLevel.PRECISE
            ),
            User(
                id="user2", 
                email="bob@example.com",
                first_name="Bob",
                last_name="Dupont",
                privacy_level=PrivacyLevel.BUBBLE
            ),
            User(
                id="user3",
                email="charlie@example.com", 
                first_name="Charlie",
                last_name="Bernard",
                privacy_level=PrivacyLevel.BUBBLE
            ),
            User(
                id="admin_chris",
                email="chrisagon@gmail.com",
                first_name="Chris",
                last_name="Agon",
                role=Role.ADMIN,
                privacy_level=PrivacyLevel.BUBBLE
            )
        ]
        
        for user in users:
            existing = session.get(User, user.id)
            if not existing:
                session.add(user)
            elif user.email == "chrisagon@gmail.com" and existing.role != Role.ADMIN:
                existing.role = Role.ADMIN
                session.add(existing)

        admin_by_email = session.exec(
            select(User).where(User.email == "chrisagon@gmail.com")
        ).first()
        if admin_by_email and admin_by_email.role != Role.ADMIN:
            admin_by_email.role = Role.ADMIN
            session.add(admin_by_email)
        
        # Ajouter des présences actives (Paris - La Défense)
        presences = [
            Presence(
                user_id="user1",
                latitude=48.8924,
                longitude=2.2360,
                location_type=LocationType.CLIENT,
                expires_at=datetime.utcnow() + timedelta(hours=4)
            ),
            Presence(
                user_id="user2",
                latitude=48.8914,
                longitude=2.2380,
                location_type=LocationType.CLIENT,
                expires_at=datetime.utcnow() + timedelta(hours=5)
            ),
            Presence(
                user_id="user3",
                latitude=48.8934,
                longitude=2.2340,
                location_type=LocationType.CLIENT,
                expires_at=datetime.utcnow() + timedelta(hours=3)
            )
        ]
        
        for presence in presences:
            # Supprimer l'ancienne présence si elle existe
            existing = session.query(Presence).filter_by(user_id=presence.user_id).first()
            if existing:
                session.delete(existing)
            session.add(presence)
        
        # Ajouter des restaurants populaires de La Défense
        restaurants = [
            Restaurant(
                place_id="ChIJM1PaREX65kcRv_D9U4oNGBQ",
                name="Les 4 Temps - Food Court",
                cuisine_tags="Multiple,Fast Food",
                is_official_habit=True,
                vote_count=15,
                average_rating=3.5
            ),
            Restaurant(
                place_id="ChIJLU7jZED65kcR6kCj8qIbFAE",
                name="Vapiano La Défense",
                cuisine_tags="Italien,Pâtes,Pizza",
                is_official_habit=True,
                vote_count=22,
                average_rating=4.2
            ),
            Restaurant(
                place_id="ChIJHc6J6z_65kcRkUciRuG1BQU",
                name="Chez Gladines La Défense", 
                cuisine_tags="Français,Bistro",
                vote_count=18,
                average_rating=4.5
            ),
            Restaurant(
                place_id="ChIJpYtlzkD65kcRBL2YJmVsVYk",
                name="Pokawa - Poké bowls",
                cuisine_tags="Hawaïen,Healthy,Poké",
                vote_count=12,
                average_rating=4.3
            )
        ]
        
        for restaurant in restaurants:
            existing = session.get(Restaurant, restaurant.place_id)
            if not existing:
                session.add(restaurant)
        
        session.commit()
        print("✅ Base de données initialisée avec succès !")
        print(f"   - {len(users)} utilisateurs créés")
        print(f"   - {len(presences)} présences actives")
        print(f"   - {len(restaurants)} restaurants ajoutés")

if __name__ == "__main__":
    init_test_data()
