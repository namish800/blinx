from typing import TypedDict, List


class BlogGeneratorState(TypedDict):
    query: str
    brand_persona: str
    max_title_suggestions: int
    generated_titles: List[str]
    selected_title: str
    introduction: str
    sections: str
    max_sections: int
    keywords: str
    generated_sections: str
    max_images: str
    include_images: bool
    img_urls: List[str]


