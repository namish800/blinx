import json

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate

from prompts.title_gen import add_creatives_sys_prompt, add_creatives_user_prompt
from utils.llm_util import model_openai, text_to_image_model


class Creator:
    def __init__(self):
        self.model = model_openai
        self.text_to_image_model = text_to_image_model

    def add_creatives(self, blog_generator_state: dict):
        prompt_template = ChatPromptTemplate.from_messages(
            [("system", add_creatives_sys_prompt), ("user", add_creatives_user_prompt)]
        )
        parser = JsonOutputParser()

        chain = prompt_template | self.model | parser
        response = chain.invoke({
            "title": blog_generator_state.get("selected_title"),
            "introduction": blog_generator_state.get("introduction"),
            "sections": blog_generator_state.get("generated_sections"),
            "brand_persona": blog_generator_state.get("brand_persona"),
            "max_images": blog_generator_state.get("max_images"),
            "format_example": """
                                ```json
                                    {
                                      "prompts": [
                                          "prompt1",
                                          "prompt2"
                                      ]
                                    }
                                ```
                              """
        })

        img_urls = [self.get_img_urls(prompt) for prompt in response['prompts']]
        return {"image_prompts": response['prompts'], "img_urls": img_urls}

    def get_img_urls(self, prompt: str):
        return self.text_to_image_model.run(prompt)
