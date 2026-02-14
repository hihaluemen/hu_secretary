import pytest

from app.core.exceptions import BadRequestError
from app.repositories.event_repository import EventRepository


def test_build_safe_update_sql_appends_user_scope():
    repo = EventRepository()
    safe_sql, params = repo._build_safe_update_sql(
        user_id="user_001",
        sql="UPDATE events SET location = 'A会议室' WHERE id = 12",
    )

    assert safe_sql == "UPDATE events SET location = 'A会议室' WHERE (id = 12) AND user_id = %s"
    assert params == ("user_001",)


@pytest.mark.parametrize(
    ("sql", "code"),
    [
        ("", "UPDATE_SQL_EMPTY"),
        ("UPDATE events SET location='A'; DELETE FROM events WHERE id=1", "UPDATE_SQL_MULTIPLE_STATEMENTS"),
        ("UPDATE users SET role='admin' WHERE id=1", "UPDATE_SQL_INVALID"),
        ("UPDATE events SET location='A会议室'", "UPDATE_SQL_INVALID"),
        ("UPDATE events SET location='A' WHERE id = %s", "UPDATE_SQL_PLACEHOLDER_FORBIDDEN"),
    ],
)
def test_build_safe_update_sql_rejects_unsafe_payload(sql: str, code: str):
    repo = EventRepository()

    with pytest.raises(BadRequestError) as exc_info:
        repo._build_safe_update_sql(user_id="user_001", sql=sql)

    assert exc_info.value.code == code
