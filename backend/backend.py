from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from ai.domain.BlogGeneratorDto import BlogGeneratorDto
from backend.models.blog_post import BlogPost  # Correct import
import uuid
from ai.orchestrator import run_blog_gen_workflow

app = FastAPI()

@app.post("/generateBlog")
async def generate_blog(request: Request):
    data = await request.json()
    blog_post = BlogPost(**data)  # Instantiate the class

    # using this for now, get this from persistance
    json_data = {
        'purpose': ['Promote and sell pet products', 'Establish an online presence for the Poochku brand',
                    'Provide information and resources for dog owners'],
        'audience': ['Dog owners', 'Potential pet owners', 'Pet enthusiasts'],
        'tone': ['Friendly', 'Enthusiastic', 'Informative', 'Approachable'],
        'emotions': ['Positive', 'Excited', 'Helpful'],
        'character': ['Enthusiastic pet enthusiast', 'Reliable source of pet products',
                      'Friendly advisor for dog owners'],
        'syntax': ['Use clear and concise sentences', 'Provide product descriptions and details',
                   'Use headings and subheadings to organize information'],
        'language': ['Simple', 'Easy to understand', 'Relatable to dog owners'],
    }

    session_id = uuid.uuid4()

    # Placeholder logic for blog post generation
    blog_data = BlogGeneratorDto(
        query=blog_post.userPrompt,
        brand_persona=json_data,
        max_suggestions=blog_post.maxSuggestions,
        max_sections=blog_post.maxSections,
        max_images=blog_post.maxImages,
        include_images=blog_post.includeImages
    )
    # You would replace this with your actual logic
    # look for a session in firebase, if not found, create a new session
    generated_content = run_blog_gen_workflow(session_id=session_id, blog_gen_dto=blog_data)
    return JSONResponse({"message": generated_content})


@app.get("/hello")
async def root():
    return {"message": "Welcome to your FastAPI Dockerized backend!"}


if __name__=="__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8080)
