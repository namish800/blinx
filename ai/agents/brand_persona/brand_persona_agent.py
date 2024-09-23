from dotenv import load_dotenv

from langchain_core.messages import SystemMessage, HumanMessage

from langchain_core.prompts import ChatPromptTemplate

from ai.utils.llm_util import model_gemini
from ai.agents.brand_persona.prompts.brand_voice_prompts import system_prompt
from ai.agents.brand_persona.prompts.brand_voice_prompts import user_prompt
from langchain_core.output_parsers import JsonOutputParser


# TODO: add keyword extraction and image analysis
class BrandPersonaAI:
    def __init__(self):
        self.model = model_gemini

        self.system_prompt = system_prompt
        self.user_prompt = user_prompt
        self.prompt_template = ChatPromptTemplate.from_messages([
            SystemMessage(system_prompt),
            ("user", "{scraped_data}"),
            HumanMessage(user_prompt)
            ]
        )
        # font family, primary, sec, ter colors,  sizing
        self.parser = JsonOutputParser()

        self.chain = self.prompt_template | self.model | self.parser

    def run(self, model_input):
        inputs = {"scraped_data": model_input}
        return self.chain.invoke(inputs)

    def get_chain(self):
        return self.chain
