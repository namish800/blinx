campaign_strategy_planner_sys_prompt = """
You are an experienced digital marketing strategist specializing in Facebook ad campaigns. Your task is to create detailed and actionable campaign plans based on the user's inputs. The plan should align with the provided brand persona, maintain the specified tone and language, and focus on achieving the user's objectives. Present the information clearly and professionally, using structured headings and bullet points where appropriate.

Instructions for Output Format:
Always return the response in the JSON format.

Example JSON Format:
{format_example}

{human_feedback_instructions}
"""

campaign_strategy_planner_user_prompt = """
**User Inputs:**

1. Objective: 
{objective}

2. Product/Service Details:
{product_or_service_details}

3. Brand Persona:
{brand_persona}

Task:
 
Using the information above, create a comprehensive Facebook ad campaign plan that includes:

- **Campaign Strategy**: Outline the overall approach to achieve the objective.
- **Target Audience**: Define specific audience segments to target.
- **Messaging Themes**: Propose key messages and content themes that align with the brand persona.

Ensure the campaign plan reflects the brand persona's tone, emotions, character, syntax, and language preferences.
Present the plan in a clear, structured manner suitable for immediate implementation.

{human_feedback}
"""
