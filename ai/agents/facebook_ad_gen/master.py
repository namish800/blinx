import json
import sqlite3

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.constants import END
from langgraph.graph import StateGraph

from ai.agents.facebook_ad_gen.creator import Creator
from ai.agents.facebook_ad_gen.domain.state import AdGeneratorState
from ai.agents.facebook_ad_gen.human import Human
from ai.agents.facebook_ad_gen.planner import Planner


class AdGeneratorAgent:
    def __init__(self):
        self.model = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
            # other params...
        )
        conn = sqlite3.connect("ad_gen_checkpoints.sqlite", check_same_thread=False)
        self.memory = SqliteSaver(conn)

        planner_agent = Planner()
        human_agent = Human()
        creator_agent = Creator()

        workflow = StateGraph(AdGeneratorState)
        workflow.add_node("planner", planner_agent.generate_campaign_plan)
        workflow.add_node("human", human_agent.review)
        workflow.add_node("creator", creator_agent.generate_ad_copies)
        workflow.add_node("image_generator", creator_agent.generate_ad_images)

        workflow.add_edge("planner", "human")
        workflow.add_conditional_edges("human",
                                       (lambda review: "continue" if review.get('human_feedback',
                                                                                None) is None else "revise"),
                                       {"continue": "creator", "revise": "planner"})
        workflow.add_edge("creator", "image_generator")
        workflow.add_edge("image_generator", END)

        workflow.set_entry_point("planner")

        self.graph = workflow.compile(checkpointer=self.memory,
                                      interrupt_before=["human"])

    def run(self, objective, details, brand_persona, config: dict):
        inputs = {
            "objective": objective,
            "product_or_service_details": details,
            "brand_persona": brand_persona,
        }
        return self.graph.invoke(inputs, config)

    def continue_run(self, config: dict):
        return self.graph.invoke(None, config)

    def get_state(self, cfg):
        return self.graph.get_state(cfg)

    def update_state(self, config, state, node_name):
        self.graph.update_state(config=config, values=state, as_node=node_name)
        pass


if __name__ == "__main__":
    agent = AdGeneratorAgent()
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
    plan = """
    {'campaign_plan': {'strategy': {'objective': 'Product promotion for my online pet shop', 'approach': ['Create awareness and interest in the dog poop scooper', 'Highlight the unique features and benefits of the product', 'Drive traffic to the online pet shop for purchases', 'Engage with the audience through informative and friendly content']}, 'target_audience': {'primary_segment': ['Dog owners', 'Potential pet owners', 'Pet enthusiasts'], 'targeting_criteria': {'interests': ['Dogs', 'Pet care', 'Pet products', 'Dog training', 'Dog walking'], 'behavior': ['Online shopping', 'Engagement with pet-related content', 'Frequent buyers of pet products']}}, 'messaging_themes': {'key_messages': ['Keep your yard clean and your hands mess-free with our dog poop scooper!', 'Make dog walking a breeze with our easy-to-use poop scooper.', "Say goodbye to the hassle of cleaning up after your dog with Poochku's reliable poop scooper."], 'content_themes': [{'theme': 'Product Features', 'content': ['Highlight the ergonomic design and ease of use', 'Showcase the durability and quality of materials', 'Explain the benefits of using the scooper for hygiene and convenience']}, {'theme': 'Customer Testimonials', 'content': ['Share positive reviews and experiences from satisfied customers', "Include before-and-after scenarios to demonstrate the product's effectiveness"]}, {'theme': 'Educational Content', 'content': ['Provide tips on maintaining a clean yard', 'Share advice on responsible pet ownership', 'Offer insights on the importance of regular dog waste cleanup']}, {'theme': 'Promotional Offers', 'content': ['Announce special discounts and limited-time offers', 'Encourage immediate purchases with time-sensitive deals', 'Highlight free shipping or bundled deals for multiple purchases']}]}}}
    """
    agent_config = {"configurable": {"thread_id": 1010}}
    resp = agent.run(objective="Product promotion for my online pet shop",
                     details="Dog poop scooper",
                     brand_persona=json.dumps(json_data), config=agent_config)

    print(json.dumps(resp))

    # agent.graph.update_state(agent_config, {"human_feedback": "Include pet trainers as well"}, as_node="human")

    resp = agent.continue_run(config=agent_config)
    print(json.dumps(resp))
