import json
import os
import uuid

import firebase_admin
import requests
from fastapi import FastAPI, Body, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from firebase_admin import firestore, credentials

from ai.ad_gen_orchestrator import AdGenOrchestrator
from ai.agents.facebook_ad_gen.domain.ad_gen_dto import AdGenDto
from ai.agents.instagram_post_gen.domain.post_gen_dto import PostGenDto
from ai.brand_persona_orchestrator import BrandPersonaOrchestrator
from ai.domain.BlogGeneratorDto import BlogGeneratorDto
from ai.instagram_post_gen_orchestrator import InstagramPostGenOrchestrator
from ai.orchestrator import run_blog_gen_workflow
from ai.video_to_blog_orchestrator import VideoToBlogOrchestrator
from backend.domain.ad_generation_request_args import AdGenerationRequestArgs, InstagramPostRequestArgs
from backend.domain.blog_post_continue_steps_request_args import BlogPostContinueStepsRequestArgs
from backend.domain.blog_post_request_args import BlogPostRequestArgs
from backend.domain.brand_persona import BrandPersona
from backend.domain.brand_persona_request_args import BrandPersonaRequestArgs
from backend.domain.enums.ad_generation_steps import AdGenerationSteps
from backend.domain.enums.blog_generation_steps import BlogGenerationSteps
from backend.domain.enums.operations import Operations
from backend.domain.session_context import SessionContext
from backend.domain.user import User

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

firestore_credentials_string = os.environ["FIRESTORE_CREDENTIALS"]
# Path to your JSON key file (make sure it's the absolute path)
firestore_credentials = json.loads(firestore_credentials_string)
cred = credentials.Certificate(firestore_credentials)

# Initialize Firebase Admin SDK *first*
firebase_admin.initialize_app(cred)

# Now create the Firestore client
client = firestore.client()


@app.post("/createUser")
async def create_user(user: User):
    """
    Creates a new user document in the 'users' collection.
    Firestore will automatically generate a unique ID for each user.
    """
    # Generate a unique user ID
    user_id = str(uuid.uuid4())  # Use UUID for uniqueness

    # Create user in Firestore (using user_id as document ID)
    user.user_id = user_id  # Get the generated ID
    user_ref = client.collection('users').document(user_id).set(user.dict())

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
async def create_brand_persona(brand_persona_request: BrandPersonaRequestArgs = Body(...)):
    # Check if user exists in Firestore
    user_ref = client.collection('users').document(brand_persona_request.user_id)
    user_doc = user_ref.get()

    if not user_doc.exists:
        raise HTTPException(status_code=401, detail="No user found.")

    # 2. Generate Brand Persona
    brand_persona_orchestrator = BrandPersonaOrchestrator()
    created_brand_persona = brand_persona_orchestrator.generate_brand_persona(brand_persona_request.brand_url)

    # 3. Map to BrandPersona Class
    brand_persona = BrandPersona(
        purpose=created_brand_persona['purpose'],
        audience=created_brand_persona['audience'],
        tone=created_brand_persona['tone'],
        emotions=created_brand_persona['emotions'],
        character=created_brand_persona['character'],
        syntax=created_brand_persona['syntax'],
        language=created_brand_persona['language'],
        name=created_brand_persona['name'],  # Assuming a default name
        user_id=brand_persona_request.user_id
    )

    # Add data to Firestore
    doc_ref = client.collection('brand-persona').document()
    doc_ref.set(brand_persona.dict())

    return {"message": "Brand persona created successfully"}


@app.post("/generateBlog")
async def generate_blog(blog_post_request_args: BlogPostRequestArgs = Body(...)):
    brand_persona = get_brand_persona(blog_post_request_args.user_id)
    session_id = uuid.uuid4().__str__()

    # Placeholder logic for blog post generation
    blog_data = BlogGeneratorDto(
        query=blog_post_request_args.user_prompt,
        brand_persona=brand_persona.to_dict(),
        max_suggestions=blog_post_request_args.max_suggestions,
        max_sections=blog_post_request_args.max_sections,
        max_images=blog_post_request_args.max_images,
        include_images=blog_post_request_args.include_images
    )

    generated_content = run_blog_gen_workflow(session_id=session_id, blog_gen_dto=blog_data)
    save_session(Operations.BLOG_GENERATION, blog_post_request_args.user_id, session_id)

    return JSONResponse({"session_id": session_id, "message": generated_content})


@app.post("/resumeBlogGeneration")
async def resume_blog_generation(blog_post_continue_request_args: BlogPostContinueStepsRequestArgs = Body(...)):
    # check for active session
    validate_session(blog_post_continue_request_args.session_id, Operations.BLOG_GENERATION)

    return_item = None
    if blog_post_continue_request_args.blog_generation_step == BlogGenerationSteps.SECTIONS.value:
        return_item = run_blog_gen_workflow(session_id=blog_post_continue_request_args.session_id,
                                            title=blog_post_continue_request_args.user_prompt)

    if blog_post_continue_request_args.blog_generation_step == BlogGenerationSteps.FINAL_REVIEW.value:
        sections = json.loads(blog_post_continue_request_args.user_prompt)
        print(sections)
        return_item = run_blog_gen_workflow(session_id=blog_post_continue_request_args.session_id, sections=sections)

    print(return_item)
    return JSONResponse({"session_id": blog_post_continue_request_args.session_id, "step_output": return_item})


