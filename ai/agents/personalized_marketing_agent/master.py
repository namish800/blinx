import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.constants import END
from langgraph.graph import StateGraph

from ai.agents.personalized_marketing_agent.analyst import CustomerAnalyst
from ai.agents.personalized_marketing_agent.domain.whiteboard import Whiteboard
from ai.agents.personalized_marketing_agent.editor import Editor
from ai.agents.personalized_marketing_agent.writer import Writer


def get_node_name(content_type):
    if content_type == 'email':
        return 'email_writer'
    elif content_type == 'sms':
        return 'sms_writer'
    elif content_type == 'notification':
        return 'notification_writer'


class MarketingAgent:
    def __init__(self):
        conn = sqlite3.connect("email_checkpoints.sqlite", check_same_thread=False)
        self.memory = SqliteSaver(conn)

        analyst = CustomerAnalyst()
        editor = Editor()
        writer = Writer()

        workflow = StateGraph(Whiteboard)

        workflow.add_node("customer_insight", analyst.identify_customer_segment)
        workflow.add_node("preferred_channel", analyst.identify_preferred_channel)
        workflow.add_node("planner", editor.create_strategy)
        workflow.add_node("email_writer", writer.write_email)
        workflow.add_node("notification_writer", writer.write_notification)
        workflow.add_node("sms_writer", writer.write_sms)
        workflow.add_node("dummy1", lambda x: {"dummy": "dummy"})
        workflow.add_node("dummy2", lambda x: {"dummy": "dummy"})
        workflow.add_node("dummy3", lambda x: {"dummy": "dummy"})

        workflow.add_edge('customer_insight', 'preferred_channel')
        workflow.add_edge('preferred_channel', 'planner')

        # parallel branches
        workflow.add_edge('planner', 'dummy1')
        workflow.add_edge('planner', 'dummy2')
        workflow.add_edge('planner', 'dummy3')

        # cannot use add_conditional_edges for parallel branches
        workflow.add_conditional_edges('dummy1', lambda x: self.check_channel(x, 'email'))
        workflow.add_conditional_edges('dummy2', lambda x: self.check_channel(x, 'sms'))
        workflow.add_conditional_edges('dummy3', lambda x: self.check_channel(x, 'notification'))

        workflow.add_edge('email_writer', END)
        workflow.add_edge('notification_writer', END)
        workflow.add_edge('sms_writer', END)

        workflow.set_entry_point("customer_insight")

        self.graph = workflow.compile(checkpointer=self.memory)

    def check_channel(self, state: Whiteboard, content_type: str):
        allowed_channels = state.get('channels')
        if content_type in allowed_channels:
            return get_node_name(content_type)
        return END

    def run(self, brand_persona, customer_data, objective, details, config: dict):
        inputs = {
            "campaign_objective": objective,
            "brand_persona": brand_persona,
            "customer_data": customer_data,
            "campaign_details": details
        }
        return self.graph.invoke(inputs, config)

    def continue_run(self, config: dict):
        return self.graph.invoke(None, config)

    def get_state(self, cfg):
        return self.graph.get_state(cfg)

    def update_state(self, config, state, node_name):
        self.graph.update_state(config=config, values=state, as_node=node_name)
        pass


if __name__ == '__main__':
    agent = MarketingAgent()

    brand_persona = {
        'purpose': ['Promote and sell pet products', 'Establish an online presence for the Poochku brand',
                    'Provide information and resources for dog owners'],
        'audience': ['Dog owners', 'Potential pet owners', 'Pet enthusiasts'],
        'tone': ['Friendly', 'Enthusiastic', 'Informative', 'Approachable'],
        'emotions': ['Positive', 'Excited', 'Helpful'],
        'character': ['Enthusiastic pet enthusiast', 'Reliable source of pet products',
                      'Friendly advisor for dog owners'],
        'syntax': ['Use clear and concise sentences', 'Provide product descriptions and details',
                   'Use headings and subheadings to organize information'],
        'language': ['Simple', 'Easy to understand', 'Relatable to dog owners'],
    }

    objective = "Product launch"
    details = "We are launching a new product line of highneck oversized sweatshirts with the modern design"

    customer_data = {"user_id": 61121, "name": "Anthony Jacobs", "email": "allen36@yahoo.com", "gender": "M", "age": 65,
                     "location": "Davidmouth", "account_creation_date": "2024-04-20 00:00:00",
                     "last_login_date": "2024-03-20 00:00:00", "total_spent": 4676.37, "transaction_frequency": 2,
                     "average_transaction_value": 2338.18, "last_transaction_date": "2024-05-09 00:00:00",
                     "number_of_transactions": 2, "favorite_payment_method": "PayPal", "purchase_channel": "in-store",
                     "preferred_device": "desktop", "preferred_language": "Hindi", "time_on_site": 99,
                     "page_views_per_session": 5, "average_cart_value": 2338.18, "abandoned_cart_count": 5,
                     "product_browsing_history": "fly", "loyalty_program_member": False, "loyalty_points_balance": 2593,
                     "email_open_rate": 91.45, "email_click_rate": 26.97, "SMS_opt_in": False, "SMS_click_rate": 38.71,
                     "best_time_in_the_day": 20, "best_day_in_a_week": "Tuesday", "best_week_in_a_month": 1,
                     "coupon_usage_frequency": 69.55, "social_media_engagement": 96, "number_of_reviews_written": 2,
                     "average_review_rating": 4.58, "referral_count": 9, "customer_service_interactions": 5,
                     "live_chat_use_frequency": 18, "marketing_segment": "A", "campaign_engagement_score": 100,
                     "preferred_communication_channel": "push notifications", "click_through_rate": 5.16,
                     "conversion_rate": 0.72, "discount_usage_rate": 99.54, "preferred_brand": "Harris-Houston",
                     "brand_loyalty_index": 6, "lifetime_value_estimate": 4676.37, "frequency_of_visits_per_week": 1,
                     "returning_customer": False, "shopping_basket_value": 2338.18, "cart_conversion_rate": 22.4,
                     "purchase_value_category": "HV", "transaction_frequency_category": "LF",
                     "product_affinity": "Jacket, Sweater, T-shirt", "discount_affinity": 20}

    agent_config = {"configurable": {"thread_id": "1019"}}
    resp = agent.run(brand_persona=brand_persona, customer_data=customer_data, objective=objective,
                     details=details, config=agent_config)

    import json

    print(json.dumps(resp))
