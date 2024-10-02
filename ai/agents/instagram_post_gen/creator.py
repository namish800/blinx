from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate

from ai.agents.instagram_post_gen.domain.state import HashtagGeneratorState, InstagramPostState
from ai.agents.instagram_post_gen.prompts.creator_prompts import caption_gen_system_prompt, caption_gen_user_prompt, \
    hashtag_gen_system_prompt, hashtag_gen_user_prompt, instagram_image_gen_system_prompt, \
    instagram_image_gen_user_prompt
from ai.utils.ImageGenerator import SocialMediaImageGenerator

from ai.utils.llm_util import model_openai


class Creator:
    def __init__(self):
        self.model = model_openai
        self.img_gen = SocialMediaImageGenerator()

    def generate_instagram_captions(self, instagram_post_state: InstagramPostState):
        prompt_template = ChatPromptTemplate.from_messages(
            [("system", caption_gen_system_prompt),
             ("user", caption_gen_user_prompt)]
        )
        parser = JsonOutputParser()

        print("Generating Instagram post Copies")
        chain = prompt_template | self.model | parser

        response = chain.invoke({"objective": instagram_post_state.get('objective'),
                                 "brand_persona": instagram_post_state.get('brand_persona'),
                                 "max_posts": instagram_post_state.get('max_posts'),
                                 "format_example": """
                                 ```json
                                 {
                                   "captions": [
                                    "caption1",
                                    "caption2",
                                    "caption3",
                                   ]
                                 }
                                 ```
                                 """
                                 })

        return {"captions": response['captions']}

    def generate_instagram_hashtags(self, state: HashtagGeneratorState):
        prompt_template = ChatPromptTemplate.from_messages(
            [("system", hashtag_gen_system_prompt),
             ("user", hashtag_gen_user_prompt)]
        )
        parser = JsonOutputParser()

        print("Generating hashtags")
        chain = prompt_template | self.model | parser

        response = chain.invoke({"caption": state.get('caption'),
                                 "format_example": """
                                    {
                                        "hashtags": [
                                            "hashtag1",
                                            "hashtag2",
                                            "hashtag3",
                                        ]
                                    }
                                 """
                                 })

        return {"hashtags": response['hashtags']}

    def generate_instagram_images(self, state: dict):
        prompt_template = ChatPromptTemplate.from_messages(
            [("system", instagram_image_gen_system_prompt),
             ("user", instagram_image_gen_user_prompt)]
        )
        parser = JsonOutputParser()

        print("Generating images")
        chain = prompt_template | self.model | parser

        response = chain.invoke({"caption": state.get('caption'),
                                 "brand_persona": state.get('brand_persona'),
                                 "format_example": """
                                    {
                                        "image_prompt": "prompt for the image"
                                    }
                                 """
                                 })

        image_urls = []
        if response['image_prompt']:
            image_url = self.img_gen.generate_image(response['image_prompt'])
            image_urls.append(image_url)

        return {"image_prompts": [response['image_prompt']], "image_urls": image_urls}
