from typing import TypeVar, assert_never
from pydantic import BaseModel
from sqlalchemy import Select
from unboil_fastapi_query import FilterOperation, SortOrder


__all__ = [
    "apply_query"
]

T = TypeVar("T")

def apply_query(statement: Select[tuple[T]], query: BaseModel):
    dump = query.model_dump(exclude_unset=True)
    for field, value in dump.items():

        if field.startswith("filter."):
            tail = field.removeprefix("filter.")
            attr_key, order_value = tail.rsplit(".", 1)
            operation = FilterOperation(order_value)
            column = statement.selected_columns.get(attr_key)
            if column is None:
                continue
            if operation == FilterOperation.EQ:
                statement = statement.where(column == value)
            elif operation == FilterOperation.NEQ:
                statement = statement.where(column != value)
            elif operation == FilterOperation.LT:
                statement = statement.where(column < value)
            elif operation == FilterOperation.GT:
                statement = statement.where(column > value)
            elif operation == FilterOperation.LTE:
                statement = statement.where(column <= value)
            elif operation == FilterOperation.GTE:
                statement = statement.where(column >= value)
            elif operation == FilterOperation.LIKE:
                statement = statement.where(column.like(f"%{value}%"))
            elif operation == FilterOperation.ILIKE:
                statement = statement.where(column.ilike(f"%{value}%"))
            elif operation == FilterOperation.STARTSWITH:
                statement = statement.where(column.startswith(value))
            elif operation == FilterOperation.ENDSWITH:
                statement = statement.where(column.endswith(value))
            elif operation == FilterOperation.IN:
                if None not in value:
                    statement = statement.where(column.in_(value))
                else:
                    statement = statement.where(column.in_(value) | column.is_(None))
            elif operation == FilterOperation.NOT_IN:
                statement = statement.where(
                    column.notin_([v for v in value if v is not None])
                )
                if None in value:
                    statement = statement.where(column.isnot(None))
            else:
                assert_never(operation)

        elif field == "sort":
            assert isinstance(value, list) and all(
                isinstance(v, str) for v in value
            ), "Sort must be a list of strings"
            for sort_value in value:
                sort_value: str = sort_value
                attr_key, order_value = sort_value.rsplit(".", 1)
                sort_order = SortOrder(order_value)
                column = statement.selected_columns.get(attr_key)
                if column is None:
                    continue
                if sort_order == SortOrder.ASC:
                    statement = statement.order_by(column.asc())
                elif sort_order == SortOrder.DESC:
                    statement = statement.order_by(column.desc())
                else:
                    assert_never(sort_order)

        elif field == "offset":
            statement = statement.offset(value)

        elif field == "limit":
            statement = statement.limit(value)

    return statement
