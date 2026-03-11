from datetime import datetime
from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, EmailStr, Field

from .models import InvitationStatus, LocationType, MeetupStatus, PrivacyLevel, Role


T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    skip: int
    limit: int
    has_more: bool


class UserRead(BaseModel):
    id: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    dietary_restrictions: Optional[str] = None
    teams_id: Optional[str] = None
    role: Role
    privacy_level: PrivacyLevel


class UserSignup(BaseModel):
    email: EmailStr
    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)
    nickname: Optional[str] = None
    password: Optional[str] = None
    avatar_url: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: Optional[str] = None


class UserUpdate(BaseModel):
    dietary_restrictions: Optional[str] = None
    privacy_level: Optional[PrivacyLevel] = None
    avatar_url: Optional[str] = None


class AuthResponse(BaseModel):
    user: UserRead
    token: str


class PresenceCreate(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    location_type: LocationType
    expires_in_hours: Optional[int] = Field(None, ge=1, le=72)


class PresenceRead(BaseModel):
    user_id: str
    latitude: float
    longitude: float
    location_type: LocationType
    expires_at: datetime
    last_updated: datetime


class NearbyResult(BaseModel):
    user_id: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    nickname: Optional[str] = None
    role: Role
    privacy_level: PrivacyLevel
    distance_km: float = Field(..., ge=0)
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class RestaurantCreate(BaseModel):
    place_id: str
    name: str
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    cuisine_tags: Optional[str] = None
    is_official_habit: bool = False


class RestaurantRead(BaseModel):
    place_id: str
    name: str
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    cuisine_tags: Optional[str] = None
    is_official_habit: bool
    vote_count: int
    average_rating: float


class RecommendationCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None


class RecommendationRead(BaseModel):
    id: int
    restaurant_id: str
    user_id: str
    rating: int
    comment: Optional[str]
    created_at: datetime


class MeetupCreate(BaseModel):
    restaurant_id: Optional[str] = None
    radius_km: int = Field(1, ge=1)
    scheduled_at: datetime


class MeetupUpdate(BaseModel):
    status: MeetupStatus


class MeetupRead(BaseModel):
    id: int
    organizer_id: str
    restaurant_id: Optional[str]
    radius_km: int
    scheduled_at: datetime
    status: MeetupStatus


class FavoriteRestaurantRead(BaseModel):
    restaurant: RestaurantRead
    created_at: datetime


class InvitationCreate(BaseModel):
    invitee_id: str
    restaurant_id: str
    meetup_id: Optional[int] = None
    message: Optional[str] = None
    scheduled_at: datetime  # Date/heure du rendez-vous (OBLIGATOIRE)


class InvitationUpdate(BaseModel):
    status: InvitationStatus


class InvitationRead(BaseModel):
    id: int
    organizer_id: str
    invitee_id: str
    restaurant_id: str
    meetup_id: Optional[int]
    status: InvitationStatus
    message: Optional[str]
    scheduled_at: datetime  # Obligatoire
    created_at: datetime


class InvitationReadWithDetails(BaseModel):
    id: int
    organizer_id: str
    organizer_name: str
    organizer_email: str
    invitee_id: str
    restaurant_id: str
    restaurant_name: str
    meetup_id: Optional[int]
    status: InvitationStatus
    message: Optional[str]
    scheduled_at: datetime  # Obligatoire
    created_at: datetime


class NotificationRead(BaseModel):
    id: int
    user_id: str
    type: str
    title: str
    message: str
    data: Optional[str] = None
    is_read: bool
    created_at: datetime
