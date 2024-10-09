from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate

from ai.agents.personalized_marketing_agent.domain.whiteboard import Whiteboard
from ai.agents.personalized_marketing_agent.prompts.prompts import customer_segment_system_prompt, \
    customer_segment_user_prompt, identify_channel_user_prompt, identify_channel_sys_prompt
from ai.utils.llm_util import model_gemini, model_openai


class CustomerAnalyst:
    def __init__(self):
        self.model = model_openai

    def identify_customer_segment(self, state: Whiteboard):
        prompt_template = ChatPromptTemplate.from_messages(
            [("system", customer_segment_system_prompt),
             ("user", customer_segment_user_prompt)]
        )
        parser = JsonOutputParser()
        chain = prompt_template | self.model | parser

        print("Identifying customer segment")
        response = chain.invoke({'customer_data': state.get('customer_data'),
                                 'format_example': """
                                 {
                                      "segments": [
                                        {
                                          "segment_name": "name",
                                          "reason": "Factual data supporting the decision"
                                        }
                                      ]
                                    }
                                 """})

        return {'customer_segment': response['segments']}

    def identify_preferred_channel(self, state: Whiteboard):
        prompt_template = ChatPromptTemplate.from_messages(
            [("system", identify_channel_sys_prompt),
             ("user", identify_channel_user_prompt)]
        )
        parser = JsonOutputParser()
        chain = prompt_template | self.model | parser

        inputs = state.get('customer_data')
        inputs['format_example'] = """
            {"channels": ["email", "notification", "sms"], "suggested_time": "", "reason": ""}
        """

        print("Identifying preferred channel")

        response = chain.invoke(inputs)

        return {"channels": response['channels'], "suggested_time": response['suggested_time'],
                "reason": response['reason']}

