import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import Settings, get_settings
from app.schemas.query import QueryRequest, QueryResponse
from app.services.ai_service import AIService
from app.services.db_service import DatabaseService, db_service
from app.services.sql_validator import SQLValidationError, SQLValidator

router = APIRouter(tags=["query"])
logger = logging.getLogger(__name__)


def get_db_service() -> DatabaseService:
    return db_service


def get_ai_service(settings: Settings = Depends(get_settings)) -> AIService:
    return AIService(settings)


@router.post("/query", response_model=QueryResponse, status_code=status.HTTP_200_OK)
async def query_database(
    payload: QueryRequest,
    settings: Settings = Depends(get_settings),
    database: DatabaseService = Depends(get_db_service),
    ai: AIService = Depends(get_ai_service),
) -> QueryResponse:
    validator = SQLValidator(max_limit=settings.max_query_limit)
    logger.info("query.request question=%s", payload.question)

    try:
        schema_context = await database.get_schema_context()
        generated_sql = await ai.generate_sql(payload.question, schema_context)
        logger.info("query.generated sql=%s", generated_sql)

        validation = validator.validate(generated_sql)
        logger.info("query.validation status=passed added_limit=%s sql=%s", validation.added_limit, validation.sql)

        try:
            result = await database.execute_select(
                validation.sql,
                statement_timeout_ms=settings.database_statement_timeout_ms,
            )
            final_sql = validation.sql
        except SQLAlchemyError as exc:
            logger.warning("query.execution_failed retrying=true error=%s", exc)
            repaired_sql = await ai.repair_sql(payload.question, schema_context, validation.sql, str(exc))
            repaired = validator.validate(repaired_sql)
            logger.info("query.repaired sql=%s", repaired.sql)
            result = await database.execute_select(
                repaired.sql,
                statement_timeout_ms=settings.database_statement_timeout_ms,
            )
            final_sql = repaired.sql

        summary = await ai.summarize_results(payload.question, final_sql, result.rows)

        return QueryResponse(
            question=payload.question,
            sql=final_sql,
            data=result.rows,
            columns=result.columns,
            row_count=len(result.rows),
            execution_time_ms=round(result.execution_time_ms, 2),
            summary=summary,
        )
    except SQLValidationError as exc:
        logger.warning("query.validation status=failed error=%s", exc)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except SQLAlchemyError as exc:
        logger.exception("query.database_error")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Generated SQL could not be executed safely.") from exc
    except Exception as exc:
        logger.exception("query.unhandled_error")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unable to process query.") from exc
