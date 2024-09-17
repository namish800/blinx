import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate

from langgraph.graph import StateGraph, END
from typing import TypedDict, List
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ChatMessage
from langchain_openai import ChatOpenAI
from tavily import TavilyClient

import re
from langchain.schema import BaseOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI

_ = load_dotenv()

import requests
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from bs4 import BeautifulSoup


title_generator_sys_prompt = """
You are an editor at a marketing agency. your task is to suggest the Titles for a blog post for a brand.
Follow the below guidelines:
1. Tone of the tile: {tone}
2. Generate upto {max_suggestions} of titles.
3. Make the outputs in JSON format.
"""

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    # other params...
)

messages = ChatPromptTemplate.from_messages([
    ("system", title_generator_sys_prompt),
    ("user", "{query}")])

chain = messages | llm | StrOutputParser

resp = chain.invoke({"tone": "Friendly,Enthusiastic,Informative,Approachable", "max_suggestions": "3",
                     "query": "First time pet parents"})

print(resp)
