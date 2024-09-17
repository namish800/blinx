from typing import TypedDict


class BlogGeneratorDto(TypedDict):
    query: str
    brand_persona: dict
    max_suggestions: int
    max_sections: int
    max_images: int
    include_images: bool


def convert_to_dict(blog_dto: BlogGeneratorDto) -> dict:
    return {
        "query": blog_dto['query'],
        "brand_persona": blog_dto['brand_persona'],
        "max_title_suggestions": 3,  # Fixed value as specified
        "max_sections": blog_dto['max_sections'],
        "max_images": blog_dto['max_images'],
        "include_images": blog_dto['include_images']
    }
