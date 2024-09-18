import json

from ai.agents.blog_gen.BlogGeneratorAgent import BlogGeneratorAgent
from ai.domain import BlogGeneratorDto


def dict_to_blog(blog_dict):
    # Extract the title and introduction
    title = blog_dict.get("selected_title", "")
    introduction = blog_dict.get("introduction", "")

    # Start building the blog post
    blog_post = f"# {title}\n\n"
    blog_post += f"{introduction}\n\n"

    # Add the generated sections
    generated_sections = blog_dict.get("generated_sections", [])
    for section in generated_sections:
        section_header = section.get("section_header", "")
        section_content = section.get("section_content", "")

        # Format each section
        blog_post += f"## {section_header}\n\n"
        blog_post += f"{section_content}\n\n"

    return blog_post


def generate_response(resp, agent, config):
    agent_state = agent.get_state(config)
    next_step = agent_state.next[0] if agent_state.next else "final_draft"
    return {"workflow_step": next_step, "state": resp}


def run_blog_gen_workflow(session_id: str, **kwargs):
    agent_config = {"configurable": {"thread_id": session_id}}
    agent = BlogGeneratorAgent()

    result = agent.get_state(agent_config).next
    if result:
        next_step = result[0]
        if next_step == 'title_review':
            agent.update_state(config=agent_config, state={"selected_title": kwargs.get("title")}, node_name=next_step)
            resp = agent.continue_run(config=agent_config)
            return generate_response(resp, agent, agent_config)
        elif next_step == 'section_header_review':
            agent.update_state(config=agent_config, state={"sections": kwargs.get("sections")}, node_name=next_step)
            resp = agent.continue_run(agent_config)
            return generate_response(resp, agent, agent_config)

    # First time flow
    blog_gen_dto = kwargs.get("blog_gen_dto")
    inputs = BlogGeneratorDto.convert_to_dict(blog_gen_dto)
    resp = agent.run(**inputs, config=agent_config)

    return generate_response(resp, agent, agent_config)


if __name__ == "__main__":
    json_data = {
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

    blog_data = BlogGeneratorDto.BlogGeneratorDto(
        query="How to train a puppy",
        brand_persona=json_data,
        max_suggestions=3,
        max_sections=5,
        max_images=2,
        include_images=True
    )
    sessionId = "1015"
    print(json.dumps(run_blog_gen_workflow(session_id=sessionId, blog_gen_dto=blog_data)))
    print(json.dumps(run_blog_gen_workflow(session_id=sessionId, title='The Ultimate Guide to Puppy Training for Potential Pet Owners')))
    sections = [{'section_header': "Understanding Your Puppy's Behavior", 'description': 'Explain the basics of puppy behavior, including common traits and tendencies. Discuss the importance of patience and consistency in training. Provide insights into how puppies learn and the role of positive reinforcement.'}, {'section_header': 'Housebreaking Made Easy', 'description': 'Offer step-by-step guidance on housebreaking a puppy. Include tips on creating a schedule, recognizing signs that your puppy needs to go, and how to handle accidents. Emphasize the importance of routine and positive reinforcement.'}, {'section_header': 'Mastering Basic Commands', 'description': "Detail the process of teaching essential commands such as 'sit,' 'stay,' 'come,' and 'leave it.' Provide clear instructions and tips for effective training sessions. Highlight the benefits of these commands for safety and good behavior."}, {'section_header': 'Socialization: The Key to a Well-Adjusted Pup', 'description': 'Discuss the importance of socializing your puppy with other dogs, people, and different environments. Offer practical advice on how to safely introduce your puppy to new experiences. Explain the long-term benefits of proper socialization.'}, {'section_header': 'Dealing with Common Challenges', 'description': 'Address common training challenges such as biting, chewing, and barking. Provide solutions and strategies to manage and correct these behaviors. Include tips on how to stay calm and consistent during difficult moments.'}]
    result = run_blog_gen_workflow(session_id=sessionId, sections=sections)
    print(json.dumps(result))
    print(dict_to_blog(result.get("state")))
