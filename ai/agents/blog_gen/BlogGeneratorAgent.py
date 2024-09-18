import sqlite3

from ai.agents.blog_gen.Creator import Creator
from ai.agents.blog_gen.Editor import Editor
from ai.agents.blog_gen.Human import Human
from ai.agents.blog_gen.Writer import Writer
from ai.domain.State import BlogGeneratorState
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.constants import END
from langgraph.graph import StateGraph


def check_include_images(state: dict):
    if state.get('include_images'):
        print("Going to generate images")
        return "creator"
    return END


class BlogGeneratorAgent:
    def __init__(self):
        self.model = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
            # other params...
        )
        conn = sqlite3.connect("checkpoints.sqlite", check_same_thread=False)
        self.memory = SqliteSaver(conn)

        editor_agent = Editor()
        human_agent = Human()
        writer_agent = Writer()
        creator_agent = Creator()

        workflow = StateGraph(BlogGeneratorState)
        workflow.add_node("keyword_researcher", editor_agent.get_keywords)
        workflow.add_node("title_recommender", editor_agent.get_titles)
        workflow.add_node("title_review", human_agent.review_titles)
        workflow.add_node("section_header_review", human_agent.review_state)
        workflow.add_node("introduction_writer", writer_agent.write_intro)
        workflow.add_node("planner", editor_agent.generate_section_headers)
        workflow.add_node("section_writer", writer_agent.write_sections)
        workflow.add_node("creator", creator_agent.add_creatives)

        workflow.add_edge("keyword_researcher", "title_recommender")
        workflow.add_edge("title_recommender", "title_review")
        workflow.add_edge("title_review", "introduction_writer")
        workflow.add_edge("introduction_writer", "planner")
        workflow.add_edge("planner", "section_header_review")
        workflow.add_edge("section_header_review", "section_writer")
        workflow.add_conditional_edges("section_writer", check_include_images)
        workflow.add_edge("creator", END)

        workflow.set_entry_point("keyword_researcher")

        self.graph = workflow.compile(checkpointer=self.memory,
                                      interrupt_before=["title_review", "section_header_review"])

    def run(self, query: str, brand_persona: str, max_title_suggestions: int, max_sections: int,
            max_images: int, include_images: bool, config: dict):
        return self.graph.invoke({"query": query, "brand_persona": brand_persona,
                                  "max_title_suggestions": max_title_suggestions,
                                  "max_sections": max_sections,
                                  "max_images": max_images, "include_images": include_images}, config)

    def update_state(self, config: dict, state: dict, node_name: str):
        self.graph.update_state(config=config, values=state, as_node=node_name)
        pass

    def get_state(self, config):
        return self.graph.get_state(config=config)

    def continue_run(self, config):
        return self.graph.invoke(None, config=config)
