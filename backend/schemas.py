from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2000)
    symbol: str | None = Field(default=None, max_length=24)
    top_k: int = Field(default=5, ge=1, le=10)

class WatchlistRequest(BaseModel):
    symbol: str = Field(min_length=1, max_length=24)
