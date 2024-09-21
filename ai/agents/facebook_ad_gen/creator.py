import json

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate

from ai.agents.facebook_ad_gen.domain.state import AdGeneratorState
from ai.agents.facebook_ad_gen.prompts.content_creator_prompts import ad_creator_system_prompt, ad_creator_user_prompt

from ai.utils.llm_util import model_openai


class Creator:
    def __init__(self):
        self.model = model_openai

    def generate_ad_copies(self, ad_gen_state: AdGeneratorState):
        prompt_template = ChatPromptTemplate.from_messages(
            [("system", ad_creator_system_prompt),
             ("user", ad_creator_user_prompt)]
        )
        parser = JsonOutputParser()

        print("Generating Ad Copies")
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
        response = chain.invoke({
            "campaign_strategy": ad_gen_state.get("campaign_plan"),
            "brand_persona": ad_gen_state.get("brand_persona"),
            "format_example": """
                        ```json
                            {
                            "ad_copies": [{
                                "framework": "",
                                "image_suggestion": "",
                                "content": {
                                    "primary_text": "",
                                    "headline": "",
                                    "description": "",
                                    "call_to_action": ""
                                }
                            },]
                        }
                        ```
                                  """})
        return {'ad_copies': response['ad_copies']}