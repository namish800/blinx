from ai.enums.review_state_enum import ReviewState
import json


class Human:
    def __init__(self):
        pass

    def review_titles(self, blog_generator_state: dict):
        generated_titles = blog_generator_state.get('generated_titles')

        print("User selected topic: " + blog_generator_state.get("selected_title"))

        pass

    def review_state(self, blog_generator_state: dict):
        generated_sections = blog_generator_state.get('sections')

        return {"sections": generated_sections}
