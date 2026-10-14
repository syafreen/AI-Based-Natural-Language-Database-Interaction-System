import time
from dataclasses import dataclass
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine


@dataclass(frozen=True)
class QueryResult:
    rows: list[dict[str, Any]]
    columns: list[str]
    execution_time_ms: float


class DatabaseService:
    def __init__(self) -> None:
        self._engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker[AsyncSession] | None = None

    async def connect(self, database_url: str) -> None:
        if self._engine:
            return
        self._engine = create_async_engine(database_url, pool_pre_ping=True)
        self._session_factory = async_sessionmaker(self._engine, expire_on_commit=False)

    async def dispose(self) -> None:
        if self._engine:
            await self._engine.dispose()
        self._engine = None
        self._session_factory = None

    async def execute_select(self, sql: str, statement_timeout_ms: int) -> QueryResult:
        session_factory = self._require_session_factory()
        start = time.perf_counter()

        async with session_factory() as session:
            async with session.begin():
                await session.execute(text("SET TRANSACTION READ ONLY"))
                timeout_ms = max(1, int(statement_timeout_ms))
                await session.execute(text(f"SET LOCAL statement_timeout = {timeout_ms}"))
                result = await session.execute(text(sql))
                rows = [dict(row._mapping) for row in result.fetchall()]
                columns = list(result.keys())

        elapsed_ms = (time.perf_counter() - start) * 1000
        return QueryResult(rows=rows, columns=columns, execution_time_ms=elapsed_ms)

    async def get_schema_context(self) -> str:
        session_factory = self._require_session_factory()
        schema_sql = """
            SELECT
                table_name,
                column_name,
                data_type
            FROM information_schema.columns
            WHERE table_schema = 'public'
            ORDER BY table_name, ordinal_position
        """

        async with session_factory() as session:
            result = await session.execute(text(schema_sql))
            rows = result.fetchall()

        tables: dict[str, list[str]] = {}
        for row in rows:
            table_name = row.table_name
            column = f"{row.column_name} {row.data_type}"
            tables.setdefault(table_name, []).append(column)

        if not tables:
            return "No public tables were found."

        return "\n".join(
            f"{table_name}({', '.join(columns)})" for table_name, columns in tables.items()
        )

    def _require_session_factory(self) -> async_sessionmaker[AsyncSession]:
        if not self._session_factory:
            raise RuntimeError("Database service has not been connected.")
        return self._session_factory


db_service = DatabaseService()
