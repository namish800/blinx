import json

from ai.agents.facebook_ad_gen.domain.ad_gen_dto import AdGenDto, convert_to_dict
from ai.agents.facebook_ad_gen.master import AdGeneratorAgent


class AdGenOrchestrator:
    def __init__(self):
        self.agent = AdGeneratorAgent()

    def generate_response(self, resp, config):
        agent_state = self.agent.get_state(config)
        next_step = agent_state.next[0] if agent_state.next else "final_draft"
        return {"workflow_step": next_step, "state": resp}

    def run_ad_gen_workflow(self, session_id: str, **kwargs):
        agent_config = {"configurable": {"thread_id": session_id}}

        result = self.agent.get_state(agent_config).next

        if result:
            next_step = result[0]
            if next_step == 'human':
                self.agent.update_state(config=agent_config, state={"human_feedback": kwargs.get("human_feedback")},
                                        node_name=next_step)
            resp = self.agent.continue_run(config=agent_config)
            return self.generate_response(resp, agent_config)

        # First time flow
        ad_gen_dto = kwargs.get("ad_gen_dto")
        inputs = convert_to_dict(ad_gen_dto)
        resp = self.agent.run(**inputs, config=agent_config)

        return self.generate_response(resp, agent_config)


if __name__ == "__main__":
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

    ad_data = AdGenDto(objective="Product promotion for my online pet shop",
                       details="Dog poop scooper",
                       brand_persona=brand_persona)
    session_id = "2010"
    orchestrator = AdGenOrchestrator()
    # First time
    resp1 = orchestrator.run_ad_gen_workflow(session_id=session_id, ad_gen_dto=ad_data)
    print(json.dumps(resp1))

    # With human review
    resp1 = orchestrator.run_ad_gen_workflow(session_id=session_id, human_feedback="Add pet trainers")
    print(json.dumps(resp1))

    # With human review when user click continue
    resp1 = orchestrator.run_ad_gen_workflow(session_id=session_id, human_feedback=None)
    print(json.dumps(resp1))

