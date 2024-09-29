from ai.agents.repurpose_video_agent.master import VideoToBlogPostAgent


class VideoToBlogOrchestrator:
    def __init__(self):
        self.agent = VideoToBlogPostAgent()

    def generate_response(self, resp, config):
        agent_state = self.agent.get_state(config)
        next_step = agent_state.next[0] if agent_state.next else "final_draft"
        return {"workflow_step": next_step, "state": resp}
    
    def run(self, video_file_path: str, session_id: str):
        agent_config = {"configurable": {"thread_id": session_id}}
        resp = self.agent.run(video_file_path, agent_config)
        return self.generate_response(resp, agent_config)
    

if __name__ == "__main__":
    from dotenv import load_dotenv
    _ = load_dotenv()
    orchestrator = VideoToBlogOrchestrator()

    resp = orchestrator.run("D:\\work\\AI\\marketingAI\\BlogGenerator\\testVideo.mp4", "112")
    print(resp)