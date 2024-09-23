from typing import TypedDict, List


class AdGeneratorState(TypedDict):
    objective: str
    product_or_service_details: str
    brand_persona: dict
    campaign_plan: str
    human_feedback: str
    ad_copies: List
