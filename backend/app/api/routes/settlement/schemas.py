import uuid
from datetime import date, datetime

from pydantic import BaseModel, field_validator


class TimeSegmentResponse(BaseModel):
    """Response model for a time segment."""

    id: uuid.UUID
    worklog_id: uuid.UUID
    start_time: datetime
    end_time: datetime
    hourly_rate: float
    created_at: datetime

    @field_validator("id")
    @classmethod
    def validate_id(cls, v: uuid.UUID) -> uuid.UUID:
        if v is None:
            raise ValueError("id is required")
        return v

    @field_validator("worklog_id")
    @classmethod
    def validate_worklog_id(cls, v: uuid.UUID) -> uuid.UUID:
        if v is None:
            raise ValueError("worklog_id is required")
        return v

    @field_validator("start_time")
    @classmethod
    def validate_start_time(cls, v: datetime) -> datetime:
        if v is None:
            raise ValueError("start_time is required")
        return v

    @field_validator("end_time")
    @classmethod
    def validate_end_time(cls, v: datetime) -> datetime:
        if v is None:
            raise ValueError("end_time is required")
        return v

    @field_validator("hourly_rate")
    @classmethod
    def validate_hourly_rate(cls, v: float) -> float:
        if v is None:
            raise ValueError("hourly_rate is required")
        if v < 0:
            raise ValueError("hourly_rate cannot be negative")
        return v

    @field_validator("created_at")
    @classmethod
    def validate_created_at(cls, v: datetime) -> datetime:
        if v is None:
            raise ValueError("created_at is required")
        return v


class AdjustmentResponse(BaseModel):
    """Response model for an adjustment."""

    id: uuid.UUID
    worklog_id: uuid.UUID
    amount: float
    reason: str
    created_at: datetime

    @field_validator("id")
    @classmethod
    def validate_id(cls, v: uuid.UUID) -> uuid.UUID:
        if v is None:
            raise ValueError("id is required")
        return v

    @field_validator("worklog_id")
    @classmethod
    def validate_worklog_id(cls, v: uuid.UUID) -> uuid.UUID:
        if v is None:
            raise ValueError("worklog_id is required")
        return v

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: float) -> float:
        if v is None:
            raise ValueError("amount is required")
        return round(v, 2)

    @field_validator("reason")
    @classmethod
    def validate_reason(cls, v: str) -> str:
        if v is None:
            raise ValueError("reason is required")
        v = v.strip()
        if len(v) == 0:
            raise ValueError("reason cannot be empty")
        if len(v) > 500:
            raise ValueError("reason too long")
        return v

    @field_validator("created_at")
    @classmethod
    def validate_created_at(cls, v: datetime) -> datetime:
        if v is None:
            raise ValueError("created_at is required")
        return v


class WorkLogResponse(BaseModel):
    """Response model for a worklog with computed amount."""

    id: uuid.UUID
    user_id: uuid.UUID
    task_name: str
    amount: float
    time_segments: list[TimeSegmentResponse]
    adjustments: list[AdjustmentResponse]
    created_at: datetime
    updated_at: datetime

    @field_validator("id")
    @classmethod
    def validate_id(cls, v: uuid.UUID) -> uuid.UUID:
        if v is None:
            raise ValueError("id is required")
        return v

    @field_validator("user_id")
    @classmethod
    def validate_user_id(cls, v: uuid.UUID) -> uuid.UUID:
        if v is None:
            raise ValueError("user_id is required")
        return v

    @field_validator("task_name")
    @classmethod
    def validate_task_name(cls, v: str) -> str:
        if v is None:
            raise ValueError("task_name is required")
        v = v.strip()
        if len(v) == 0:
            raise ValueError("task_name cannot be empty")
        if len(v) > 500:
            raise ValueError("task_name too long")
        return v

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: float) -> float:
        if v is None:
            raise ValueError("amount is required")
        return round(v, 2)

    @field_validator("created_at")
    @classmethod
    def validate_created_at(cls, v: datetime) -> datetime:
        if v is None:
            raise ValueError("created_at is required")
        return v

    @field_validator("updated_at")
    @classmethod
    def validate_updated_at(cls, v: datetime) -> datetime:
        if v is None:
            raise ValueError("updated_at is required")
        return v


