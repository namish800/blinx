from ai.utils.llm_util import model_gemini, model_openai

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate

from ai.agents.personalized_marketing_agent.domain.whiteboard import Whiteboard
from ai.agents.personalized_marketing_agent.prompts.prompts import create_campaign_strategy_sys_prompt, create_campaign_strategy_user_prompt
from ai.utils.llm_util import model_gemini


class Editor:
    def __init__(self):
        self.model = model_openai

    def create_strategy(self, state: Whiteboard):
        output_format, example = create_strategy_format_instructions()

        prompt_template = ChatPromptTemplate.from_messages(
            [("system", create_campaign_strategy_sys_prompt),
             ("user", create_campaign_strategy_user_prompt)]
        )
        parser = JsonOutputParser()

        chain = prompt_template | self.model | parser

        inputs = {"customer_data": state.get('customer_data'),
                  "campaign_objective": state.get('campaign_objective'),
                  "campaign_details": state.get('campaign_details'),
                  "output_format": output_format,
                  "customer_segment": state.get('customer_segment')}

        print("Create Strategy")

        response = chain.invoke(inputs)

        return {"targeting_strategy": response['strategy']}


def create_strategy_format_instructions():
    example = """{
      "strategy": {
        "reasoning": "Anthony has a high push notification engagement rate (100% campaign engagement score) and a good email open rate (91.45%), but primarily engages with push. We should leverage his preferred channel.",
        "message_timing": {
          "day": "Tuesday",
          "time": "8 PM (adjusting for Anthony's older demographic and potential preference for early evening)",
          "week": "First week of the month"
        },
        "messaging_tone": {
          "style": "Formal",
          "personalization": "Address him by name, considering his age and potential preference for formality.",
          "brand_voice": "Maintain the Harris-Houston brand voice, which he prefers."
        },
        "content_pillars": [
          "Modern Design: Highlight the modern design elements of the sweatshirt, aligning with his interest in 'fly' products.",
          "High Neck and Oversized Fit: Emphasize the comfort and style of the high neck and oversized fit, appealing to a mature demographic.",
          "Exclusivity and Scarcity:  Subtly hint at the product's exclusivity as a new launch, potentially mentioning limited availability to drive urgency."
        ],
        "call_to_action": "Visit Website to View New Collection",
        "additional_considerations": [
          "Anthony is a high-value customer with a strong purchase history. Emphasize the quality and value of the new sweatshirt line.",
          "Leverage his loyalty points balance (2593 points) to incentivize purchase. Perhaps offer bonus points for purchasing from the new collection.",
          "Given his high discount affinity, consider offering a small, exclusive discount on the new sweatshirts."
        ]
      }
    }"""

    output_format = """{
  "strategy": {
    "reasoning": "",
    "message_timing": {
      "day": "",
      "time": "",
      "week": ""
    },
    "messaging_tone": {
      "style": "",
      "personalization": "",
      "brand_voice": ""
    },
    "content_pillars": ["", "", ""],
    "call_to_action": "",
    "additional_considerations": ["", "", ""]
  }
}"""
    return output_format, example
