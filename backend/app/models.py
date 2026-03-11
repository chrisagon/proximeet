from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class Role(str, Enum):
    ADMIN = "ADMIN"
    PROXIMEETER = "PROXIMEETER"
    CONSULTANT = "CONSULTANT"


class PrivacyLevel(str, Enum):
    PRECISE = "PRECISE"
    BUBBLE = "BUBBLE"


class LocationType(str, Enum):
    CLIENT = "CLIENT"
    HOME = "HOME"


class MeetupStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class InvitationStatus(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: str = Field(primary_key=True)
    email: str = Field(index=True, unique=True)
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    dietary_restrictions: Optional[str] = None
    teams_id: Optional[str] = None
    role: Role = Role.CONSULTANT
    privacy_level: PrivacyLevel = PrivacyLevel.BUBBLE
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Presence(SQLModel, table=True):
    __tablename__ = "presence"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    latitude: float
    longitude: float
    location_type: LocationType
    expires_at: datetime = Field(index=True)  # Index ajouté pour les requêtes de nettoyage
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class Restaurant(SQLModel, table=True):
    __tablename__ = "restaurants"

    place_id: str = Field(primary_key=True)
    name: str
    address: Optional[str] = None  # Adresse complète
    latitude: Optional[float] = None  # Pour la carte
    longitude: Optional[float] = None  # Pour la carte
    cuisine_tags: Optional[str] = None
    is_official_habit: bool = False
    vote_count: int = 0
    average_rating: float = 0.0


class Recommendation(SQLModel, table=True):
    __tablename__ = "recommendations"

    id: Optional[int] = Field(default=None, primary_key=True)
    restaurant_id: str = Field(foreign_key="restaurants.place_id", index=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Meetup(SQLModel, table=True):
    __tablename__ = "meetups"

    id: Optional[int] = Field(default=None, primary_key=True)
    organizer_id: str = Field(foreign_key="users.id", index=True)
    restaurant_id: Optional[str] = Field(default=None, foreign_key="restaurants.place_id")
    radius_km: int = 1
    scheduled_at: datetime
    status: MeetupStatus = MeetupStatus.PENDING


class UserFavoriteRestaurant(SQLModel, table=True):
    __tablename__ = "user_favorite_restaurants"

    user_id: str = Field(foreign_key="users.id", primary_key=True)
    restaurant_id: str = Field(foreign_key="restaurants.place_id", primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Invitation(SQLModel, table=True):
    __tablename__ = "invitations"

    id: Optional[int] = Field(default=None, primary_key=True)
    organizer_id: str = Field(foreign_key="users.id", index=True)
    invitee_id: str = Field(foreign_key="users.id", index=True)
    restaurant_id: str = Field(foreign_key="restaurants.place_id", index=True)
    meetup_id: Optional[int] = Field(default=None, foreign_key="meetups.id")
    status: InvitationStatus = InvitationStatus.PENDING
    message: Optional[str] = None
    scheduled_at: datetime  # Date/heure du rendez-vous (OBLIGATOIRE)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Notification(SQLModel, table=True):
    __tablename__ = "notifications"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    type: str
    title: str
    message: str
    data: Optional[str] = None
    is_read: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
