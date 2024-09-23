from pydantic import BaseModel

class BrandPersona(BaseModel):
    purpose: list[str]
    audience: list[str]
    tone: list[str]
    emotions: list[str]
    character: list[str]
    syntax: list[str]
    language: list[str]
    name: str
    user_id: str