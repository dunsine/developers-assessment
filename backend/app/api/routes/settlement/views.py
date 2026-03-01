from typing import Any

from fastapi import APIRouter, Query

from app.api.deps import SessionDep
from app.api.routes.settlement import schemas as settlement_schemas
from app.api.routes.settlement.service import SettlementService

router = APIRouter(prefix="/settlement", tags=["settlement"])


@router.post(
    "/generate-remittances-for-all-users",
    response_model=settlement_schemas.GenerateRemittancesResponse,
    status_code=201,
)
def generate_remittances(session: SessionDep) -> Any:
    """Generate remittances for all users based on eligible work."""
    return SettlementService.generate_remittances(session)


@router.get(
    "/list-all-worklogs",
    response_model=settlement_schemas.WorkLogsResponse,
)
def list_all_worklogs(
    session: SessionDep,
    remittanceStatus: str | None = Query(
        default=None, description="Filter: REMITTED or UNREMITTED"
    ),
) -> Any:
    """List all worklogs with optional remittance status filter."""
    return SettlementService.list_all_worklogs(session, remittanceStatus)
