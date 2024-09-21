import json

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate

from ai.agents.facebook_ad_gen.domain.state import AdGeneratorState
from ai.agents.facebook_ad_gen.prompts.planner_prompts import campaign_strategy_planner_sys_prompt, \
    campaign_strategy_planner_user_prompt

from ai.utils.llm_util import model_openai


class Planner:
    def __init__(self):
        self.model = model_openai

    def generate_campaign_plan(self, ad_gen_state: AdGeneratorState):
        prompt_template = ChatPromptTemplate.from_messages(
            [("system", campaign_strategy_planner_sys_prompt),
             ("user", campaign_strategy_planner_user_prompt)]
        )
        parser = JsonOutputParser()

        print("Generating campaign plan")
        chain = prompt_template | self.model | parser

        human_feedback = ad_gen_state.get("human_feedback")
        human_feedback_prompt = f"""
            {(f'Human feedback: {human_feedback}. You must Incorporate the human feedback.'
              f'Previous Plan: {ad_gen_state.get("campaign_plan")}')
        if human_feedback and human_feedback != 'continue' else ''}
        """
        human_feedback_instructions = f"""
            {'VERY IMPORTANT !!!! Incorporate the feedback given by the user'
        if human_feedback and human_feedback != 'no' else ''}
        """

        print(human_feedback_prompt, human_feedback_instructions)
        response = chain.invoke({
            "objective": ad_gen_state.get("objective"),
            "product_or_service_details": ad_gen_state.get("product_or_service_details"),
            "brand_persona": ad_gen_state.get("brand_persona"),
            "human_feedback_instructions": human_feedback_instructions,
            "human_feedback": human_feedback_prompt,
            "format_example": """
                                        ```json
                                            {
                                            "plan": {
                                                "strategy": {
                                                    "objective": "",
                                                    "approach": []
                                                },
                                                "target_audience": {
                                                    "primary_segment": [],
                                                    "targeting_criteria": {
                                                        "interests": [],
                                                        "behavior": []
                                                    }
                                                },
                                                "messaging_themes": {
                                                    "key_messages": [],
                                                    "content_themes": []
                                                }
                                            }
                                        }
                                        ```
                                  """})
        return {'campaign_plan': response['plan']}


if __name__ == "__main__":
    agent = Planner()
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
    state = AdGeneratorState(objective="Product promotion for my online pet shop",
                             product_or_service_details="Dog poop scooper",
                             brand_persona=json.dumps(json_data),
                             campaign_plan=plan,
                             human_feedback="Include pet trainers as well")
    print(agent.generate_campaign_plan(state))
