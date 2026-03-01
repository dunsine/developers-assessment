import uuid
from datetime import date, datetime

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=128)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)


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
    pass


# Properties to receive on item update
class ItemUpdate(ItemBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
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
    new_password: str = Field(min_length=8, max_length=128)


# Settlement Domain Models


class WorkLog(SQLModel, table=True):
    """Container for all work done on a task."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, index=True)
    task_name: str = Field(max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    time_segments: list["TimeSegment"] = Relationship(
        back_populates="worklog", cascade_delete=True
    )
    adjustments: list["Adjustment"] = Relationship(
        back_populates="worklog", cascade_delete=True
    )
    remittance_worklogs: list["RemittanceWorklog"] = Relationship(
        back_populates="worklog"
    )


class TimeSegment(SQLModel, table=True):
    """Individual recorded time entry within a worklog."""

    __tablename__ = "time_segment"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    worklog_id: uuid.UUID = Field(
        foreign_key="worklog.id", nullable=False, index=True, ondelete="CASCADE"
    )
    start_time: datetime
    end_time: datetime
    hourly_rate: float
    created_at: datetime = Field(default_factory=datetime.utcnow)

    worklog: WorkLog | None = Relationship(back_populates="time_segments")


class Adjustment(SQLModel, table=True):
    """Retroactive deduction or addition on a worklog."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    worklog_id: uuid.UUID = Field(
        foreign_key="worklog.id", nullable=False, index=True, ondelete="CASCADE"
    )
    amount: float
    reason: str = Field(max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    worklog: WorkLog | None = Relationship(back_populates="adjustments")


class Remittance(SQLModel, table=True):
    """Single monthly payout to a worker."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, index=True)
    period_start: date = Field(index=True)
    period_end: date = Field(index=True)
    total_amount: float
    status: str = Field(max_length=20, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    remittance_worklogs: list["RemittanceWorklog"] = Relationship(
        back_populates="remittance", cascade_delete=True
    )


class RemittanceWorklog(SQLModel, table=True):
    """Links worklogs to the remittance that settled them."""

    __tablename__ = "remittance_worklog"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    remittance_id: uuid.UUID = Field(
        foreign_key="remittance.id", nullable=False, index=True, ondelete="CASCADE"
    )
    worklog_id: uuid.UUID = Field(
        foreign_key="worklog.id", nullable=False, index=True
    )
    amount: float

    remittance: Remittance | None = Relationship(
        back_populates="remittance_worklogs"
    )
    worklog: WorkLog | None = Relationship(
        back_populates="remittance_worklogs"
    )
