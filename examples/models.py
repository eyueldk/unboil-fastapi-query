from uuid import uuid4
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped

class Base(DeclarativeBase):
    pass

class Example(Base):
    __tablename__ = "examples"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: uuid4().hex)
    name: Mapped[str] = mapped_column(String)
