from typing import Literal

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.constants import END
from langgraph.graph import StateGraph

from agents.Creator import Creator
from agents.Editor import Editor
from agents.Human import Human
from agents.Writer import Writer
from domain.BrandPersona import BrandPersona
from domain.State import BlogGeneratorState


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

    def init_workflow(self):
        editor_agent = Editor()
        human_agent = Human()
        writer_agent = Writer()
        creator_agent = Creator()

        workflow = StateGraph(BlogGeneratorState)
        workflow.add_node("keyword_researcher", editor_agent.get_keywords)
        workflow.add_node("title_recommender", editor_agent.get_titles)
        workflow.add_node("human_review", human_agent.review_titles)
        workflow.add_node("section_header_review", human_agent.review_state)
        workflow.add_node("introduction_writer", writer_agent.write_intro)
        workflow.add_node("planner", editor_agent.generate_section_headers)
        workflow.add_node("section_writer", writer_agent.write_sections)
        workflow.add_node("creator", creator_agent.add_creatives)

        workflow.add_edge("keyword_researcher", "title_recommender")
        workflow.add_edge("title_recommender", "human_review")
        workflow.add_edge("human_review", "introduction_writer")
        workflow.add_edge("introduction_writer", "planner")
        workflow.add_edge("planner", "section_header_review")
        workflow.add_edge("section_header_review", "section_writer")
        workflow.add_conditional_edges("section_writer", check_include_images)
        workflow.add_edge("creator", END)

        workflow.set_entry_point("keyword_researcher")

        return workflow

    def run(self, query: str, brand_persona: BrandPersona, max_suggestions: int, max_sections: int,
            max_images: int, include_images: bool):
        workflow = self.init_workflow()

        graph = workflow.compile()

        return graph.invoke({"query": query, "brand_persona": brand_persona,
                             "max_title_suggestions": max_suggestions,
                             "max_sections": max_sections,
                             "max_images": max_images, "include_images": include_images})


def dict_to_blog(blog_dict):
    # Extract the title and introduction
    title = blog_dict.get("selected_title", "")
    introduction = blog_dict.get("introduction", "")

    # Start building the blog post
    blog_post = f"# {title}\n\n"
    blog_post += f"{introduction}\n\n"

    # Add the generated sections
    generated_sections = blog_dict.get("generated_sections", [])
    for section in generated_sections:
        section_header = section.get("section_header", "")
        section_content = section.get("section_content", "")

        # Format each section
        blog_post += f"## {section_header}\n\n"
        blog_post += f"{section_content}\n\n"

    return blog_post


if __name__ == "__main__":
    agent = BlogGeneratorAgent()

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
    keywords = "New pet parent tips, First-time dog owner guide, Essential pet care for beginners, Puppy care basics for new owners, First-time pet supplies checklist, Training tips for new pet parents"
    brand_persona = BrandPersona(**json_data)
    query = "First time pet parents"
    response = agent.run(query=query, brand_persona=brand_persona, max_suggestions=5, max_sections=5,
                         max_images=2, include_images=False)

    ## create final blog
    print(dict_to_blog(response))