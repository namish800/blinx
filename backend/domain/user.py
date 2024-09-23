from pydantic import BaseModel

class User(BaseModel):
    user_id: str = None  # Now truly optional
    name: str
    email: str