from fastapi import APIRouter, File, Form, UploadFile

from app.core.config import get_settings
from app.core.exceptions import BadRequestError
from app.schemas.asr import ASRTranscribeResponse
from app.services.asr_service import ASRService

router = APIRouter(prefix="/asr", tags=["asr"])

ALLOWED_AUDIO_TYPES = {
    "audio/mpeg",
    "audio/mp3",
    "audio/wav",
    "audio/x-wav",
    "audio/webm",
    "audio/mp4",
    "audio/m4a",
}


@router.post("/transcribe", response_model=ASRTranscribeResponse)
async def transcribe_audio(
    file: UploadFile = File(...),
    user_id: str = Form(default="user_001"),
) -> ASRTranscribeResponse:
    settings = get_settings()

    raw_mime_type = (file.content_type or "").strip().lower()
    mime_type = raw_mime_type.split(";", 1)[0].strip()
    if mime_type not in ALLOWED_AUDIO_TYPES:
        raise BadRequestError(message=f"不支持的音频类型: {raw_mime_type}", code="ASR_UNSUPPORTED_MIME")

    audio_bytes = await file.read()
    if not audio_bytes:
        raise BadRequestError(message="音频文件为空", code="ASR_EMPTY_AUDIO")

    max_size = settings.ASR_MAX_FILE_SIZE_MB * 1024 * 1024
    if len(audio_bytes) > max_size:
        raise BadRequestError(
            message=f"音频文件过大，限制 {settings.ASR_MAX_FILE_SIZE_MB}MB",
            code="ASR_FILE_TOO_LARGE",
        )

    result = ASRService().transcribe(audio_bytes=audio_bytes, mime_type=mime_type)
    return ASRTranscribeResponse(
        user_id=user_id,
        text=str(result["text"]),
        provider=str(result["provider"]),
        model=str(result["model"]),
        mime_type=mime_type,
        file_size=len(audio_bytes),
        duration_ms=int(result["duration_ms"]),
    )
