# unboil-fastapi-query

Easily add advanced filtering and sorting to your FastAPI endpoints using SQLAlchemy.

## Installation

```bash
pip install unboil-fastapi-query
```

## Quick Start

1. **Define your SQLAlchemy models** as usual.
2. **Build a query model** using `build_query`:

```python
from unboil_fastapi_query import build_query, FilterOperation

ExampleQuery = build_query(
	filters={
		Example.id: FilterOperation.EQ,
		Example.name: "*",  # allow all operations
	},
	sortables=[Example.name]
)
```

3. **Use `QueryDepends` in your FastAPI endpoint**:

```python
from unboil_fastapi_query import QueryDepends

@app.get("/", response_model=list[ExampleRead])
def list(query = QueryDepends(ExampleQuery)):
	with Session(engine) as session:
		stmt = select(Example)
		stmt = apply_query(stmt, query)
		result = session.execute(stmt)
		return result.scalars().all()
```

4. **Enjoy automatic filtering and sorting** via query parameters:

- `/api?filter.name.eq=Alice`  
- `/api?sort=sort.name.asc`

## Example

See `examples/main.py` for a complete example.

## Testing

Run tests with:

```bash
pytest
```
