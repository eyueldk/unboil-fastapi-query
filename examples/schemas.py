
from pydantic import BaseModel
from .models import Example

class ExampleCreate(BaseModel):
    name: str
    
class ExampleRead(BaseModel):
    id: str
    name: str