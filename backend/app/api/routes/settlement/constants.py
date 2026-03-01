from enum import Enum


class RemittanceStatus(str, Enum):
    """Status values for remittance records."""

    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
