import json

from ai.agents.personalized_marketing_agent.master import MarketingAgent


class PersonalizedMarketingOrchestrator:
    def __init__(self):
        self.agent = MarketingAgent()

    def generate_response(self, resp, config):
        agent_state = self.agent.get_state(config)
        next_step = agent_state.next[0] if agent_state.next else "final_draft"
        return {"workflow_step": next_step, "state": resp}

    def run_workflow(self, session_id: str, brand_persona, objective, details, customer_data):
        agent_config = {"configurable": {"thread_id": session_id}}
        resp = self.agent.run(brand_persona=brand_persona, customer_data=customer_data, objective=objective,
                              details=details, config=agent_config)

        return self.generate_response(resp, agent_config)


if __name__ == '__main__':
    orchestrator = PersonalizedMarketingOrchestrator()

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

    session_id = '2001'

    resp = orchestrator.run_workflow(session_id=session_id,brand_persona=brand_persona, objective=objective,
                                     details=details, customer_data=customer_data)

    print(json.dumps(resp))