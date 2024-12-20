import json
import os
import shutil
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed

import firebase_admin
import pandas as pd
import requests
from fastapi import FastAPI, Body, HTTPException, BackgroundTasks, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.params import Query
from fastapi.responses import JSONResponse
from firebase_admin import firestore, credentials
from firebase_admin import storage

from ai.ad_gen_orchestrator import AdGenOrchestrator
from ai.agents.facebook_ad_gen.domain.ad_gen_dto import AdGenDto
from ai.agents.instagram_post_gen.domain.post_gen_dto import PostGenDto
from ai.brand_persona_orchestrator import BrandPersonaOrchestrator
from ai.domain.BlogGeneratorDto import BlogGeneratorDto
from ai.instagram_post_gen_orchestrator import InstagramPostGenOrchestrator
from ai.orchestrator import run_blog_gen_workflow
from ai.personalized_marketing_orchestrator import PersonalizedMarketingOrchestrator
from ai.video_to_blog_orchestrator import VideoToBlogOrchestrator
from backend.domain.ad_generation_request_args import AdGenerationRequestArgs, InstagramPostRequestArgs, \
    MarketingPostRequestArgs
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
firebase_admin.initialize_app(cred, {"storageBucket": "blinx-63185.appspot.com"})

# Now create the Firestore client
client = firestore.client()
executor = ThreadPoolExecutor(max_workers=5)
bucket = storage.bucket('blinx-63185.appspot.com')


@app.post("/uploadCSV")
async def upload_csv(
        file: UploadFile = File(...),
        user_id: str = Form(...)  # Take user_id as a form field
):
    """Uploads a CSV file to Firebase Storage, ensuring only one file per user (upsert).

    Args:
        file (UploadFile): The CSV file to upload.
        user_id (str): The ID of the authenticated user.

    Returns:
        JSONResponse: A JSON response containing information about the uploaded file.
    """

    # 1. Check if user exists (Implement your own validation)
    user_ref = client.collection('users').document(user_id)
    user_doc = user_ref.get()

    if not user_doc.exists:
        raise HTTPException(status_code=401, detail="No user found.")

    # 2. Get the bucket and generate a filename
    file_name = f"{user_id}_{file.filename}_{uuid.uuid4()}.csv"  # Use user ID for organization

    # 3. Check if a file already exists for this user
    existing_blob = bucket.blob(file_name)
    if existing_blob.exists():
        # Delete the existing file
        existing_blob.delete()

    # 4. Read the contents of the CSV file
    file_contents = await file.read()

    # 5. Upload the file to Firebase Storage
    blob = bucket.blob(file_name)
    blob.upload_from_string(file_contents)
    blob.make_public()
    print(blob.public_url)
    return JSONResponse(
        content={"message": "CSV file uploaded successfully."},
        status_code=200
    )


@app.get("/getCSVFiles")
async def get_csv_files(
        user_id: str = Query(...)
):
    """Retrieves all CSV files for a given user from Firebase Storage.

    Args:
        user_id (str): The ID of the authenticated user.

    Returns:
        JSONResponse: A JSON response containing a list of URLs for the user's CSV files.
    """

    user_ref = client.collection('users').document(user_id)
    user_doc = user_ref.get()

    if not user_doc.exists:
        raise HTTPException(status_code=401, detail="No user found.")

    # 3. Fetch all files with the user ID prefix
    blobs = bucket.list_blobs(prefix=f"{user_id}")

    # 4. Build a list of public URLs
    file_objects = [
        {"file_url": blob.public_url, "file_name": blob.name} for blob in blobs
    ]

    return JSONResponse(
        content={"message": "CSV files retrieved successfully.", "files": file_objects},
        status_code=200
    )


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
    user_ref = client.collection('users').document(user_id)
    user_doc = user_ref.get()

    if not user_doc.exists:
        raise HTTPException(status_code=404, detail="No user found.")
    # Create a User object from the retrieved data
    user = User(**user_doc.to_dict())  # Initialize a User object using the data

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

    # Check if a brand persona already exists for the user
    brand_persona_query = client.collection('brand-persona').where('user_id', '==', brand_persona_request.user_id).get()

    if brand_persona_query:
        # If the brand persona exists, update the existing document
        doc_ref = brand_persona_query[0].reference
        doc_ref.update(brand_persona.dict())
    else:
        # If no brand persona exists, create a new document
        doc_ref = client.collection('brand-persona').document()
        doc_ref.set(brand_persona.dict())

    return {"brand_persona": brand_persona}


