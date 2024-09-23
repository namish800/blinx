from pydantic import BaseModel

class BlogPost(BaseModel):
    user_id: str
    user_prompt: str
    max_suggestions: int
    max_sections: int
    max_images: int
    include_images: bool