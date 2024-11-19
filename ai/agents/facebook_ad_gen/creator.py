import json
from typing import List

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate

from ai.agents.facebook_ad_gen.domain.state import AdGeneratorState, ImagePromptState
from ai.agents.facebook_ad_gen.prompts.content_creator_prompts import ad_creator_system_prompt, ad_creator_user_prompt, \
    image_gen_sys_prompt, image_gen_user_prompt
from ai.utils.ImageGenerator import SocialMediaImageGenerator

from ai.utils.llm_util import model_openai


class Creator:
    def __init__(self):
        self.model = model_openai
        self.img_gen = SocialMediaImageGenerator()

    def generate_ad_copies(self, ad_gen_state: AdGeneratorState):
        prompt_template = ChatPromptTemplate.from_messages(
            [("system", ad_creator_system_prompt),
             ("user", ad_creator_user_prompt)]
        )
        parser = JsonOutputParser()

        print("Generating Ad Copies")
        chain = prompt_template | self.model | parser

        response = chain.invoke({
            "campaign_strategy": ad_gen_state.get("campaign_plan"),
            "brand_persona": ad_gen_state.get("brand_persona"),
            "format_example": """
                        ```json
                            {
                            "ad_copies": [{
                                "framework": "",
                                "background_image_prompt": "",
                                "suggestions": ["idea1", "idea"2]
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
        return {'ad_copies_intermediate': response['ad_copies']}

    def generate_ad_images(self, ad_gen_state: AdGeneratorState):
        ad_copies = ad_gen_state.get("ad_copies", [])
        update_ad_copies = []
        for ad_copy in ad_copies:
            # prompt = self.generate_image_prompt(ad_copy.get("background_image_prompt"), ad_copy.get("suggestions"))
            # ad_copy["background_image_prompt"] = prompt
            ad_copy["background_image_url"] = self.img_gen.generate_facebook_ad_post(ad_copy.get("background_image_prompt"))
            update_ad_copies.append(ad_copy)
        return {'ad_copies': update_ad_copies}

    def generate_image(self, state: ImagePromptState):
        # prompt_template = ChatPromptTemplate.from_messages(
        #     [("system", image_gen_sys_prompt),
        #      ("user", image_gen_user_prompt)]
        # )
        # parser = JsonOutputParser()
        #
        # print("Generating images")
        # chain = prompt_template | self.model | parser
        #
        # response = chain.invoke({"ad_copy": state.get('ad_copy'),
        #                          "brand_persona": state.get('brand_persona'),
        #                          "campaign_plan": state.get('campaign_plan'),
        #                          "format_example": """
        #                             {
        #                                 "image_prompt": "prompt for the image",
        #                                 "suggestions": ["suggestion1", "suggestion2"]
        #                             }
        #                          """
        #                          })

        image_url = self.img_gen.generate_facebook_ad_post(state['ad_copy']['background_image_prompt'])
        ad_copy = state.get('ad_copy')
        ad_copy["background_image_url"] = image_url
        return {"ad_copies": [ad_copy]}

    # def generate_image_prompt(self, background_prompt, suggestions):
    #     """
    #     Combines the background image prompt with suggestions to create a detailed image generation prompt.
    #
    #     Args:
    #         background_prompt (str): The base description of the background image.
    #         suggestions (list): A list of suggestions to enhance the image prompt.
    #
    #     Returns:
    #         str: A comprehensive prompt for image generation.
    #     """
    #     # Start with the background prompt
    #     prompt = f"{background_prompt}"
    #
    #     # Add each suggestion as an additional detail
    #     for suggestion in suggestions:
    #         prompt += f" {suggestion}"
    #
    #     return prompt


