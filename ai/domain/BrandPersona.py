import json


class BrandPersona:
    def __init__(self, purpose, audience, tone, emotions, character, syntax, language):
        self.purpose = purpose
        self.audience = audience
        self.tone = tone
        self.emotions = emotions
        self.character = character
        self.syntax = syntax
        self.language = language

    def __repr__(self):
        return f"BrandPersona(purpose={self.purpose}, audience={self.audience}, " \
               f"tone={self.tone}, emotions={self.emotions}, character={self.character}, " \
               f"syntax={self.syntax}, language={self.language})"

    def to_dict(self):
        return {
            'purpose': self.purpose,
            'audience': self.audience,
            'tone': self.tone,
            'emotions': self.emotions,
            'character': self.character,
            'syntax': self.syntax,
            'language': self.language,
        }


if __name__ == "__main__":
    # Sample JSON data
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
        'name': 'Pawsitive Pet Shop Voice'
    }
    print(json.dumps(json_data))
    # Convert JSON to a PetShopVoice object
    pet_shop_voice = BrandPersona(**json_data)

    print(pet_shop_voice)
