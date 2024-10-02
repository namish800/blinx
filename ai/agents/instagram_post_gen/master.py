from ai.agents.instagram_post_gen.creator import Creator
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import StateGraph
from langgraph.constants import END
from langgraph.types import Send

import sqlite3

from ai.agents.instagram_post_gen.domain.state import InstagramPostState


class InstagramPostGenAgent:
    def __init__(self):
        conn = sqlite3.connect("instagram_post_checkpoints.sqlite", check_same_thread=False)
        self.memory = SqliteSaver(conn)

        creator = Creator()

        workflow = StateGraph(InstagramPostState)

        workflow.add_node("caption_gen", creator.generate_instagram_captions)
        workflow.add_node("hashtag_gen", creator.generate_instagram_hashtags)
        workflow.add_node("image_gen", creator.generate_instagram_images)

        workflow.add_conditional_edges("caption_gen", continue_to_hashtags, ["hashtag_gen"])
        workflow.add_conditional_edges("caption_gen", continue_to_image_gen, ["image_gen"])

        workflow.add_edge("hashtag_gen", END)
        workflow.add_edge("image_gen", END)

        workflow.set_entry_point("caption_gen")

        self.graph = workflow.compile(checkpointer=self.memory)

    def run(self, objective, max_posts, brand_persona, include_images, config: dict):
        inputs = {
            "objective": objective,
            "brand_persona": brand_persona,
            "max_posts": max_posts,
            "include_images": include_images
        }
        return self.graph.invoke(inputs, config)

    def continue_run(self, config: dict):
        return self.graph.invoke(None, config)

    def get_state(self, cfg):
        return self.graph.get_state(cfg)

    def update_state(self, config, state, node_name):
        self.graph.update_state(config=config, values=state, as_node=node_name)
        pass


# Here we define the logic to map out over the generated captions
# We will use this an edge in the graph
def continue_to_hashtags(state: InstagramPostState):
    # We will return a list of `Send` objects
    # Each `Send` object consists of the name of a node in the graph
    # as well as the state to send to that node
    return [Send("hashtag_gen", {"caption": s}) for s in state["captions"]]


# Here we define the logic to map out over the generated captions
# We will use this an edge in the graph
def continue_to_image_gen(state: InstagramPostState):
    # We will return a list of `Send` objects
    # Each `Send` object consists of the name of a node in the graph
    # as well as the state to send to that node
    return [Send("image_gen", {"caption": s, "brand_persona": state["brand_persona"]}) for s in state["captions"]]