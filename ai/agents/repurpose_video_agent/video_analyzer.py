import time
import google.generativeai as genai

from ai.agents.repurpose_video_agent.domain.state import VideoAnalyzerState
from ai.agents.repurpose_video_agent.prompts import prompts
from ai.agents.repurpose_video_agent.utils import replace_image_placeholders


class VideoAnalyzer:
    def __init__(self):
        print("Initializing VideoAnalyzer...")
        self.gemini_adaptor = genai
        self.gemini_adaptor.configure()
        self.model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest")
        print("VideoAnalyzer initialized successfully.")

    def upload_video(self, state: VideoAnalyzerState):
        print("Uploading video...")
        video_file = self.gemini_adaptor.upload_file(path=state['video_file_path'])
        self.wait_for_processing(video_file)
        print("Video uploaded successfully.")
        return {"video_file_name": video_file.name}

    def wait_for_processing(self, video_file):
        # Check whether the file is ready to be used.
        while video_file.state.name == "PROCESSING":
            print('.', end='')
            time.sleep(10)
            video_file = self.gemini_adaptor.get_file(video_file.name)

        if video_file.state.name == "FAILED":
            raise ValueError(video_file.state.name)

    def get_summary(self, state: VideoAnalyzerState):
        print("Getting summary...")
        summary_prompt = prompts.summary_prompt
        video_file = self.gemini_adaptor.get_file(state['video_file_name'])
        summary_response = self.model.generate_content([summary_prompt, video_file],
                                                       request_options={"timeout": 600}
                                                       )
        return summary_response.text

    def get_key_points(self, state: VideoAnalyzerState):
        print("Getting key points...")
        key_points_prompt = prompts.key_points_prompt
        video_file = self.gemini_adaptor.get_file(state['video_file_name'])
        key_points_response = self.run_llm(key_points_prompt, video_file)
        return key_points_response

    def get_target_audience(self, state: VideoAnalyzerState):
        print("Getting target audience...")
        target_audience_prompt = prompts.target_audience_prompt
        video_file = self.gemini_adaptor.get_file(state['video_file_name'])
        target_audience_response = self.run_llm(target_audience_prompt, video_file)
        return target_audience_response

    def analyze_video(self, state: VideoAnalyzerState):
        print("Analyzing video...")
        summary = self.get_summary(state)
        key_points = self.get_key_points(state)
        target_audience = self.get_target_audience(state)

        return {"summary": summary, "key_points": key_points, "target_audience": target_audience}

    def get_outline(self, state: VideoAnalyzerState):
        print("Getting outline...")
        outline_prompt = prompts.outline_prompt(state['summary'], state['key_points'], state['target_audience'])
        video_file = self.gemini_adaptor.get_file(state['video_file_name'])
        outline_response = self.run_llm(outline_prompt, video_file)
        return {"outline": outline_response}

    def get_introduction(self, state: VideoAnalyzerState):
        print("Getting introduction...")
        introduction_prompt = prompts.introduction_prompt(state['outline'])
        video_file = self.gemini_adaptor.get_file(state['video_file_name'])
        introduction_response = self.run_llm(introduction_prompt, video_file)
        return {"introduction": introduction_response}

    def write_sections(self, state: VideoAnalyzerState):
        print("Writing sections...")
        section_writer_prompt = prompts.section_writer_prompt(state['outline'], state['introduction'])
        video_file = self.gemini_adaptor.get_file(state['video_file_name'])
        section_writer_response = self.run_llm(section_writer_prompt, video_file)
        return {"blog_post": section_writer_response}

    def generate_keywords(self, state: VideoAnalyzerState):
        print("Generating keywords...")
        add_seo_keywords_prompt = prompts.generate_keywords_prompt(state['blog_post'])
        video_file = self.gemini_adaptor.get_file(state['video_file_name'])
        add_seo_keywords_response = self.run_llm(add_seo_keywords_prompt, video_file)
        return {"keywords": add_seo_keywords_response}

    def add_seo_keywords(self, state: VideoAnalyzerState):
        print("Adding SEO keywords...")
        keywords = self.generate_keywords(state)
        add_seo_keywords_prompt = prompts.add_seo_prompt(state['blog_post'], keywords['keywords'])
        video_file = self.gemini_adaptor.get_file(state['video_file_name'])
        add_seo_keywords_response = self.run_llm(add_seo_keywords_prompt, video_file)
        return {"blog_post": add_seo_keywords_response}

    def add_images(self, state: VideoAnalyzerState):
        print("Adding images...")
        add_images_prompt = prompts.add_images_prompt(state['blog_post'])
        video_file = self.gemini_adaptor.get_file(state['video_file_name'])
        add_images_response = self.run_llm(add_images_prompt, video_file)
        blog_post = replace_image_placeholders(add_images_response, video_path=state['video_file_path'])
        return {"blog_post": blog_post}

    def run_llm(self, prompt, video_file):
        response = self.model.generate_content([video_file, prompt],
                                               request_options={"timeout": 600})
        return response.text
