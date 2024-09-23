from pydantic import BaseModel

class BrandPersonaRequest(BaseModel):
    user_id: str
    brand_url: str