from pydantic import BaseModel

class BlogPostContinueStepsRequestArgs(BaseModel):
    session_id: str
    blog_generation_step: int
    user_prompt: str