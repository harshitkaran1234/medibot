from fastapi import APIRouter

from medibot.schema.api_response import SuccessResponse

router = APIRouter()


@router.get("/health")
async def healthcheck():
    return SuccessResponse(message="healthy")
