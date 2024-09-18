from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate

from ai.agents.blog_gen.prompts.write_prompts import intro_writer_sys_prompt, intro_writer_user_prompt, section_writer_sys_prompt, \
    section_writer_user_prompt
from ai.utils.llm_util import model_openai


class Writer:
    def __init__(self):
        self.model = model_openai

    def write_intro(self, blog_generator_state: dict):
        prompt_template = ChatPromptTemplate.from_messages(
            [("system", intro_writer_sys_prompt), ("user", intro_writer_user_prompt)]
        )
        parser = JsonOutputParser()

        print("Writing Intro")
        chain = prompt_template | self.model | parser
        response = chain.invoke({"tone": blog_generator_state.get("brand_persona").get("tone"),
                                 "audience": blog_generator_state.get("brand_persona").get("audience"),
                                 "language": blog_generator_state.get("brand_persona").get("language"),
                                 "title": blog_generator_state.get("selected_title"),
                                 "keywords": blog_generator_state.get("keywords"),
                                 "format_example": """
                                        ```json
                                            {
                                              "introduction": "Introduction of the blog post"
                                            }
                                        ```
                                  """})
        return {"introduction": response['introduction']}

    def write_sections(self, blog_generator_state: dict):
        prompt_template = ChatPromptTemplate.from_messages(
            [("system", section_writer_sys_prompt), ("user", section_writer_user_prompt)]
        )
        parser = JsonOutputParser()
        print("Writing sections")
        chain = prompt_template | self.model | parser
        response = chain.invoke({
                                 "title": blog_generator_state.get("selected_title"),
                                 "introduction": blog_generator_state.get("introduction"),
                                 "sections": blog_generator_state.get("sections"),
                                 "keywords": blog_generator_state.get("keywords"),
                                 "brand_persona": blog_generator_state.get("brand_persona"),
                                 "format_example": """
                                        ```json
                                            {
                                              "sections": [
                                                  {
                                                    "section_header": Title of the section(Same as input)
                                                    "section_content": Content for that section
                                                  }
                                              ]
                                            }
                                        ```
                                  """})

        return {"generated_sections": response['sections']}