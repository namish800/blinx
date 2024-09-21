from typing import TypedDict, List, Dict


class Strategy(TypedDict):
    objective: str
    approach: List[str]


class TargetingCriteria(TypedDict):
    interests: List[str]
    behavior: List[str]


class TargetAudience(TypedDict):
    primary_segment: List[str]
    targeting_criteria: TargetingCriteria


class MessagingThemes(TypedDict):
    key_messages: List[str]
    content_themes: List[str]


class MarketingPlan(TypedDict):
    strategy: Strategy
    target_audience: TargetAudience
    messaging_themes: MessagingThemes
