# Blinx - Multi-Agent Generative AI for Content Creation

**Blinx** is a multi-agent Generative AI system designed to streamline personalized content creation, ranging from blog posts to full-fledged marketing campaigns. This project, developed as part of a Gen AI hackathon, aims to revolutionize how brands and individuals generate tailored, data-driven content by leveraging the power of AI agents working collaboratively.

## Project Overview

Blinx harnesses the capabilities of multiple AI agents to produce high-quality content that adapts to specific audience segments and real-time inputs. By integrating advanced language models, natural language processing (NLP), and data analysis techniques, Blinx can generate a variety of content formats to suit diverse needs.

## Features

- **Multi-Agent Collaboration:** Employs a network of AI agents specialized in research, content generation, editing, and optimization to produce cohesive and impactful content.
- **Personalized Content Creation:** Generates personalized blogs, articles, and marketing materials tailored to different audience segments.
- **Dynamic Adaptation:** Adapts content in real-time based on input data, audience feedback, and changing trends.
- **Brand Consistency:** Analyzes a brand's voice and tone using NLP techniques to ensure consistency across generated content.
- **Scalable Content Generation:** From single blog posts to full-scale marketing campaigns, Blinx can scale to meet various content demands.

## Installation

To set up the Blinx system locally, follow these steps:

1. **Clone the Repository**
    ```bash
    git clone https://github.com/namish800/blinx-blog-generator.git
    cd blinx-blog-generator
    ```

2. **Install Dependencies**
   Ensure you have Python installed. Then, install the necessary packages:
    ```bash
    pip install -r requirements.txt
    ```

3. **Configure Environment Variables**
   Create a `.env` file or set the environment variables directly:
    ```bash
    GOOGLE_API_KEY=xxx
    OPENAI_API_KEY=sk-xxx
    LANGCHAIN_API_KEY=ls__xxx
    LANGCHAIN_TRACING_V2=true
    LANGCHAIN_PROJECT={PROJECT-NAME}
    ```

4. **Set Up Additional Services**
    - For advanced functionalities like real-time adaptation, set up any additional services or APIs as specified in the documentation.

## Usage

1. **Content Generation**
    - Run the main script to generate content:
      ```bash
      python main.py
      ```
    - Customize the generation process by modifying configuration files or using command-line arguments.

2. **Brand Voice Analysis**
    - Use the brand voice analysis feature to align content with a specific brand's tone:
      ```bash
      python analyze_brand_voice.py --url your-brand-url
      ```

3. **Campaign Management**
    - Integrate with other platforms or use the built-in multi-channel integration to manage marketing campaigns:
      ```bash
      python manage_campaign.py --config campaign_config.yaml
      ```

## Configuration

- **Config Files:** Modify `config.yaml` and other configuration files to adjust AI model parameters, content styles, output formats, and more.
- **Custom Scripts:** Create custom scripts using the provided modules to expand functionality or integrate new AI agents.

## Architecture

Blinx uses a modular architecture, consisting of various AI agents, including:
- **Content Generation Agent:** Responsible for creating the initial draft using generative AI models.
- **Editing Agent:** Refines the content for style, grammar, and coherence.
- **Optimization Agent:** Analyzes audience feedback and optimizes content for engagement.
- **Brand Voice Agent:** Ensures consistency with the brand's voice by analyzing existing content.
