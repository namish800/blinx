from enums.review_state_enum import ReviewState
import json


class Human:
    def __init__(self):
        pass

    def review_titles(self, blog_generator_state: dict):
        generated_titles = blog_generator_state.get('generated_titles')

        print("Please select the title you like")
        for title in generated_titles:
            print(title)

        user_input = input("Please input the title you like")

        return {"selected_title": user_input}

    def review_state(self, blog_generator_state: dict):
        generated_sections = blog_generator_state.get('sections')

        return {"sections": generated_sections}
