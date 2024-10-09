from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate

from ai.agents.personalized_marketing_agent.domain.whiteboard import Whiteboard
from ai.agents.personalized_marketing_agent.prompts.prompts import write_email_prompt
from ai.utils.llm_util import model_gemini, model_openai


def get_output_format_for_content_type(content_type):
    if content_type == 'email':
        return """{"email": {"subject": "", "body": ""}}"""
    elif content_type == 'sms':
        return """{"sms":""}"""
    elif content_type == 'notification':
        return """{"notification": ""}"""


def get_content_type_format(content_type):
    email_format = """
                  - Aim for a concise email of approximately 150-200 words.
                    - Format should include a warm greeting, a personalized body, and a strong call to action.
                  """

    notification_format = """
     - Keep the notification concise for about 50 words. This will be shown in the notification drawer on the mobile app
     - Format should include, a short, concise and engaging notification text
    """

    sms_format = """
        - Aim for concise message for approximately 150-200 words.
        - Format should include a warm greeting, a personalized body, and a strong call to action.
    """
    if content_type == 'email':
        return email_format
    elif content_type == 'sms':
        return sms_format
    elif content_type == 'notification':
        return notification_format


class Writer:
    def __init__(self):
        self.model = model_openai

    def write_content(self, state: Whiteboard, content_type):
        prompt_template = ChatPromptTemplate.from_messages(
            [("user", write_email_prompt)]
        )

        parser = JsonOutputParser()
        chain = prompt_template | self.model | parser
        output_format = get_output_format_for_content_type(content_type)
        content_type_format = get_content_type_format(content_type)
        inputs = {"campaign_objective": state.get('campaign_objective'),
                  "campaign_details": state.get('campaign_details'),
                  "customer_data": state.get('customer_data'),
                  "targeting_strategy": state.get('targeting_strategy'),
                  "brand_persona": state.get('brand_persona'),
                  "content_type": "email",
                  "output_format": output_format,
                  "content_type_format": content_type_format
                  }

        resp = chain.invoke(inputs)

        return {content_type: resp[content_type]}

    def write_email(self, state: Whiteboard):
        return self.write_content(state, 'email')

    def write_notification(self, state: Whiteboard):
        return self.write_content(state, 'notification')

    def write_sms(self, state: Whiteboard):
        return self.write_content(state, 'sms')
