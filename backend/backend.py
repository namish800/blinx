import uuid

import firebase_admin
from fastapi import FastAPI, Request, Body, HTTPException
from fastapi.responses import JSONResponse
from firebase_admin import firestore, credentials

from ai.domain.BlogGeneratorDto import BlogGeneratorDto
from ai.orchestrator import run_blog_gen_workflow
from backend.models.blog_post import BlogPost  # Correct import
from backend.models.brand_persona import BrandPersona
from backend.models.user import User

app = FastAPI()

# Path to your JSON key file (make sure it's the absolute path)
cred = credentials.Certificate("blinx-63185-firebase-adminsdk-qv7yr-737cbb7829.json")

# Initialize Firebase Admin SDK *first*
firebase_admin.initialize_app(cred)

# Now create the Firestore client
client = firestore.Client()


@app.post("/createUser")
async def create_user(user: User):
    """
    Creates a new user document in the 'users' collection.
    Firestore will automatically generate a unique ID for each user.
    """
    doc_ref = client.collection("users").document()
    user.id = doc_ref.id  # Get the generated ID
    doc_ref.set(user.dict())

    return {"message": "User created successfully", "user": user}


@app.get("/users/{user_id}")
async def get_user(user_id: str):
    doc_ref = client.collection("users").document(user_id)
    user_data = doc_ref.get().to_dict()

    print(user_data)
    # Create a User object from the retrieved data
    user = User(**user_data)  # Initialize a User object using the data

    return user


@app.post("/createBrandPersona")
async def create_brand_persona(brand_persona: BrandPersona = Body(...)):
    # Convert BrandPersona object to a dictionary
    brand_persona_data = brand_persona.dict()

    # Add the data to the 'brand-persona' collection
    doc_ref = client.collection("brand-persona").document()
    doc_ref.set(brand_persona_data)
    return {"message": "Brand persona created successfully"}


@app.post("/generateBlog")
async def generate_blog(request: Request):
    data = await request.json()
    blog_post = BlogPost(**data)  # Instantiate the class

    docs = client.collection("brand-persona").where("user_id", "==", blog_post.user_id).stream()
    brand_persona = next(docs, None)
    if brand_persona is None:
        raise HTTPException(status_code=404, detail="No brand persona found for this user.")

    session_id = uuid.uuid4().__str__()

    # Placeholder logic for blog post generation
    blog_data = BlogGeneratorDto(
        query=blog_post.user_prompt,
        brand_persona=brand_persona,
        max_suggestions=blog_post.max_suggestions,
        max_sections=blog_post.max_sections,
        max_images=blog_post.max_images,
        include_images=blog_post.include_images
    )
    # You would replace this with your actual logic
    # look for a session in firebase, if not found, create a new session
    generated_content = run_blog_gen_workflow(session_id=session_id, blog_gen_dto=blog_data)
    return JSONResponse({"message": generated_content})


@app.get("/hello")
async def root():
    return {"message": "Welcome to your FastAPI Dockerized backend!"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8080)
