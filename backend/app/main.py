from datetime import datetime, timedelta, timezone
import logging
import math
import random
import re
from uuid import uuid4
from typing import List, Optional

import requests
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select

from .auth import get_current_user
from .config import get_settings
from .db import get_session, init_db
from .email import send_invitation_email
from .models import (
    Invitation,
    InvitationStatus,
    Meetup,
    MeetupStatus,
    Notification,
    Presence,
    Restaurant,
    Recommendation,
    Role,
    User,
    UserFavoriteRestaurant,
)
from .schemas import (
    MeetupCreate,
    MeetupRead,
    MeetupUpdate,
    NearbyResult,
    PaginatedResponse,
    AuthResponse,
    FavoriteRestaurantRead,
    InvitationCreate,
    InvitationRead,
    InvitationReadWithDetails,
    InvitationUpdate,
    NotificationRead,
    PresenceCreate,
    PresenceRead,
    RecommendationCreate,
    RecommendationRead,
    RestaurantCreate,
    RestaurantRead,
    UserSignup,
    UserLogin,
    UserUpdate,
    UserRead,
)


app = FastAPI(title="PROXIMEET API")
settings = get_settings()
logger = logging.getLogger("proximeet")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://frontend:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"] ,
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/me", response_model=UserRead)
def get_me(user: User = Depends(get_current_user)) -> User:
    return user


def _is_base64(value: str) -> bool:
    if len(value) < 24:
        return False
    return bool(re.fullmatch(r"[A-Za-z0-9+/=\s]+", value))


def _normalize_avatar(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    trimmed = value.strip()
    if trimmed.startswith("http://") or trimmed.startswith("https://"):
        return trimmed
    if trimmed.startswith("data:image/"):
        return trimmed
    if _is_base64(trimmed):
        return trimmed
    raise HTTPException(status_code=422, detail="avatar_url must be a URL or base64 string")


def _require_admin(user: User) -> None:
    if user.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="Admin role required")


