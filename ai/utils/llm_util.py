from langchain_google_genai import ChatGoogleGenerativeAI

from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

_ = load_dotenv()

model_gemini = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    # other params...
)

model_openai = ChatOpenAI(model="gpt-4o", temperature=0)

# text_to_image_model = DallEAPIWrapper(model_name='dall-e-3')
