import operator
from typing import TypedDict, List, Annotated


class AdGeneratorState(TypedDict):
    objective: str
    product_or_service_details: str
    brand_persona: dict
    campaign_plan: str
    human_feedback: str
    ad_copies: Annotated[list, operator.add]
    ad_copies_intermediate: List
    image_prompts: Annotated[list, operator.add]
    image_urls: Annotated[list, operator.add]
    suggestions: Annotated[list, operator.add]


class ImagePromptState(TypedDict):
    ad_copy: dict
    campaign_plan: str
    brand_persona: dict

