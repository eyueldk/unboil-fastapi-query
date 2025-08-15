# Helper to test filter operations
from sqlalchemy.orm import InstrumentedAttribute, Session
from unboil_fastapi_query import FilterOperation
from typing import Any, Sequence

import pytest
from unboil_fastapi_query import FilterOperation, build_query
from unboil_fastapi_query.sqlalchemy import apply_query
from sqlalchemy.orm import DeclarativeBase, mapped_column, Session, Mapped
from sqlalchemy import Integer, String, create_engine, select


class Base(DeclarativeBase):
    pass


class Example(Base):
    __tablename__ = "example"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str | None] = mapped_column(String, nullable=True)


@pytest.fixture(scope="session")
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        session.add_all(
            [
                Example(id=1, name="Alice"),
                Example(id=2, name="Bob"),
                Example(id=3, name="Alicia"),
                Example(id=4, name=None),
            ]
        )
        session.commit()
        yield session


def filter_test(
    session: Session,
    column: InstrumentedAttribute,
    operation: FilterOperation,
    value: Any,
    expected_names: Sequence[str | None],
):
    QueryModel = build_query(filters={column: [operation]})
    request = QueryModel(**{f"filter.{column.key}.{operation.value}": value})
    stmt = select(Example)
    stmt = apply_query(stmt, request)
    result = session.execute(stmt).scalars().all()
    assert {u.name for u in result} == set(expected_names)


def sort_test(
    session: Session,
    sort_column: InstrumentedAttribute,
    direction: str,
    expected_names: list[str | None],
):
    QueryModel = build_query(sortables=[sort_column])
    request = QueryModel(sort=[f"sort.{sort_column.key}.{direction}"])
    stmt = select(Example)
    stmt = apply_query(stmt, request)
    result = session.execute(stmt).scalars().all()
    names = [u.name for u in result]
    assert names == expected_names


def test_apply_query_eq(session: Session):
    filter_test(session, Example.name, FilterOperation.EQ, "Alice", ["Alice"])


def test_apply_query_eq_none(session: Session):
    filter_test(session, Example.name, FilterOperation.EQ, None, [None])


def test_apply_query_neq(session: Session):
    filter_test(session, Example.name, FilterOperation.NEQ, "Alice", ["Bob", "Alicia"])


def test_apply_query_neq_none(session: Session):
    filter_test(
        session, Example.name, FilterOperation.NEQ, None, ["Alice", "Bob", "Alicia"]
    )


def test_apply_query_lt(session: Session):
    filter_test(session, Example.id, FilterOperation.LT, 2, ["Alice"])


def test_apply_query_gt(session: Session):
    filter_test(session, Example.id, FilterOperation.GT, 2, ["Alicia", None])


def test_apply_query_lte(session: Session):
    filter_test(session, Example.id, FilterOperation.LTE, 2, ["Alice", "Bob"])


def test_apply_query_gte(session: Session):
    filter_test(session, Example.id, FilterOperation.GTE, 2, ["Bob", "Alicia", None])


def test_apply_query_like(session: Session):
    filter_test(session, Example.name, FilterOperation.LIKE, "Ali", ["Alice", "Alicia"])


def test_apply_query_ilike(session: Session):
    filter_test(
        session, Example.name, FilterOperation.ILIKE, "ali", ["Alice", "Alicia"]
    )


def test_apply_query_startswith(session: Session):
    filter_test(
        session, Example.name, FilterOperation.STARTSWITH, "Ali", ["Alice", "Alicia"]
    )


def test_apply_query_endswith(session: Session):
    filter_test(session, Example.name, FilterOperation.ENDSWITH, "cia", ["Alicia"])


def test_apply_query_in(session: Session):
    filter_test(
        session, Example.name, FilterOperation.IN, ["Alice", None], ["Alice", None]
    )


def test_apply_query_not_in(session: Session):
    filter_test(
        session,
        Example.name,
        FilterOperation.NOT_IN,
        ["Alice", None],
        ["Alicia", "Bob"],
    )


def test_sort_by_name_asc(session: Session):
    sort_test(session, Example.name, "asc", [None, "Alice", "Alicia", "Bob"])


def test_sort_by_name_desc(session: Session):
    sort_test(session, Example.name, "desc", ["Bob", "Alicia", "Alice", None])
