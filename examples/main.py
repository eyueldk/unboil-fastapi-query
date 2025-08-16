from fastapi import FastAPI
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session


from .schemas import ExampleCreate, ExampleRead
from .models import Base, Example
from unboil_fastapi_query import FilterOperation, QueryDepends, build_query
from unboil_fastapi_query.sqlalchemy import apply_query


engine = create_engine("sqlite:///db.sqlite", echo=False)
Base.metadata.create_all(engine)

app = FastAPI()

@app.post("/", response_model=ExampleRead)
def create(request: ExampleCreate):
    with Session(engine, expire_on_commit=False) as session:
        example = Example(**request.model_dump(exclude_unset=True))
        session.add(example)
        session.commit()
        return example

ExampleQuery = build_query(
    filters={
        Example.id: FilterOperation.EQ,
        Example.name: "*",
    },
    sortables=[
        Example.name,
    ],
    max_results=200
)

@app.get("/", response_model=list[ExampleRead])
def list(
    query = QueryDepends(ExampleQuery)
):
    with Session(engine) as session:
        stmt = select(Example)
        stmt = apply_query(stmt, query)
        result = session.execute(stmt)
        return result.scalars().all()