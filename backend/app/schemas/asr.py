from pydantic import BaseModel


class ASRTranscribeResponse(BaseModel):
    user_id: str
    text: str
    provider: str
    model: str
    mime_type: str
    file_size: int
    duration_ms: int
