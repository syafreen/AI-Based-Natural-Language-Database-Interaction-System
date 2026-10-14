import pytest
from httpx import ASGITransport, AsyncClient

from app.api.routes.query import get_ai_service, get_db_service
from app.core.config import Settings, get_settings
from app.main import app
from app.services.db_service import QueryResult


class FakeAIService:
    async def generate_sql(self, question: str, schema_context: str) -> str:
        return "select id, email from users"

    async def repair_sql(self, question: str, schema_context: str, failed_sql: str, error: str) -> str:
        return "select id, email from users limit 10"

    async def summarize_results(self, question: str, sql: str, rows: list[dict]) -> str:
        return "One user matched the request."


class FakeDatabaseService:
    async def get_schema_context(self) -> str:
        return "users(id integer, email text)"

    async def execute_select(self, sql: str, statement_timeout_ms: int) -> QueryResult:
        return QueryResult(
            rows=[{"id": 1, "email": "ada@example.com"}],
            columns=["id", "email"],
            execution_time_ms=2.5,
        )


def override_settings() -> Settings:
    return Settings(
        environment="test",
        openai_api_key="test",
        max_query_limit=25,
        enable_ai_summary=True,
    )


@pytest.mark.asyncio
async def test_query_endpoint_returns_validated_sql_and_rows():
    app.dependency_overrides[get_settings] = override_settings
    app.dependency_overrides[get_ai_service] = lambda: FakeAIService()
    app.dependency_overrides[get_db_service] = lambda: FakeDatabaseService()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/query", json={"question": "show users"})

    app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["sql"] == "SELECT id, email FROM users LIMIT 25"
    assert body["row_count"] == 1
    assert body["data"][0]["email"] == "ada@example.com"
