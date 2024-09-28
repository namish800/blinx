import operator
from typing import Annotated, TypedDict, List


class InstagramPostState(TypedDict):
    objective: str
    brand_persona: dict
    max_posts: int
    include_images: bool
    include_hashtags: bool
    captions: List
    hashtags: Annotated[list, operator.add]
    image_prompts: Annotated[list, operator.add]
    image_urls: Annotated[list, operator.add]


class HashtagGeneratorState(TypedDict):
    caption: str
