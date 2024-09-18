from pydantic import BaseModel

class User(BaseModel):
    id: str = None  # Now truly optional
    name: str
    email: str