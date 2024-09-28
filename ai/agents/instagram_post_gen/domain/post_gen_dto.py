from typing import TypedDict


class PostGenDto(TypedDict):
    objective: str
    brand_persona: dict
    max_posts: int
    include_images: bool


def convert_to_dict(post_dto: PostGenDto) -> dict:
    return {
        "objective": post_dto['objective'],
        "brand_persona": post_dto['brand_persona'],
        "max_posts": post_dto['max_posts'],
        "include_images": post_dto['include_images']
    }