@app.post("/auth/signup", response_model=AuthResponse, status_code=201)
def signup(
    payload: UserSignup,
    session: Session = Depends(get_session),
) -> dict:
    existing = session.exec(select(User).where(User.email == payload.email)).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")
    avatar = _normalize_avatar(payload.avatar_url)
    user = User(
        id=str(uuid4()),
        email=payload.email,
        first_name=payload.first_name,
        last_name=payload.last_name,
        nickname=payload.nickname,
        avatar_url=avatar,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    token = f"local:{user.id}"
    return {
        "user": UserRead(**user.model_dump()),
        "token": token
    }


@app.post("/auth/login", response_model=AuthResponse)
def login(
    payload: UserLogin,
    session: Session = Depends(get_session),
) -> dict:
    user = session.exec(select(User).where(User.email == payload.email)).first()
    if not user:
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
    
    # En mode anonyme, on accepte n'importe quel mot de passe ou pas de mot de passe
    # Pour une vraie auth, il faudrait vérifier le hash du password ici
    
    token = f"local:{user.id}"
    return {
        "user": UserRead(**user.model_dump()),
        "token": token
    }


@app.patch("/me", response_model=UserRead)
def update_me(
    payload: UserUpdate,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
) -> User:
    if payload.dietary_restrictions is not None:
        user.dietary_restrictions = payload.dietary_restrictions
    if payload.privacy_level is not None:
        user.privacy_level = payload.privacy_level
    if payload.avatar_url is not None:
        user.avatar_url = _normalize_avatar(payload.avatar_url)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return r * c


def _bubble_coordinates(lat: float, lon: float, radius_km: float) -> tuple[float, float]:
    angle = random.uniform(0, 2 * math.pi)
    distance = random.uniform(0, radius_km)
    delta_lat = (distance / 111.0) * math.cos(angle)
    delta_lon = (distance / (111.0 * math.cos(math.radians(lat)))) * math.sin(angle)
    return lat + delta_lat, lon + delta_lon


@app.post("/presence", response_model=PresenceRead)
def update_presence(
    payload: PresenceCreate,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
) -> Presence:
    expires_in = payload.expires_in_hours or settings.presence_default_hours
    expires_at = datetime.utcnow() + timedelta(hours=expires_in)

    existing = session.exec(select(Presence).where(Presence.user_id == user.id)).first()
    if existing:
        session.delete(existing)
        session.commit()

    presence = Presence(
        user_id=user.id,
        latitude=payload.latitude,
        longitude=payload.longitude,
        location_type=payload.location_type,
        expires_at=expires_at,
    )
    session.add(presence)
    session.commit()
    session.refresh(presence)
    return presence


@app.get("/presence/me", response_model=Optional[PresenceRead])
def get_presence(
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
) -> Optional[Presence]:
    now = datetime.utcnow()
    presence = session.exec(
        select(Presence).where(Presence.user_id == user.id, Presence.expires_at > now)
    ).first()
    return presence


@app.get("/nearby", response_model=PaginatedResponse[NearbyResult])
def nearby_users(
    radius_km: int = Query(1, ge=1, le=20),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
) -> PaginatedResponse[NearbyResult]:
    now = datetime.utcnow()
    my_presence = session.exec(
        select(Presence).where(Presence.user_id == user.id, Presence.expires_at > now)
    ).first()
    if not my_presence:
        raise HTTPException(status_code=400, detail="No active presence")

    presences = session.exec(
        select(Presence, User)
        .where(Presence.user_id == User.id)
        .where(Presence.expires_at > now)
        .where(Presence.user_id != user.id)
    ).all()

    results: List[NearbyResult] = []
    for presence, other in presences:
        distance = _haversine_km(
            my_presence.latitude,
            my_presence.longitude,
            presence.latitude,
            presence.longitude,
        )
        if distance > radius_km:
            continue
        lat = presence.latitude
        lon = presence.longitude
        if other.privacy_level.value == "BUBBLE":
            lat, lon = _bubble_coordinates(lat, lon, settings.bubble_radius_km)
        results.append(
            NearbyResult(
                user_id=other.id,
                first_name=other.first_name,
                last_name=other.last_name,
                nickname=other.nickname,
                role=other.role,
                privacy_level=other.privacy_level,
                distance_km=round(distance, 3),
                latitude=lat if other.privacy_level.value == "PRECISE" else lat,
                longitude=lon if other.privacy_level.value == "PRECISE" else lon,
            )
        )

    sorted_results = sorted(results, key=lambda item: item.distance_km)
    total = len(sorted_results)
    paginated = sorted_results[skip : skip + limit]
    has_more = (skip + limit) < total

    return PaginatedResponse(
        items=paginated,
        total=total,
        skip=skip,
        limit=limit,
        has_more=has_more,
    )


@app.get("/restaurants", response_model=PaginatedResponse[RestaurantRead])
def list_restaurants(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_session),
) -> PaginatedResponse[RestaurantRead]:
    # Get total count
    from sqlalchemy import func
    count_query = select(func.count()).select_from(Restaurant)
    total = session.exec(count_query).first() or 0
    # Get paginated results
    statement = select(Restaurant).offset(skip).limit(limit)
    restaurants = list(session.exec(statement).all())
    has_more = (skip + limit) < total

    return PaginatedResponse(
        items=restaurants,
        total=total,
        skip=skip,
        limit=limit,
        has_more=has_more,
    )


@app.get("/restaurants/search")
def search_restaurants(
    query: str, 
    latitude: Optional[float] = None, 
    longitude: Optional[float] = None,
    radius: int = 2000  # Réduit à 2km par défaut pour plus de pertinence locale
) -> dict:
    if not settings.google_places_api_key:
        return {"results": [], "message": "GOOGLE_PLACES_API_KEY not configured"}
    
    # Si on a une localisation, on privilégie nearbysearch qui est bien meilleur pour "Autour de moi"
    if latitude is not None and longitude is not None:
        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        params = {
            "keyword": query, # nearbysearch utilise keyword ou name
            "location": f"{latitude},{longitude}",
            "radius": radius,
            "key": settings.google_places_api_key
        }
    else:
        # Fallback sur textsearch si pas de geoloc
        url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        params = {
            "query": query,
            "key": settings.google_places_api_key
        }
        
    response = requests.get(
        url,
        params=params,
        timeout=8,
    )
    response.raise_for_status()
    data = response.json()
    
    # Mapping des résultats qui peut varier légèrement entre textsearch et nearbysearch
    results = [
        {
            "place_id": item.get("place_id"),
            "name": item.get("name"),
            "rating": item.get("rating"),
            "address": item.get("vicinity") if "vicinity" in item else item.get("formatted_address"), # nearbysearch renvoie vicinity
            "lat": item.get("geometry", {}).get("location", {}).get("lat"),
            "lng": item.get("geometry", {}).get("location", {}).get("lng"),
        }
        for item in data.get("results", [])
    ]
    return {"results": results}


