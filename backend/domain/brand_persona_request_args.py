from pydantic import BaseModel

class BrandPersonaRequestArgs(BaseModel):
    user_id: str
    brand_url: str