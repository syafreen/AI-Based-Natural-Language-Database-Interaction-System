from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=1000)


class QueryResponse(BaseModel):
    question: str
    sql: str
    data: list[dict]
    columns: list[str]
    row_count: int
    execution_time_ms: float
    summary: str | None = None


class ErrorResponse(BaseModel):
    detail: str