@app.post("/generateBlog")
async def generate_blog(blog_post_request_args: BlogPostRequestArgs = Body(...)):
    brand_persona = get_brand_persona_from_firestore(blog_post_request_args.user_id)
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
    brand_persona = get_brand_persona_from_firestore(ad_gen_request_args.user_id)
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
    brand_persona = get_brand_persona_from_firestore(instagram_post_request_args.user_id)
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
        video_ref = client.collection('video-processor-status').document(session_id).set(
            {"session_id": session_id, "status": "completed", "result": analysis_result})

        # Remove the video after processing
        os.remove(video_path)

    except Exception as e:
        # Handle any errors and update the status
        video_ref = client.collection('video-processor-status').document(session_id).set(
            {"session_id": session_id, "status": "failed", "error": str(e)})


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
def analyse_video(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    session_id = uuid.uuid4().__str__()
    video_ref = client.collection('video-processor-status').document(session_id).set(
        {"session_id": session_id, "status": "processing", "result": None})
    try:
        # video_path = download_video(video_url)
        if not os.path.exists("temp/videos"):
            os.makedirs("temp/videos")

        video_path = f"temp/videos/{session_id}_{file.filename}"

        # Save the uploaded file to the temporary path
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        print("Video Path : " + video_path)

        # Add the video processing task to the background
        background_tasks.add_task(process_video_background, video_path, session_id)

        return JSONResponse(content={"session_id": session_id, "status": "processing"})

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error downloading video: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing video: {e}")


@app.get("/taskStatus/{session_id}")
def check_task_status(session_id: str):
    docs = client.collection("video-processor-status").where("session_id", "==", session_id).stream()
    video_processor_status = next(docs, None)
    if video_processor_status is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return JSONResponse(content=video_processor_status.to_dict())


@app.get("/getBrandPersona")
def get_brand_persona(user_id: str):
    return get_brand_persona_from_firestore(user_id).to_dict()


@app.get("/hello")
async def root():
    return {"message": "Welcome to your FastAPI Dockerized backend!"}


def process_chunk(chunk, session_id, brand_persona, marketing_post_request_args):
    orchestrator = PersonalizedMarketingOrchestrator()
    responses = []
    for _, row in chunk.iterrows():
        # Convert each row to a dictionary for easier processing
        row_dict = row.to_dict()
        # Run the personalized marketing workflow for each customer data row
        orchestrator_session = uuid.uuid4().__str__()
        response = orchestrator.run_workflow(
            session_id=orchestrator_session,
            brand_persona=brand_persona,
            objective=marketing_post_request_args.objective,
            details=marketing_post_request_args.details,
            customer_data=row_dict
        )
        # Append the response to the list of responses
        responses.append(response)
    return responses


def process_df(session_id, marketing_post_request_args: MarketingPostRequestArgs, path_to_csv):
    brand_persona = get_brand_persona_from_firestore(marketing_post_request_args.user_id).to_dict()
    futures = []
    responses = []
    result_df = None
    # Read the CSV file in chunks to handle large datasets without using too much memory
    with ThreadPoolExecutor(max_workers=5) as exec1:
        for chunk in pd.read_csv(path_to_csv, chunksize=2):
            # Submit each chunk for parallel processing
            futures.append(
                exec1.submit(process_chunk, chunk, session_id, brand_persona, marketing_post_request_args))

        # Collect the results as they complete
        for future in as_completed(futures):
            responses.extend(future.result())

    result_list = []
    # Extracting data
    for resp in responses:
        segment_name = resp["state"]["customer_segment"][0]["segment_name"]
        name = resp["state"]["customer_data"]["name"]
        user_id = resp["state"]["customer_data"]["user_id"]
        contact_email = resp["state"]["customer_data"]["email"]
        channels = ','.join(resp["state"]["channels"])
        sms_content = resp["state"].get("sms", "")
        email_content = resp["state"]["email"].get("body", "")
        email_subject = resp["state"]["email"].get("subject", "")
        notification = resp["state"].get("notification", "")
        suggested_time = resp["state"]["suggested_time"]
        strategy_reasoning = resp['state']['targeting_strategy']['reasoning']
        comm_channel_reasoning = resp['state']['reason']

        # Create DataFrame
        data = {
            "segment_name": segment_name,
            "name": name,
            "user_id": user_id,
            "contact_email": contact_email,
            "channel": channels,
            "SMS": sms_content,
            "email_body": email_content,
            "email_subject": email_subject,
            "notification": notification,
            "suggested_time": suggested_time,
            "strategy_reasoning": strategy_reasoning,
            "comm_channel_reasoning": comm_channel_reasoning

        }

        result_list += [data]

    result_df = pd.DataFrame(result_list)
    result_csv_path = f'temp/files/result_{session_id}.csv'
    result_df.to_csv(result_csv_path, index=False)
    bucket = storage.bucket()
    result_blob = bucket.blob(f'results/result_{session_id}.csv')
    result_blob.upload_from_filename(result_csv_path)

    result_blob.make_public()

    # Update the status to "completed" and store the result URL in Firestore
    result_url = result_blob.public_url

    os.remove(result_csv_path)

    return result_url


# def process_df(session_id, marketing_post_request_args: MarketingPostRequestArgs, path_to_csv):
#     orchestrator = PersonalizedMarketingOrchestrator()
#     responses = []
#     brand_persona = get_brand_persona_from_firestore(marketing_post_request_args.user_id)
#     for chunk in pd.read_csv(path_to_csv, chunksize=100):
#         for _, row in chunk.iterrows():
#             row_dict = row.to_dict()
#             response = orchestrator.run_workflow(session_id=session_id, brand_persona=brand_persona.to_dict(),
#                                                  objective=marketing_post_request_args.objective,
#                                                  details=marketing_post_request_args.details,
#                                                  customer_data=row_dict)
#             responses.append(response)
#
#     return responses


def process_df_background(session_id, path_to_csv, marketing_post_request_args: MarketingPostRequestArgs):
    try:
        analysis_result = process_df(session_id, marketing_post_request_args, path_to_csv)

        # Update the status to "completed" and store the result
        csv_ref = client.collection('csv-processor-status').document(session_id).set(
            {"session_id": session_id, "status": "completed", "result": analysis_result})

        # Remove the video after processing
        os.remove(path_to_csv)

    except Exception as e:
        print(e)
        # Handle any errors and update the status
        video_ref = client.collection('csv-processor-status').document(session_id).set(
            {"session_id": session_id, "status": "failed", "error": str(e)})


@app.post("/personalized_marketing")
def analyze_customers(background_tasks: BackgroundTasks,
                      marketing_post_request_args: MarketingPostRequestArgs = Body(...)):
    session_id = uuid.uuid4().__str__()
    csv_ref = client.collection('csv-processor-status').document(session_id).set(
        {"session_id": session_id, "status": "processing", "result": None})

    # file_location='user_attribures.csv'
    bucket = storage.bucket()
    blob = bucket.blob(marketing_post_request_args.file_name)

    unique_id = str(uuid.uuid4())
    if not os.path.exists("temp/files"):
        os.makedirs("temp/files")
    path_to_csv = f'temp/files/test_{unique_id}.csv'
    blob.download_to_filename(path_to_csv)
    try:
        df = pd.read_csv(path_to_csv)
        df_size_5 = df.head(5)

        df_size_5.to_csv(path_to_csv)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading CSV file: {e}")

    background_tasks.add_task(process_df_background, session_id, path_to_csv, marketing_post_request_args)
    return JSONResponse(content={"session_id": session_id, "status": "processing"})


@app.get("/poll-csv/{session_id}")
def get_csv_result(session_id: str):
    docs = client.collection("csv-processor-status").where("session_id", "==", session_id).stream()
    csv_processor_status = next(docs, None)
    if csv_processor_status is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return JSONResponse(content=csv_processor_status.to_dict())


def get_brand_persona_from_firestore(user_id: str):
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
