from pydantic import BaseModel

from backend.domain.enums.ad_generation_steps import AdGenerationSteps


class AdGenerationRequestArgs(BaseModel):
    user_id: str
    ad_objective: str
    ad_details: str
    human_feedback: str
    ad_gen_step: AdGenerationSteps
    session_id: str

class InstagramPostRequestArgs(BaseModel):
    user_id: str
    objective: str
    max_posts: int
    include_images: bool
