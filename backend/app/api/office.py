"""Back-office router — lead queue, metrics, assignment, model retrain."""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.core.db import get_session
from app.models.models import User
from app.schemas.schemas import (
    LeadAssignReq,
    LeadAssignResp,
    LeadResp,
    MetricsResp,
    RetrainResp,
)
from app.security.auth import get_current_user, require_role
from app.services.admin_service import AdminService
from app.services.services import MetricsService, ModelService

router = APIRouter(tags=["office"])


def _lead_resp(lead, current_user: User) -> LeadResp:
    if current_user.role == "partner":
        return LeadResp(
            lead_id=lead.lead_id,
            business_name=lead.business_name,
            business_type=lead.business_type,
            segment=lead.segment,
            city=lead.city,
            language=lead.preferred_language,
            bundle_drafted="",
            propensity_score=0,
            reasons=[],
            ai_summary="",
            suggested_action="",
            stage=lead.stage_reached,
            drop_reason=lead.drop_reason,
            has_gstin="***MASKED***",
        )
    return LeadResp(
        lead_id=lead.lead_id,
        business_name=lead.business_name,
        business_type=lead.business_type,
        segment=lead.segment,
        city=lead.city,
        language=lead.preferred_language,
        bundle_drafted="",
        propensity_score=0,
        reasons=[],
        ai_summary="",
        suggested_action="",
        stage=lead.stage_reached,
        drop_reason=lead.drop_reason,
        has_gstin=lead.has_gstin,
    )


@router.get("/leads", response_model=list[LeadResp])
def leads(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    service = AdminService(session)
    leads = service.list_leads(
        actor_user_id=current_user.user_id,
        actor_role=current_user.role,
    )
    return [_lead_resp(lead, current_user) for lead in leads]


@router.get("/metrics", response_model=MetricsResp)
def metrics(
    session: Session = Depends(get_session),
    _=Depends(require_role(["sales", "partner", "admin"])),
):
    service = MetricsService(session)
    return service.get_metrics()


@router.post("/leads/{lead_id}/assign", response_model=LeadAssignResp)
def assign_lead(
    lead_id: str,
    req: LeadAssignReq,
    session: Session = Depends(get_session),
    _=Depends(require_role(["sales", "partner", "admin"])),
):
    service = MetricsService(session)
    result = service.assign_lead(lead_id, req.assignee, req.type)
    if not result:
        raise HTTPException(status_code=404, detail="Lead not found")
    return LeadAssignResp(**result)


@router.post("/model/retrain", response_model=RetrainResp)
def retrain_model(
    session: Session | None = Depends(get_session),
    _=Depends(require_role(["admin"])),
):
    if session is None:
        from app.core.db import engine as _engine
        session = Session(_engine)
    service = ModelService(session)
    return service.retrain()


