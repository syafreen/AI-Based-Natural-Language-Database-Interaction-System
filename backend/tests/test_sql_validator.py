import pytest

from app.services.sql_validator import SQLValidationError, SQLValidator


def test_validator_allows_select_and_adds_limit():
    result = SQLValidator(max_limit=50).validate("select id, email from users")

    assert result.added_limit is True
    assert "LIMIT 50" in result.sql


def test_validator_rejects_mutation():
    with pytest.raises(SQLValidationError):
        SQLValidator().validate("delete from users")


def test_validator_clamps_large_limit():
    result = SQLValidator(max_limit=100).validate("select * from users limit 1000")

    assert "LIMIT 100" in result.sql


def test_validator_rejects_multiple_statements():
    with pytest.raises(SQLValidationError):
        SQLValidator().validate("select * from users; select * from orders")