@app.post("/restaurants", response_model=RestaurantRead)
def create_restaurant(
    payload: RestaurantCreate,
    session: Session = Depends(get_session),
) -> Restaurant:
    existing = session.get(Restaurant, payload.place_id)
    if existing:
        # Rafraîchir pour s'assurer que tous les champs sont chargés
        session.refresh(existing)
        return existing
    restaurant = Restaurant(**payload.model_dump())
    session.add(restaurant)
    session.commit()
    session.refresh(restaurant)
    return restaurant


@app.post("/restaurants/{place_id}/favorite", response_model=FavoriteRestaurantRead)
def add_favorite(
    place_id: str,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
) -> FavoriteRestaurantRead:
    restaurant = session.get(Restaurant, place_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    # Rafraîchir le restaurant pour s'assurer que tous les champs sont chargés
    session.refresh(restaurant)
    
    favorite = session.exec(
        select(UserFavoriteRestaurant).where(
            UserFavoriteRestaurant.user_id == user.id,
            UserFavoriteRestaurant.restaurant_id == place_id,
        )
    ).first()
    
    if not favorite:
        favorite = UserFavoriteRestaurant(user_id=user.id, restaurant_id=place_id)
        session.add(favorite)
        session.commit()
        session.refresh(favorite)
    else:
        # Rafraîchir aussi le favori existant
        session.refresh(favorite)
    
    # Construire explicitement le dict avec valeurs par défaut pour éviter NULL
    restaurant_dict = {
        "place_id": restaurant.place_id or "",
        "name": restaurant.name or "",
        "address": restaurant.address,
        "latitude": restaurant.latitude,
        "longitude": restaurant.longitude,
        "cuisine_tags": restaurant.cuisine_tags,
        "is_official_habit": restaurant.is_official_habit if restaurant.is_official_habit is not None else False,
        "vote_count": restaurant.vote_count if restaurant.vote_count is not None else 0,
        "average_rating": restaurant.average_rating if restaurant.average_rating is not None else 0.0,
    }
    
    return FavoriteRestaurantRead(
        restaurant=RestaurantRead(**restaurant_dict),
        created_at=favorite.created_at,
    )


@app.delete("/restaurants/{place_id}/favorite")
def remove_favorite(
    place_id: str,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
) -> dict:
    favorite = session.exec(
        select(UserFavoriteRestaurant).where(
            UserFavoriteRestaurant.user_id == user.id,
            UserFavoriteRestaurant.restaurant_id == place_id,
        )
    ).first()
    if not favorite:
        raise HTTPException(status_code=404, detail="Favorite not found")
    session.delete(favorite)
    session.commit()
    return {"status": "removed"}


@app.delete("/restaurants/{place_id}")
def delete_restaurant(
    place_id: str,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
) -> dict:
    _require_admin(user)
    restaurant = session.get(Restaurant, place_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    if not restaurant.is_official_habit:
        raise HTTPException(
            status_code=400,
            detail="Only internal restaurants can be deleted",
        )

    favorites = session.exec(
        select(UserFavoriteRestaurant).where(
            UserFavoriteRestaurant.restaurant_id == place_id
        )
    ).all()
    for favorite in favorites:
        session.delete(favorite)

    recommendations = session.exec(
        select(Recommendation).where(Recommendation.restaurant_id == place_id)
    ).all()
    for recommendation in recommendations:
        session.delete(recommendation)

    invitations = session.exec(
        select(Invitation).where(Invitation.restaurant_id == place_id)
    ).all()
    for invitation in invitations:
        session.delete(invitation)

    meetups = session.exec(
        select(Meetup).where(Meetup.restaurant_id == place_id)
    ).all()
    for meetup in meetups:
        meetup.restaurant_id = None
        session.add(meetup)

    session.delete(restaurant)
    session.commit()
    return {"status": "deleted"}


@app.get("/me/favorites", response_model=List[FavoriteRestaurantRead])
def list_favorites(
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
) -> List[FavoriteRestaurantRead]:
    rows = session.exec(
        select(UserFavoriteRestaurant, Restaurant)
        .where(UserFavoriteRestaurant.user_id == user.id)
        .where(UserFavoriteRestaurant.restaurant_id == Restaurant.place_id)
        .order_by(UserFavoriteRestaurant.created_at.desc())
    ).all()
    return [
        FavoriteRestaurantRead(
            restaurant=RestaurantRead(**restaurant.model_dump()),
            created_at=favorite.created_at,
        )
        for favorite, restaurant in rows
    ]


def _recompute_stats(session: Session, restaurant_id: str) -> None:
    ratings = session.exec(
        select(Recommendation.rating).where(Recommendation.restaurant_id == restaurant_id)
    ).all()
    if not ratings:
        vote_count = 0
        average = 0.0
    else:
        vote_count = len(ratings)
        average = sum(ratings) / vote_count
    restaurant = session.get(Restaurant, restaurant_id)
    if restaurant:
        restaurant.vote_count = vote_count
        restaurant.average_rating = round(average, 2)
        session.add(restaurant)
        session.commit()


@app.post(
    "/restaurants/{place_id}/recommendations", response_model=RecommendationRead
)
def add_recommendation(
    place_id: str,
    payload: RecommendationCreate,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
) -> Recommendation:
    restaurant = session.get(Restaurant, place_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    recommendation = Recommendation(
        restaurant_id=place_id,
        user_id=user.id,
        rating=payload.rating,
        comment=payload.comment,
    )
    session.add(recommendation)
    session.commit()
    session.refresh(recommendation)
    _recompute_stats(session, place_id)
    return recommendation


@app.get(
    "/restaurants/{place_id}/recommendations", response_model=List[RecommendationRead]
)
def list_recommendations(
    place_id: str, session: Session = Depends(get_session)
) -> List[Recommendation]:
    return list(
        session.exec(
            select(Recommendation).where(Recommendation.restaurant_id == place_id)
        ).all()
    )


@app.post("/meetups", response_model=MeetupRead)
def create_meetup(
    payload: MeetupCreate,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
) -> Meetup:
    meetup = Meetup(
        organizer_id=user.id,
        restaurant_id=payload.restaurant_id,
        radius_km=payload.radius_km,
        scheduled_at=payload.scheduled_at,
        status=MeetupStatus.PENDING,
    )
    session.add(meetup)
    session.commit()
    session.refresh(meetup)
    return meetup


@app.get("/meetups", response_model=PaginatedResponse[MeetupRead])
def list_meetups(
    status: Optional[MeetupStatus] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_session),
) -> PaginatedResponse[MeetupRead]:
    from sqlalchemy import func
    
    # Build base query
    base_query = select(Meetup)
    if status:
        base_query = base_query.where(Meetup.status == status)

    # Get total count
    count_query = select(func.count()).select_from(Meetup)
    if status:
        count_query = count_query.where(Meetup.status == status)
    total = session.exec(count_query).first() or 0
    
    # Get paginated results
    query = base_query.offset(skip).limit(limit)
    meetups = list(session.exec(query).all())
    has_more = (skip + limit) < total

    return PaginatedResponse(
        items=meetups,
        total=total,
        skip=skip,
        limit=limit,
        has_more=has_more,
    )


@app.patch("/meetups/{meetup_id}", response_model=MeetupRead)
def update_meetup(
    meetup_id: int,
    payload: MeetupUpdate,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
) -> Meetup:
    meetup = session.get(Meetup, meetup_id)
    if not meetup:
        raise HTTPException(status_code=404, detail="Meetup not found")
    if meetup.organizer_id != user.id:
        raise HTTPException(status_code=403, detail="Not organizer")
    meetup.status = payload.status
    session.add(meetup)
    session.commit()
    session.refresh(meetup)
    return meetup


@app.post("/invitations", response_model=InvitationRead, status_code=201)
def create_invitation(
    payload: InvitationCreate,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
) -> Invitation:
    invitee = session.get(User, payload.invitee_id)
    if not invitee:
        raise HTTPException(status_code=404, detail="Invitee not found")
    restaurant = session.get(Restaurant, payload.restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    if payload.meetup_id is not None:
        meetup = session.get(Meetup, payload.meetup_id)
        if not meetup:
            raise HTTPException(status_code=404, detail="Meetup not found")
    if payload.scheduled_at:
        scheduled_at = payload.scheduled_at
        if scheduled_at.tzinfo is not None:
            scheduled_at = scheduled_at.astimezone(timezone.utc).replace(tzinfo=None)
        if scheduled_at.date() < datetime.utcnow().date():
            raise HTTPException(status_code=400, detail="Scheduled date must be today or in the future")
    
    # Formatter la date/heure pour affichage
    scheduled_str = ""
    if payload.scheduled_at:
        scheduled_str = payload.scheduled_at.strftime("%d/%m/%Y à %H:%M")
    elif payload.meetup_id:
        meetup = session.get(Meetup, payload.meetup_id)
        if meetup:
            scheduled_str = meetup.scheduled_at.strftime("%d/%m/%Y à %H:%M")
    
    invitation = Invitation(
        organizer_id=user.id,
        invitee_id=payload.invitee_id,
        restaurant_id=payload.restaurant_id,
        meetup_id=payload.meetup_id,
        status=InvitationStatus.PENDING,
        message=payload.message,
        scheduled_at=payload.scheduled_at,
    )
    session.add(invitation)
    session.commit()
    session.refresh(invitation)
    
    # Créer une notification pour l'invité avec actions accept/decline
    organizer_name = user.first_name or user.nickname or user.email
    date_str = f" le {scheduled_str}" if scheduled_str else ""
    message_str = f" {payload.message}" if payload.message else ""
    
    # Construire le message de notification avec l'adresse si disponible
    address_str = ""
    if restaurant.address:
        address_str = f"\n📍 {restaurant.address}"
    
    notification_message = f"{organizer_name} vous invite au restaurant {restaurant.name}{date_str}.{address_str}{message_str}"
    
    notification = Notification(
        user_id=payload.invitee_id,
        type="invitation_received",
        title="Nouvelle invitation",
        message=notification_message,
        data=str(invitation.id),
    )
    session.add(notification)
    session.commit()
    
    # Générer des tokens d'action pour liens email (simple implementation)
    accept_token = f"accept_{invitation.id}_{invitee.id}"
    decline_token = f"decline_{invitation.id}_{invitee.id}"
    
    # Construire les URLs
    base_url = settings.frontend_url
    accept_url = f"{base_url}/invitations/{invitation.id}/respond?action=accept&token={accept_token}"
    decline_url = f"{base_url}/invitations/{invitation.id}/respond?action=decline&token={decline_token}"
    
    # Envoyer l'email d'invitation avec l'adresse du restaurant
    send_invitation_email(
        to_email=invitee.email,
        organizer_name=organizer_name,
        restaurant_name=restaurant.name,
        restaurant_address=restaurant.address,
        restaurant_lat=restaurant.latitude,
        restaurant_lng=restaurant.longitude,
        scheduled_at=scheduled_str or None,
        invitation_message=payload.message,
        accept_url=accept_url,
        decline_url=decline_url,
        frontend_url=base_url,
    )
    
    # Simulation d'envoi d'email (visible dans les logs) - gardé pour debug
    email_message = f"""
========================================
📧 EMAIL ENVOYÉ
À: {invitee.email}
Sujet: Invitation à déjeuner - Proximeet

Bonjour,

{organizer_name} vous invite à déjeuner au restaurant "{restaurant.name}"{date_str}.

Message: {payload.message or 'Aucun message'}

Pour répondre à cette invitation :

✅ ACCEPTER : http://localhost:3000/invitations/{invitation.id}/respond?action=accept&token={accept_token}

❌ REFUSER : http://localhost:3000/invitations/{invitation.id}/respond?action=decline&token={decline_token}

Ou connectez-vous sur Proximeet pour gérer vos invitations.

Cordialement,
L'équipe Proximeet
========================================
    """
    print(email_message)
    logger.info(email_message)
    
    return invitation


@app.get("/invitations/received", response_model=List[InvitationReadWithDetails])
def list_received_invitations(
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
) -> List[InvitationReadWithDetails]:
    logger.info(f"Fetching invitations for user: {user.id}")
    
    results = session.exec(
        select(Invitation, User, Restaurant)
        .where(Invitation.invitee_id == user.id)
        .join(User, Invitation.organizer_id == User.id, isouter=False)
        .join(Restaurant, Invitation.restaurant_id == Restaurant.place_id, isouter=False)
        .order_by(Invitation.created_at.desc())
    ).all()
    
    logger.info(f"Found {len(results)} invitations")
    
    invitations_with_details = []
    for row in results:
        invitation, organizer, restaurant = row
        
        organizer_name = f"{organizer.first_name or ''} {organizer.last_name or ''}".strip()
        if not organizer_name:
            organizer_name = organizer.nickname or organizer.email
        
        logger.info(f"Invitation {invitation.id}: organizer={organizer_name}, restaurant={restaurant.name}")
        
        invitations_with_details.append(
            InvitationReadWithDetails(
                id=invitation.id,
                organizer_id=invitation.organizer_id,
                organizer_name=organizer_name,
                organizer_email=organizer.email,
                invitee_id=invitation.invitee_id,
                restaurant_id=invitation.restaurant_id,
                restaurant_name=restaurant.name,
                meetup_id=invitation.meetup_id,
                status=invitation.status,
                message=invitation.message,
                scheduled_at=invitation.scheduled_at,
                created_at=invitation.created_at
            )
        )
    return invitations_with_details


@app.get("/invitations/accepted-meetings", response_model=List[InvitationReadWithDetails])
def list_accepted_meetings(
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
) -> List[InvitationReadWithDetails]:
    """
    Retourne toutes les invitations ACCEPTÉES où l'utilisateur est:
    - soit l'invité (celui qui reçoit l'invitation)
    - soit l'organisateur (celui qui envoie l'invitation)
    
    Utilisé pour l'agenda/calendrier pour montrer tous les rendez-vous confirmés.
    """
    logger.info(f"Fetching accepted meetings for user: {user.id}")
    
    # Récupérer les invitations acceptées où l'utilisateur est l'invité
    received_results = session.exec(
        select(Invitation, User, Restaurant)
        .where(Invitation.invitee_id == user.id)
        .where(Invitation.status == InvitationStatus.ACCEPTED)
        .join(User, Invitation.organizer_id == User.id, isouter=False)
        .join(Restaurant, Invitation.restaurant_id == Restaurant.place_id, isouter=False)
        .order_by(Invitation.scheduled_at.asc())
    ).all()
    
    # Récupérer les invitations acceptées où l'utilisateur est l'organisateur
    # Dans ce cas, on joint avec User pour obtenir les infos de l'invité
    sent_results = session.exec(
        select(Invitation, User, Restaurant)
        .where(Invitation.organizer_id == user.id)
        .where(Invitation.status == InvitationStatus.ACCEPTED)
        .join(User, Invitation.invitee_id == User.id, isouter=False)
        .join(Restaurant, Invitation.restaurant_id == Restaurant.place_id, isouter=False)
        .order_by(Invitation.scheduled_at.asc())
    ).all()
    
    logger.info(f"Found {len(received_results)} received and {len(sent_results)} sent accepted invitations")
    
    invitations_with_details = []
    
    # Traiter les invitations reçues (user = invité)
    for row in received_results:
        invitation, organizer, restaurant = row
        
        organizer_name = f"{organizer.first_name or ''} {organizer.last_name or ''}".strip()
        if not organizer_name:
            organizer_name = organizer.nickname or organizer.email
        
        invitations_with_details.append(
            InvitationReadWithDetails(
                id=invitation.id,
                organizer_id=invitation.organizer_id,
                organizer_name=organizer_name,
                organizer_email=organizer.email,
                invitee_id=invitation.invitee_id,
                restaurant_id=invitation.restaurant_id,
                restaurant_name=restaurant.name,
                meetup_id=invitation.meetup_id,
                status=invitation.status,
                message=invitation.message,
                scheduled_at=invitation.scheduled_at,
                created_at=invitation.created_at
            )
        )
    
    # Traiter les invitations envoyées (user = organisateur)
    # Dans ce cas, "organizer_name" dans le schema représente la personne avec qui on a RDV
    # donc on met le nom de l'invité à la place
    for row in sent_results:
        invitation, invitee_user, restaurant = row
        
        # Le "organizer_name" dans le response model représente la personne avec qui on a RDV
        # Pour les invitations envoyées, c'est l'invité
        person_name = f"{invitee_user.first_name or ''} {invitee_user.last_name or ''}".strip()
        if not person_name:
            person_name = invitee_user.nickname or invitee_user.email
        
        invitations_with_details.append(
            InvitationReadWithDetails(
                id=invitation.id,
                organizer_id=invitation.organizer_id,
                organizer_name=f"{person_name} (invité)",
                organizer_email=invitee_user.email,
                invitee_id=invitation.invitee_id,
                restaurant_id=invitation.restaurant_id,
                restaurant_name=restaurant.name,
                meetup_id=invitation.meetup_id,
                status=invitation.status,
                message=invitation.message,
                scheduled_at=invitation.scheduled_at,
                created_at=invitation.created_at
            )
        )
    
    # Trier par date de rendez-vous
    invitations_with_details.sort(key=lambda x: x.scheduled_at or datetime.min)
    
    logger.info(f"Total accepted meetings returned: {len(invitations_with_details)}")
    return invitations_with_details


@app.get("/invitations/sent", response_model=List[InvitationRead])
def list_sent_invitations(
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
) -> List[Invitation]:
    return list(
        session.exec(
            select(Invitation)
            .where(Invitation.organizer_id == user.id)
            .order_by(Invitation.created_at.desc())
        ).all()
    )


@app.get("/invitations/{invitation_id}", response_model=InvitationRead)
def get_invitation(
    invitation_id: int,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
) -> Invitation:
    """Récupère une invitation spécifique (accessible à l'organisateur ou l'invité)"""
    invitation = session.get(Invitation, invitation_id)
    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation not found")
    if invitation.invitee_id != user.id and invitation.organizer_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this invitation")
    return invitation


@app.patch("/invitations/{invitation_id}", response_model=InvitationRead)
def update_invitation(
    invitation_id: int,
    payload: InvitationUpdate,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
) -> Invitation:
    invitation = session.get(Invitation, invitation_id)
    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation not found")
    if invitation.invitee_id != user.id:
        raise HTTPException(status_code=403, detail="Not invitee")
    
    old_status = invitation.status
    invitation.status = payload.status
    session.add(invitation)
    session.commit()
    session.refresh(invitation)
    
    # Notifier l'organisateur si le statut change
    if old_status != payload.status:
        restaurant = session.get(Restaurant, invitation.restaurant_id)
        status_text = "acceptée" if payload.status == InvitationStatus.ACCEPTED else "déclinée"
        
        # Éviter les notifications en double - vérifier si une notification similaire existe récemment
        recent_notification = session.exec(
            select(Notification)
            .where(Notification.user_id == invitation.organizer_id)
            .where(Notification.type == "invitation_response")
            .where(Notification.data == str(invitation.id))
            .where(Notification.created_at > datetime.utcnow() - timedelta(minutes=5))
        ).first()
        
        if not recent_notification:
            notification = Notification(
                user_id=invitation.organizer_id,
                type="invitation_response",
                title=f"Invitation {status_text}",
                message=f"{user.first_name or user.nickname or user.email} a {status_text} votre invitation au restaurant {restaurant.name if restaurant else 'inconnu'}",
                data=str(invitation.id),
            )
            session.add(notification)
            session.commit()
    
    return invitation


@app.post("/invitations/{invitation_id}/respond")
def respond_to_invitation(
    invitation_id: int,
    action: str = Query(..., regex="^(accept|decline)$"),
    token: str = Query(...),
    session: Session = Depends(get_session),
) -> dict:
    """Endpoint public pour accepter/refuser une invitation via lien email"""
    invitation = session.get(Invitation, invitation_id)
    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation not found")
    
    # Vérifier le token (simple vérification pour demo)
    expected_accept = f"accept_{invitation.id}_{invitation.invitee_id}"
    expected_decline = f"decline_{invitation.id}_{invitation.invitee_id}"
    
    if action == "accept" and token != expected_accept:
        raise HTTPException(status_code=403, detail="Invalid token")
    if action == "decline" and token != expected_decline:
        raise HTTPException(status_code=403, detail="Invalid token")
    
    if invitation.status != InvitationStatus.PENDING:
        return {"message": "Cette invitation a déjà été traitée", "status": invitation.status.value}
    
    # Mettre à jour le statut
    old_status = invitation.status
    invitation.status = InvitationStatus.ACCEPTED if action == "accept" else InvitationStatus.DECLINED
    session.add(invitation)
    session.commit()
    session.refresh(invitation)
    
    # Notifier l'organisateur
    invitee = session.get(User, invitation.invitee_id)
    restaurant = session.get(Restaurant, invitation.restaurant_id)
    status_text = "acceptée" if invitation.status == InvitationStatus.ACCEPTED else "déclinée"
    
    # Vérifier si une notification similaire existe récemment (éviter les doubles)
    recent_notification = session.exec(
        select(Notification)
        .where(Notification.user_id == invitation.organizer_id)
        .where(Notification.type == "invitation_response")
        .where(Notification.data == str(invitation.id))
        .where(Notification.created_at > datetime.utcnow() - timedelta(minutes=5))
    ).first()
    
    if not recent_notification:
        notification = Notification(
            user_id=invitation.organizer_id,
            type="invitation_response",
            title=f"Invitation {status_text}",
            message=f"{invitee.first_name or invitee.nickname or invitee.email} a {status_text} votre invitation au restaurant {restaurant.name if restaurant else 'inconnu'}",
            data=str(invitation.id),
        )
        session.add(notification)
        session.commit()
    
    action_text = "acceptée" if action == "accept" else "refusée"
    return {
        "message": f"Invitation {action_text} avec succès",
        "status": invitation.status.value,
        "invitation_id": invitation.id
    }


@app.delete("/invitations/{invitation_id}")
def delete_invitation(
    invitation_id: int,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
) -> dict:
    invitation = session.get(Invitation, invitation_id)
    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation not found")
    if invitation.organizer_id != user.id:
        raise HTTPException(status_code=403, detail="Not organizer")
    session.delete(invitation)
    session.commit()
    return {"status": "cancelled"}


@app.get("/notifications", response_model=List[NotificationRead])
def list_notifications(
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
) -> List[Notification]:
    return list(
        session.exec(
            select(Notification)
            .where(Notification.user_id == user.id)
            .order_by(Notification.created_at.desc())
        ).all()
    )


@app.patch("/notifications/{notification_id}/read", response_model=NotificationRead)
def mark_notification_read(
    notification_id: int,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
) -> Notification:
    notification = session.get(Notification, notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    if notification.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not owner")
    notification.is_read = True
    session.add(notification)
    session.commit()
    session.refresh(notification)
    return notification


@app.delete("/invitations/{invitation_id}/clear")
def clear_invitation_for_invitee(
    invitation_id: int,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
) -> dict:
    """Permet à l'invité de supprimer une invitation de sa liste (même déclinée)"""
    invitation = session.get(Invitation, invitation_id)
    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation not found")
    if invitation.invitee_id != user.id:
        raise HTTPException(status_code=403, detail="Not invitee")
    
    # On ne supprime pas vraiment l'invitation, on marque juste comme 'cachée' pour l'invité
    # ou on peut la supprimer si le statut est DECLINED
    if invitation.status == InvitationStatus.DECLINED:
        session.delete(invitation)
    else:
        # Pour les autres statuts, on pourrait ajouter un flag 'hidden_by_invitee'
        # Pour l'instant, on autorise la suppression seulement si DECLINED
        raise HTTPException(status_code=400, detail="Can only clear declined invitations")
    
    session.commit()
    return {"status": "cleared", "invitation_id": invitation_id}


@app.delete("/notifications/{notification_id}")
def delete_notification(
    notification_id: int,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
) -> dict:
    """Supprimer une notification"""
    notification = session.get(Notification, notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    if notification.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not owner")
    
    session.delete(notification)
    session.commit()
    return {"status": "deleted", "notification_id": notification_id}


@app.delete("/notifications")
def delete_all_read_notifications(
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
) -> dict:
    """Supprimer toutes les notifications lues de l'utilisateur"""
    from sqlmodel import delete
    
    statement = delete(Notification).where(
        Notification.user_id == user.id,
        Notification.is_read == True
    )
    result = session.exec(statement)
    session.commit()
    
    return {"status": "deleted", "count": result.rowcount}
