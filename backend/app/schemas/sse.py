from pydantic import BaseModel

class SseRequest(BaseModel):
    question: str