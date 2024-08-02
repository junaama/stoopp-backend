from datetime import datetime
import uuid
from typing import List, Optional
from pydantic import AnyUrl, EmailStr
from sqlmodel import Field, Relationship, SQLModel, JSON, Column


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    items: list["Item"] = Relationship(back_populates="owner")


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Shared properties
class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Properties to receive on item creation
class ItemCreate(ItemBase):
    title: str = Field(min_length=1, max_length=255)


# Properties to receive on item update
class ItemUpdate(ItemBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(max_length=255)
    owner_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)
    owner: User | None = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)

class ListingBase(SQLModel):
    title: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = Field(default=None, max_length=255)
    price: Optional[float] = Field(default=None)
    category: Optional[str] = Field(default=None, max_length=255)
    location: Optional[str] = Field(default=None, max_length=255)
    images: Optional[List[AnyUrl]] = Field(default=None, sa_column=Column(JSON))  # Use JSON type for images
    class Config:
        arbitrary_types_allowed = True

class ListingCreate(ListingBase):
    pass

class ListingUpdate(SQLModel):
    title: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = Field(default=None, max_length=255)
    price: Optional[float] = Field(default=None)
    category: Optional[str] = Field(default=None, max_length=255)
    location: Optional[str] = Field(default=None, max_length=255)
    images: Optional[List[AnyUrl]] = Field(default=None, sa_column=Column(JSON))
    class Config:
        arbitrary_types_allowed = True

class Listing(ListingBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)

class ListingPublic(ListingBase):
    id: uuid.UUID
    owner_id: uuid.UUID

class ListingsPublic(SQLModel):
    data: List[ListingPublic]
    count: int


class TransactionBase(SQLModel):
    listing_id: uuid.UUID
    renter_id: uuid.UUID
    lender_id: uuid.UUID
    start_date: datetime
    end_date: datetime
    total_price: float
    status: str  # e.g., "pending", "approved", "completed", "canceled"

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(SQLModel):
    status: Optional[str] = None
    total_price: Optional[float] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class Transaction(TransactionBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

class TransactionPublic(TransactionBase):
    id: uuid.UUID

class TransactionsPublic(SQLModel):
    data: list[TransactionPublic]
    count: int

class ListingSearch(SQLModel):
    title: Optional[str] = None
    category: Optional[str] = None
    location: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None

class MessageBase(SQLModel):
    sender_id: uuid.UUID
    receiver_id: uuid.UUID
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class MessageCreate(MessageBase):
    pass

class Message(MessageBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

class MessagePublic(MessageBase):
    id: uuid.UUID

class ReviewBase(SQLModel):
    reviewer_id: uuid.UUID
    reviewee_id: uuid.UUID
    listing_id: uuid.UUID
    rating: float
    comment: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ReviewCreate(ReviewBase):
    pass

class Review(ReviewBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

class ReviewPublic(ReviewBase):
    id: uuid.UUID

class NotificationBase(SQLModel):
    user_id: uuid.UUID
    title: str
    message: str
    is_read: bool = Field(default=False)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class NotificationCreate(NotificationBase):
    pass

class Notification(NotificationBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

class NotificationPublic(NotificationBase):
    id: uuid.UUID

class NotificationsPublic(SQLModel):
    data: list[NotificationPublic]
    count: int

class ReportBase(SQLModel):
    reporter_id: uuid.UUID
    reported_user_id: uuid.UUID
    listing_id: Optional[uuid.UUID] = None
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(default="pending")  # e.g., "pending", "resolved", "dismissed"

class ReportCreate(ReportBase):
    pass

class ReportUpdate(SQLModel):
    status: Optional[str] = None

class Report(ReportBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

class ReportPublic(ReportBase):
    id: uuid.UUID

class ReportsPublic(SQLModel):
    data: list[ReportPublic]
    count: int