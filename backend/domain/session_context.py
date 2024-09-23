from pydantic import BaseModel

from backend.domain.enums.operations import Operations


class SessionContext(BaseModel):
    user_id: str
    session_id: str
    operation: int
