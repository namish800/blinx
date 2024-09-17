from pydantic import BaseModel

class BlogPost(BaseModel):
    userId: int
    userPrompt: str
    maxSuggestions: int
    maxSections: int
    maxImages: int
    includeImages: bool