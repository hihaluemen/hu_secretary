from fastapi import APIRouter

from app.schemas.assistant import AssistantProcessRequest, AssistantProcessResponse
from app.services.assistant_service import AssistantService

router = APIRouter(prefix="/assistant", tags=["assistant"])


@router.post("/process", response_model=AssistantProcessResponse)
def process(req: AssistantProcessRequest) -> AssistantProcessResponse:
    service = AssistantService()
    result = service.process(user_id=req.user_id, text=req.text, dry_run=req.dry_run)
    return AssistantProcessResponse(**result)
