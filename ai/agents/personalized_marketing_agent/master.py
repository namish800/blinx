import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.constants import END
from langgraph.graph import StateGraph

from ai.agents.personalized_marketing_agent.analyst import CustomerAnalyst
from ai.agents.personalized_marketing_agent.domain.whiteboard import Whiteboard
from ai.agents.personalized_marketing_agent.editor import Editor
from ai.agents.personalized_marketing_agent.writer import Writer


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

        workflow.add_edge('customer_insight', 'preferred_channel')
        workflow.add_edge('preferred_channel', 'planner')
        workflow.add_edge('planner', 'email_writer')
        workflow.add_edge('planner', 'notification_writer')
        workflow.add_edge('planner', 'sms_writer')

        workflow.add_edge('email_writer', END)
        workflow.add_edge('notification_writer', END)
        workflow.add_edge('sms_writer', END)

        workflow.set_entry_point("customer_insight")

        self.graph = workflow.compile(checkpointer=self.memory)

    def run(self, brand_persona, customer_data, objective, details, config: dict):
        inputs = {
            "campaign_objective": objective,
            "brand_persona": brand_persona,
            "customer_data": customer_data,
            "campaign_details": details
        }
        return self.graph.invoke(inputs, config)


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

    customer_data = {"user_id": 7146, "name": "Austin Newman", "email": "azavala@yahoo.com", "gender": "M", "age": 44,
                     "location": "Colinfurt", "account_creation_date": "2024-01-18 00:00:00",
                     "last_login_date": "2024-01-16 00:00:00", "total_spent": 69.18, "transaction_frequency": 7,
                     "average_transaction_value": 9.88, "last_transaction_date": "2024-06-09 00:00:00",
                     "number_of_transactions": 7, "favorite_payment_method": "PayPal", "purchase_channel": "in-store",
                     "preferred_device": "mobile", "preferred_language": "French", "time_on_site": 34,
                     "page_views_per_session": 4, "average_cart_value": 9.88, "abandoned_cart_count": 5,
                     "product_browsing_history": "ok, where, follow", "loyalty_program_member": False,
                     "loyalty_points_balance": 505, "email_open_rate": 78.29, "email_click_rate": 35.88,
                     "SMS_opt_in": False, "SMS_click_rate": 74.18, "best_time_in_the_day": 8,
                     "best_day_in_a_week": "Tuesday", "best_week_in_a_month": 1, "coupon_usage_frequency": 40.28,
                     "social_media_engagement": 49, "number_of_reviews_written": 9, "average_review_rating": 3.92,
                     "referral_count": 6, "customer_service_interactions": 5, "live_chat_use_frequency": 21,
                     "marketing_segment": "D", "campaign_engagement_score": 34,
                     "preferred_communication_channel": "email", "click_through_rate": 8.64, "conversion_rate": 9.97,
                     "discount_usage_rate": 45.8, "preferred_brand": "Brandt, Lee and Brown", "brand_loyalty_index": 67,
                     "lifetime_value_estimate": 69.18, "frequency_of_visits_per_week": 4, "returning_customer": False,
                     "shopping_basket_value": 9.88, "cart_conversion_rate": 40.45, "purchase_value_category": "LV",
                     "transaction_frequency_category": "HF", "product_affinity": "Sweater, Hoodie, Jacket",
                     "discount_affinity": 30}

    agent_config = {"configurable": {"thread_id": "1007"}}
    resp = agent.run(brand_persona=brand_persona, customer_data=customer_data, objective=objective,
                     details=details, config=agent_config)

    import json

    print(json.dumps(resp))
