from enum import StrEnum
from typing import Literal, Optional
from fastapi import Depends, Query
from pydantic import BaseModel, Field, create_model
from sqlalchemy.orm import InstrumentedAttribute, ColumnProperty

__all__ = [
    "QueryRequest",
    "QueryDepends",
    "FilterOperation",
    "SortOrder",
    "build_query",
]

QueryRequest = BaseModel

def QueryDepends(model: type[BaseModel]) -> BaseModel:
    def f(query = Query()):
        return query
    f.__annotations__["query"] = model 
    return Depends(f)

class FilterOperation(StrEnum):
    EQ = "eq"
    NEQ = "neq"
    LT = "lt"
    GT = "gt"
    LTE = "lte"
    GTE = "gte"
    LIKE = "like"
    ILIKE = "ilike"
    STARTSWITH = "startswith"
    ENDSWITH = "endswith"
    IN = "in"
    NOT_IN = "not_in"


class SortOrder(StrEnum):
    ASC = "asc"
    DESC = "desc"


def build_query(
    filters: dict[InstrumentedAttribute, Literal["*"] | FilterOperation | list[FilterOperation]] = {},
    sortables: list[InstrumentedAttribute] = [],
) -> type[QueryRequest]:

    field_definitions = {}

    # add filters
    for attr, operations in filters.items():
        
        if operations == "*":
            operations = [op for op in FilterOperation]
        elif isinstance(operations, FilterOperation):
            operations = [operations]
            
        for operation in operations:
            if isinstance(attr.property, ColumnProperty):
                field_name = f"filter.{attr.key}.{operation.value}"
                if operation in [FilterOperation.IN, FilterOperation.NOT_IN]:
                    field_definitions[field_name] = (
                        list[Optional[attr.property.columns[0].type.python_type]],
                        Field(default=None),
                    )
                else:
                    field_definitions[field_name] = (
                        Optional[attr.property.columns[0].type.python_type],
                        Field(default=None),
                    )

    # add sorting
    options: list[str] = []
    for attr in sortables:
        options.append(f"{attr.key}.{SortOrder.ASC.value}")
        options.append(f"{attr.key}.{SortOrder.DESC.value}")
    if options:
        field_definitions["sort"] = (
            list[Literal[*options]],
            Field(default_factory=list, json_schema_extra={"uniqueItems": True}),
        )

    return create_model(
        "QueryRequest", 
        __base__=QueryRequest,
        **field_definitions
    )