class WorkLogsResponse(BaseModel):
    """Response model for list of worklogs."""

    data: list[WorkLogResponse]
    count: int

    @field_validator("data")
    @classmethod
    def validate_data(cls, v: list) -> list:
        if v is None:
            raise ValueError("data is required")
        return v

    @field_validator("count")
    @classmethod
    def validate_count(cls, v: int) -> int:
        if v is None:
            raise ValueError("count is required")
        if v < 0:
            raise ValueError("count cannot be negative")
        return v


class RemittanceWorklogResponse(BaseModel):
    """Response model for a remittance-worklog link."""

    id: uuid.UUID
    worklog_id: uuid.UUID
    amount: float

    @field_validator("id")
    @classmethod
    def validate_id(cls, v: uuid.UUID) -> uuid.UUID:
        if v is None:
            raise ValueError("id is required")
        return v

    @field_validator("worklog_id")
    @classmethod
    def validate_worklog_id(cls, v: uuid.UUID) -> uuid.UUID:
        if v is None:
            raise ValueError("worklog_id is required")
        return v

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: float) -> float:
        if v is None:
            raise ValueError("amount is required")
        return round(v, 2)


class RemittanceResponse(BaseModel):
    """Response model for a remittance."""

    id: uuid.UUID
    user_id: uuid.UUID
    period_start: date
    period_end: date
    total_amount: float
    status: str
    remittance_worklogs: list[RemittanceWorklogResponse]
    created_at: datetime
    updated_at: datetime

    @field_validator("id")
    @classmethod
    def validate_id(cls, v: uuid.UUID) -> uuid.UUID:
        if v is None:
            raise ValueError("id is required")
        return v

    @field_validator("user_id")
    @classmethod
    def validate_user_id(cls, v: uuid.UUID) -> uuid.UUID:
        if v is None:
            raise ValueError("user_id is required")
        return v

    @field_validator("period_start")
    @classmethod
    def validate_period_start(cls, v: date) -> date:
        if v is None:
            raise ValueError("period_start is required")
        return v

    @field_validator("period_end")
    @classmethod
    def validate_period_end(cls, v: date) -> date:
        if v is None:
            raise ValueError("period_end is required")
        return v

    @field_validator("total_amount")
    @classmethod
    def validate_total_amount(cls, v: float) -> float:
        if v is None:
            raise ValueError("total_amount is required")
        return round(v, 2)

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        if v is None:
            raise ValueError("status is required")
        v = v.strip()
        valid = {"PENDING", "SUCCESS", "FAILED", "CANCELLED"}
        if v not in valid:
            raise ValueError(f"status must be one of {valid}")
        return v

    @field_validator("created_at")
    @classmethod
    def validate_created_at(cls, v: datetime) -> datetime:
        if v is None:
            raise ValueError("created_at is required")
        return v

    @field_validator("updated_at")
    @classmethod
    def validate_updated_at(cls, v: datetime) -> datetime:
        if v is None:
            raise ValueError("updated_at is required")
        return v


class GenerateRemittancesResponse(BaseModel):
    """Response model for the generate remittances endpoint."""

    processed: int
    total: int
    remittances: list[RemittanceResponse]

    @field_validator("processed")
    @classmethod
    def validate_processed(cls, v: int) -> int:
        if v is None:
            raise ValueError("processed is required")
        if v < 0:
            raise ValueError("processed cannot be negative")
        return v

    @field_validator("total")
    @classmethod
    def validate_total(cls, v: int) -> int:
        if v is None:
            raise ValueError("total is required")
        if v < 0:
            raise ValueError("total cannot be negative")
        return v
