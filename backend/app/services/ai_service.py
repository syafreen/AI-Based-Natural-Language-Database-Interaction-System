from openai import AsyncOpenAI

from app.core.config import Settings


class AIService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = AsyncOpenAI(
            api_key=settings.openai_api_key or "not-configured",
            base_url=settings.openai_base_url,
        )

    async def generate_sql(self, question: str, schema_context: str) -> str:
        prompt = self._sql_prompt(question, schema_context)
        response = await self.client.chat.completions.create(
            model=self.settings.openai_model,
            temperature=self.settings.ai_temperature,
            messages=[
                {
                    "role": "system",
                    "content": "You are a careful PostgreSQL SQL generator. Return only SQL.",
                },
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content or ""

    async def summarize_results(
        self,
        question: str,
        sql: str,
        rows: list[dict],
    ) -> str | None:
        if not self.settings.enable_ai_summary or not rows:
            return None

        sample_rows = rows[:10]
        response = await self.client.chat.completions.create(
            model=self.settings.openai_model,
            temperature=0.2,
            messages=[
                {
                    "role": "system",
                    "content": "Summarize SQL query results for a business user in one concise paragraph.",
                },
                {
                    "role": "user",
                    "content": (
                        f"Question: {question}\n"
                        f"SQL: {sql}\n"
                        f"Rows sample: {sample_rows}\n"
                        "Explain the answer without mentioning internal implementation details."
                    ),
                },
            ],
        )
        return response.choices[0].message.content

    async def repair_sql(
        self,
        question: str,
        schema_context: str,
        failed_sql: str,
        error: str,
    ) -> str:
        prompt = (
            f"{self._sql_prompt(question, schema_context)}\n\n"
            "The previous SQL failed.\n"
            f"Failed SQL:\n{failed_sql}\n\n"
            f"Database error:\n{error}\n\n"
            "Return a corrected SELECT-only PostgreSQL query."
        )
        response = await self.client.chat.completions.create(
            model=self.settings.openai_model,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": "You repair PostgreSQL SELECT queries. Return only SQL.",
                },
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content or ""

    def _sql_prompt(self, question: str, schema_context: str) -> str:
        return (
            "You are a SQL generator.\n"
            "Only return valid PostgreSQL SQL.\n"
            "Only use SELECT.\n"
            "Never modify data.\n"
            "Use only tables and columns present in the schema.\n"
            f"Always include LIMIT {self.settings.max_query_limit} or smaller.\n\n"
            "Schema:\n"
            f"{schema_context}\n\n"
            "User request:\n"
            f"{question}\n\n"
            "Return ONLY SQL, no explanation."
        )
