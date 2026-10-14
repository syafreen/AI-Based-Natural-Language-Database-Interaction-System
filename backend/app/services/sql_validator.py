from dataclasses import dataclass

import sqlglot
from sqlglot import exp


MUTATION_KEYWORDS = {
    "ALTER",
    "CREATE",
    "DELETE",
    "DROP",
    "GRANT",
    "INSERT",
    "MERGE",
    "REPLACE",
    "REVOKE",
    "TRUNCATE",
    "UPDATE",
    "VACUUM",
}


class SQLValidationError(ValueError):
    pass


@dataclass(frozen=True)
class ValidationResult:
    sql: str
    added_limit: bool


class SQLValidator:
    def __init__(self, max_limit: int = 100) -> None:
        self.max_limit = max_limit

    def validate(self, sql: str) -> ValidationResult:
        normalized = self._strip_wrappers(sql)
        statements = sqlglot.parse(normalized, read="postgres")

        if len(statements) != 1:
            raise SQLValidationError("Only a single SELECT statement is allowed.")

        statement = statements[0]
        if not isinstance(statement, exp.Select):
            raise SQLValidationError("Only SELECT queries are allowed.")

        self._reject_mutations(statement)
        added_limit = self._enforce_limit(statement)
        return ValidationResult(sql=statement.sql(dialect="postgres"), added_limit=added_limit)

    def _strip_wrappers(self, sql: str) -> str:
        value = sql.strip().rstrip(";").strip()

        if value.startswith("```"):
            lines = value.splitlines()
            if len(lines) >= 2 and lines[-1].strip() == "```":
                lines = lines[1:-1]
            if lines and lines[0].strip().lower() == "sql":
                lines = lines[1:]
            value = "\n".join(lines).strip().rstrip(";").strip()

        if not value:
            raise SQLValidationError("SQL cannot be empty.")

        upper = value.upper()
        if any(keyword in upper.split() for keyword in MUTATION_KEYWORDS):
            raise SQLValidationError("Query contains a blocked SQL operation.")

        return value

    def _reject_mutations(self, statement: exp.Expression) -> None:
        for node in statement.walk():
            if isinstance(
                node,
                (
                    exp.Delete,
                    exp.Drop,
                    exp.Insert,
                    exp.Update,
                    exp.Create,
                    exp.Alter,
                    exp.Command,
                ),
            ):
                raise SQLValidationError("Query contains a blocked SQL operation.")

    def _enforce_limit(self, statement: exp.Select) -> bool:
        limit = statement.args.get("limit")
        if limit is None:
            statement.set("limit", exp.Limit(expression=exp.Literal.number(self.max_limit)))
            return True

        limit_value = self._extract_limit(limit)
        if limit_value is None or limit_value > self.max_limit:
            statement.set("limit", exp.Limit(expression=exp.Literal.number(self.max_limit)))
            return True

        return False

    def _extract_limit(self, limit: exp.Limit) -> int | None:
        expression = limit.expression
        if isinstance(expression, exp.Literal) and expression.is_int:
            return int(expression.this)
        return None
