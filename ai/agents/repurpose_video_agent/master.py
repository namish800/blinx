import sqlite3
from ai.agents.repurpose_video_agent.video_analyzer import VideoAnalyzer
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import StateGraph
from langgraph.constants import END

from ai.agents.repurpose_video_agent.domain.state import VideoAnalyzerState, OutputState


class VideoToBlogPostAgent:
    def __init__(self):
        conn = sqlite3.connect("video_to_blog_checkpoints.sqlite", check_same_thread=False)
        self.memory = SqliteSaver(conn)

        video_analyzer = VideoAnalyzer()

        workflow = StateGraph(VideoAnalyzerState, output=OutputState)

        workflow.add_node("upload_video", video_analyzer.upload_video)
        workflow.add_node("analyze_video", video_analyzer.analyze_video)
        workflow.add_node("get_outline", video_analyzer.get_outline)
        workflow.add_node("get_introduction", video_analyzer.get_introduction)
        workflow.add_node("write_sections", video_analyzer.write_sections)
        workflow.add_node("seo_keywords", video_analyzer.add_seo_keywords)
        workflow.add_node("images", video_analyzer.add_images)

        workflow.add_edge("upload_video", "analyze_video")
        workflow.add_edge("analyze_video", "get_outline")
        workflow.add_edge("get_outline", "get_introduction")
        workflow.add_edge("get_introduction", "write_sections")
        workflow.add_edge("write_sections", "seo_keywords")
        workflow.add_edge("seo_keywords", "images")

        workflow.set_entry_point("upload_video")
        workflow.add_edge("images", END)

        self.graph = workflow.compile(checkpointer=self.memory)

    def run(self, video_file_path, config: dict):
        inputs = {
            "video_file_path": video_file_path,
        }
        return self.graph.invoke(inputs, config)
    
    def get_state(self, cfg):
        return self.graph.get_state(cfg)

    def update_state(self, config, state, node_name):
        self.graph.update_state(config=config, values=state, as_node=node_name)
        pass


if __name__ == "__main__":
    from dotenv import load_dotenv
    _ = load_dotenv()
    agent = VideoToBlogPostAgent()
    agent_config = {"configurable": {"thread_id": "123"}}
    resp = agent.run("D:\\work\\AI\\marketingAI\\BlogGenerator\\testVideo.mp4", agent_config)
    print(resp.get('blog_post'))
