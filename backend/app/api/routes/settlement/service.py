import logging
import uuid
from datetime import date, datetime

from sqlmodel import Session, select

from app.api.routes.settlement import constants as settlement_constants
from app.api.routes.settlement import schemas as settlement_schemas
from app.models import (
    Adjustment,
    Remittance,
    RemittanceWorklog,
    TimeSegment,
    User,
    WorkLog,
)

logger = logging.getLogger(__name__)


class SettlementService:
    @staticmethod
    def calc_wl_amt(session: Session, wl_id: uuid.UUID) -> float:
        """
        wl_id: worklog id
        Returns total amount for a worklog (time segments + adjustments).
        """
        segs = session.exec(
            select(TimeSegment).where(TimeSegment.worklog_id == wl_id)
        ).all()

        t = 0.0
        for s in segs:
            hrs = (s.end_time - s.start_time).total_seconds() / 3600
            t += hrs * s.hourly_rate

        adjs = session.exec(
            select(Adjustment).where(Adjustment.worklog_id == wl_id)
        ).all()

        for a in adjs:
            t += a.amount

        return round(t, 2)

    @staticmethod
    def get_unremitted_wls(session: Session, u_id: uuid.UUID) -> list[WorkLog]:
        """
        u_id: user id
        Returns worklogs not yet linked to a SUCCESS remittance.
        """
        all_wls = session.exec(
            select(WorkLog).where(WorkLog.user_id == u_id)
        ).all()

        unremitted = []
        for wl in all_wls:
            rw_links = session.exec(
                select(RemittanceWorklog).where(
                    RemittanceWorklog.worklog_id == wl.id
                )
            ).all()

            is_remitted = False
            for rw in rw_links:
                rm = session.get(Remittance, rw.remittance_id)
                if rm and rm.status == settlement_constants.RemittanceStatus.SUCCESS:
                    is_remitted = True
                    break

            if not is_remitted:
                unremitted.append(wl)

        return unremitted

    @staticmethod
    def generate_remittances(
        session: Session,
    ) -> settlement_schemas.GenerateRemittancesResponse:
        """Generate remittances for all users with unremitted worklogs."""
        users = session.exec(select(User)).all()
        results: list[settlement_schemas.RemittanceResponse] = []
        total = len(users)
        now = datetime.utcnow()
        p_start = date(now.year, now.month, 1)
        p_end = date(now.year, now.month, now.day)

        for usr in users:
            try:
                wls = SettlementService.get_unremitted_wls(session, usr.id)
                if not wls:
                    continue

                ttl = 0.0
                wl_amounts: list[tuple[WorkLog, float]] = []
                for wl in wls:
                    amt = SettlementService.calc_wl_amt(session, wl.id)
                    ttl += amt
                    wl_amounts.append((wl, amt))

                rm = Remittance(
                    user_id=usr.id,
                    period_start=p_start,
                    period_end=p_end,
                    total_amount=round(ttl, 2),
                    status=settlement_constants.RemittanceStatus.PENDING,
                )
                session.add(rm)
                session.commit()
                session.refresh(rm)

                rw_responses: list[settlement_schemas.RemittanceWorklogResponse] = []
                for wl, amt in wl_amounts:
                    rw = RemittanceWorklog(
                        remittance_id=rm.id,
                        worklog_id=wl.id,
                        amount=round(amt, 2),
                    )
                    session.add(rw)
                    session.commit()
                    session.refresh(rw)

                    rw_responses.append(
                        settlement_schemas.RemittanceWorklogResponse(
                            id=rw.id,
                            worklog_id=rw.worklog_id,
                            amount=rw.amount,
                        )
                    )

                rm.status = settlement_constants.RemittanceStatus.SUCCESS
                rm.updated_at = datetime.utcnow()
                session.add(rm)
                session.commit()
                session.refresh(rm)

                results.append(
                    settlement_schemas.RemittanceResponse(
                        id=rm.id,
                        user_id=rm.user_id,
                        period_start=rm.period_start,
                        period_end=rm.period_end,
                        total_amount=rm.total_amount,
                        status=rm.status,
                        remittance_worklogs=rw_responses,
                        created_at=rm.created_at,
                        updated_at=rm.updated_at,
                    )
                )
            except Exception as e:
                logger.error(f"Failed to generate remittance for user {usr.id}: {e}")
                session.rollback()
                continue

        return settlement_schemas.GenerateRemittancesResponse(
            processed=len(results),
            total=total,
            remittances=results,
        )

    @staticmethod
    def list_all_worklogs(
        session: Session, remittance_status: str | None = None
    ) -> settlement_schemas.WorkLogsResponse:
        """
        List worklogs with optional filtering by remittance status.
        remittance_status: REMITTED or UNREMITTED
        """
        all_wls = session.exec(select(WorkLog)).all()
        wl_responses: list[settlement_schemas.WorkLogResponse] = []

        for wl in all_wls:
            try:
                rw_links = session.exec(
                    select(RemittanceWorklog).where(
                        RemittanceWorklog.worklog_id == wl.id
                    )
                ).all()

                is_remitted = False
                for rw in rw_links:
                    rm = session.get(Remittance, rw.remittance_id)
                    if rm and rm.status == settlement_constants.RemittanceStatus.SUCCESS:
                        is_remitted = True
                        break

                if remittance_status == "REMITTED" and not is_remitted:
                    continue
                if remittance_status == "UNREMITTED" and is_remitted:
                    continue

                amt = SettlementService.calc_wl_amt(session, wl.id)

                segs = session.exec(
                    select(TimeSegment).where(TimeSegment.worklog_id == wl.id)
                ).all()
                seg_responses = [
                    settlement_schemas.TimeSegmentResponse(
                        id=s.id,
                        worklog_id=s.worklog_id,
                        start_time=s.start_time,
                        end_time=s.end_time,
                        hourly_rate=s.hourly_rate,
                        created_at=s.created_at,
                    )
                    for s in segs
                ]

                adjs = session.exec(
                    select(Adjustment).where(Adjustment.worklog_id == wl.id)
                ).all()
                adj_responses = [
                    settlement_schemas.AdjustmentResponse(
                        id=a.id,
                        worklog_id=a.worklog_id,
                        amount=a.amount,
                        reason=a.reason,
                        created_at=a.created_at,
                    )
                    for a in adjs
                ]

                wl_responses.append(
                    settlement_schemas.WorkLogResponse(
                        id=wl.id,
                        user_id=wl.user_id,
                        task_name=wl.task_name,
                        amount=amt,
                        time_segments=seg_responses,
                        adjustments=adj_responses,
                        created_at=wl.created_at,
                        updated_at=wl.updated_at,
                    )
                )
            except Exception as e:
                logger.error(f"Failed to process worklog {wl.id}: {e}")
                continue

        return settlement_schemas.WorkLogsResponse(
            data=wl_responses,
            count=len(wl_responses),
        )
