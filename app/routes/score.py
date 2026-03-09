from fastapi import APIRouter
from app.schemas.score_schema import ScoreRequest, ScoreResponse
from app.services.scoring_service import score_property

router = APIRouter(tags=["scoring"])

@router.post("/score", response_model=ScoreResponse)
def score(request: ScoreRequest) -> ScoreResponse:
    result = score_property(request)
    return ScoreResponse(**result)