@app.post("/generateAd")
async def generate_ad(ad_gen_request_args: AdGenerationRequestArgs = Body(...)):
    session_id = None
    brand_persona = get_brand_persona(ad_gen_request_args.user_id)
    return_item = None
    orchestrator = AdGenOrchestrator()
    if ad_gen_request_args.ad_gen_step == AdGenerationSteps.REQUEST:
        session_id = uuid.uuid4().__str__()
        ad_data = AdGenDto(objective=ad_gen_request_args.ad_objective,
                           details=ad_gen_request_args.ad_details,
                           brand_persona=brand_persona.to_dict())
        return_item = orchestrator.run_ad_gen_workflow(session_id=session_id, ad_gen_dto=ad_data)
        save_session(Operations.AD_GENERATION, ad_gen_request_args.user_id, session_id)
    elif ad_gen_request_args.ad_gen_step == AdGenerationSteps.REVIEW:
        # check for active session
        validate_session(ad_gen_request_args.session_id, Operations.AD_GENERATION)
        session_id = ad_gen_request_args.session_id
        no_feedback = "no feedback"
        if ad_gen_request_args.human_feedback == no_feedback:
            return_item = orchestrator.run_ad_gen_workflow(session_id=ad_gen_request_args.session_id,
                                                           human_feedback=None)
        else:
            return_item = orchestrator.run_ad_gen_workflow(session_id=ad_gen_request_args.session_id,
                                                           human_feedback=ad_gen_request_args.human_feedback)

    return JSONResponse({"session_id": session_id, "step_output": return_item})


@app.post("/generateInstagramPost")
async def generate_instagram_post(instagram_post_request_args: InstagramPostRequestArgs = Body(...)):
    session_id = uuid.uuid4().__str__()
    orchestrator = InstagramPostGenOrchestrator()
    brand_persona = get_brand_persona(instagram_post_request_args.user_id)
    instagram_post_data = PostGenDto(objective=instagram_post_request_args.objective,
                                     brand_persona=brand_persona.to_dict(),
                                     max_posts=instagram_post_request_args.max_posts,
                                     include_images=instagram_post_request_args.include_images)
    return_item = orchestrator.run_instagram_post_gen_workflow(session_id=session_id,
                                                               instagram_post_dto=instagram_post_data)
    save_session(Operations.INSTAGRAM_POST_GENERATION, instagram_post_request_args.user_id, session_id)
    return JSONResponse({"session_id": session_id, "step_output": return_item})


tasks_status = {}


def process_video_background(video_path: str, session_id: str):
    try:
        # Process the video (placeholder for your actual processing code)
        analysis_result = process_video(video_path, session_id)

        # Update the status to "completed" and store the result
        tasks_status[session_id]['status'] = 'completed'
        tasks_status[session_id]['result'] = analysis_result

        # Remove the video after processing
        os.remove(video_path)

    except Exception as e:
        # Handle any errors and update the status
        tasks_status[session_id]['status'] = 'failed'
        tasks_status[session_id]['error'] = str(e)


def process_video(video_path, session_id):
    """
    This function will contain your video processing logic.
    Replace this with your actual implementation.
    """
    # Your video processing code here
    orchestrator = VideoToBlogOrchestrator()
    resp = orchestrator.run(video_path, session_id)

    return resp


@app.post("/analyseVideo")
def analyse_video(video_url: str, background_tasks: BackgroundTasks):
    session_id = uuid.uuid4().__str__()
    tasks_status[session_id] = {"status": "processing", "result": None}
    try:
        # # 1. Download video from URL
        # response = requests.get(video_url, stream=True)
        # response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        #
        # # Create 'temp' directory if it doesn't exist
        # if not os.path.exists("videos"):
        #     os.makedirs("videos")
        #
        # # Generate unique filename to avoid conflicts
        # unique_filename = session_id + ".mp4"
        # video_path = os.path.join("videos", unique_filename)  # Assuming 'temp' directory exists
        video_path = "D:\\work\\AI\\marketingAI\\BlogGenerator\\testVideo.mp4"
        print("Video Path : " + video_path)

        # with open(video_path, 'wb') as f:
        #     for chunk in response.iter_content(chunk_size=8192):
        #         f.write(chunk)

        # Add the video processing task to the background
        background_tasks.add_task(process_video_background, video_path, session_id)

        # 4. Return the analysis
        return JSONResponse(content={"session_id": session_id, "status": "processing"})

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error downloading video: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing video: {e}")


@app.get("/taskStatus/{session_id}")
def check_task_status(session_id: str):
    if session_id not in tasks_status:
        return JSONResponse(status_code=404, content={"error": "Task not found"})

    status_info = tasks_status[session_id]
    return JSONResponse(content=status_info)


@app.get("/hello")
async def root():
    return {"message": "Welcome to your FastAPI Dockerized backend!"}


def get_brand_persona(user_id: str):
    docs = client.collection("brand-persona").where("user_id", "==", user_id).stream()
    brand_persona = next(docs, None)
    if brand_persona is None:
        raise HTTPException(status_code=404, detail="No brand persona found for this user.")

    return brand_persona


def save_session(operation: Operations, user_id: str, session_id: str):
    session_context_ref = client.collection("session-context").document()
    session_context = SessionContext(
        user_id=user_id,
        session_id=session_id,
        operation=operation.value
    )
    session_context_ref.set(session_context.dict())


def validate_session(session_id: str, operation: Operations):
    docs = client.collection("session-context").where("session_id", "==",
                                                      session_id).stream()
    session_context = next(docs, None)
    if session_context is None:
        raise HTTPException(status_code=404, detail="No active session.")
    # TODO: add validation on operation as well
