from typing import TypedDict, List


class Whiteboard(TypedDict):
    customer_data: dict
    customer_segment: dict
    brand_persona: dict
    campaign_objective: str
    campaign_details: str
    messages: dict
    channels: List
    suggested_time: str
    reason: str
    targeting_strategy: str
    email: str
    sms: str
    notification: str

