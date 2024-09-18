from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate

from ai.agents.blog_gen.prompts.title_gen import add_creatives_sys_prompt, add_creatives_user_prompt

from ai.utils.ImageGenerator import SocialMediaImageGenerator
from ai.utils.llm_util import model_openai


class Creator:
    def __init__(self):
        self.model = model_openai
        self.image_gen = SocialMediaImageGenerator()

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

        img_urls = [self.image_gen.generate_image(prompt) for prompt in response['prompts']]
        return {"image_prompts": response['prompts'], "img_urls": img_urls}


