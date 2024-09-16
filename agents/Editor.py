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
from prompts.title_gen import title_generator_sys_prompt, section_header_generator_sys_prompts, \
    section_header_generator_user_prompts, add_creatives_sys_prompt, add_creatives_user_prompt, \
    keyword_generator_sys_prompt
from utils.llm_util import model, model_openai


class Editor:
    def __init__(self):
        self.model = model_openai

    def get_titles(self, blog_generator_state: dict):
        prompt_template = ChatPromptTemplate.from_messages(
            [("system", title_generator_sys_prompt), ("user", "{query}")]
        )
        parser = JsonOutputParser()
        print("Generating Titles")
        chain = prompt_template | self.model | parser
        response = chain.invoke({"tone": blog_generator_state.get("brand_persona").tone,
                                 "max_suggestions": blog_generator_state.get("max_title_suggestions"),
                                 "audience": blog_generator_state.get("brand_persona").audience,
                                 "query": blog_generator_state.get("query"),
                                 "keywords": blog_generator_state.get("keywords"),
                                 "format_example": """
                                        ```json
                                            {
                                              "titles": [
                                                "Title 1",
                                                "Title 2",
                                                "Title 3"
                                              ]
                                            }
                                        ```
                                  """})

        return {"generated_titles": response['titles']}

    def get_keywords(self, blog_generator_state: dict):
        prompt_template = ChatPromptTemplate.from_messages(
            [("user", keyword_generator_sys_prompt)]
        )
        parser = JsonOutputParser()

        chain = prompt_template | self.model | parser
        print("Searching for keywords")
        response = chain.invoke({
                                 "topic": blog_generator_state.get("query"),
                                 "format_example": """
                                        ```json
                                            {
                                              "keywords": [
                                                "Keyword 1",
                                                "Keyword 2",
                                                "Keyword 3"
                                              ]
                                            }
                                        ```
                                  """})
        return {"keywords": response['keywords']}

    def generate_section_headers(self, blog_generator_state: dict):
        prompt_template = ChatPromptTemplate.from_messages(
            [("system", section_header_generator_sys_prompts),
             ("user", section_header_generator_user_prompts)]
        )
        parser = JsonOutputParser()

        print("Generating Sections")
        chain = prompt_template | self.model | parser
        response = chain.invoke({"tone": blog_generator_state.get("brand_persona").tone,
                                 "max_sections": blog_generator_state.get("max_sections"),
                                 "audience": blog_generator_state.get("brand_persona").audience,
                                 "title": blog_generator_state.get("selected_title"),
                                 "introduction": blog_generator_state.get("introduction"),
                                 "keywords": blog_generator_state.get("keywords"),
                                 "format_example": """
                                        ```json
                                            {
                                              "sections": [
                                                {
                                                    "section_header": "Header of the section 1",
                                                    "description": "Pointers for the writers"
                                                },
                                                {
                                                    "section_header": "Header of the section 2",
                                                    "description": "Pointers for the writers"
                                                }
                                              ]
                                            }
                                        ```
                                  """})

        return {"sections": response['sections']}


if __name__ == "__main__":
    load_dotenv()
    agent = Editor()

    print(agent.get_titles())
