from ai.agents.brand_persona.brand_persona_agent import BrandPersonaAI
from ai.utils.scraper.web_scraper import scrape_full_seo_data
import json


class BrandPersonaOrchestrator:

    def __init__(self):
        self.brand_persona_agent = BrandPersonaAI()

    def generate_brand_persona(self, url, **kwargs):
        print("Scraping data")
        scraped_data = scrape_full_seo_data(url)

        scraped_data_str = json.dumps(scraped_data)

        print("generating brand persona")
        resp = self.brand_persona_agent.run(scraped_data_str)

        return resp


if __name__ == "__main__":
    url = "https://shop.poochku.in"
    orchestrator = BrandPersonaOrchestrator()
    resp = orchestrator.generate_brand_persona(url)

    print(json.dumps(resp))
