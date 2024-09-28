import json
from ai.agents.instagram_post_gen.domain.post_gen_dto import PostGenDto, convert_to_dict
from ai.agents.instagram_post_gen.master import InstagramPostGenAgent


class InstagramPostGenOrchestrator:
    def __init__(self):
        self.agent = InstagramPostGenAgent()

    def generate_response(self, resp, config):
        agent_state = self.agent.get_state(config)
        next_step = agent_state.next[0] if agent_state.next else "final_draft"
        return {"workflow_step": next_step, "state": resp}

    def run_instagram_post_gen_workflow(self, session_id: str, **kwargs):
        agent_config = {"configurable": {"thread_id": session_id}}

        # First time flow
        post_gen_dto = kwargs.get("instagram_post_dto")
        inputs = convert_to_dict(post_gen_dto)
        resp = self.agent.run(**inputs, config=agent_config)

        return self.generate_response(resp, agent_config)


if __name__ == "__main__":
    orchestrator = InstagramPostGenOrchestrator()
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
    post_data = PostGenDto(objective="Product promotion for my online pet shop. Product name is Poochku's Poop scooper",
                           brand_persona=brand_persona, max_posts=3, include_images=True)
    session_id = "3003"
    resp = orchestrator.run_instagram_post_gen_workflow(session_id=session_id, instagram_post_dto=post_data)
    print(json.dumps(resp))
