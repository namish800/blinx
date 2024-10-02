## task 1: get summary of the video
summary_prompt = """Please watch the provided video and generate a concise summary (150-200 words) of its main topics, messages, and any conclusions drawn
Always output in markdown format.
"""

key_points_prompt = """List the key points, important facts, statistics, and any notable quotes mentioned in the video. Present them in bullet-point format.
Always output in markdown format.
"""

target_audience_prompt = """
Based on the video's content, identify the target audience and the primary purpose of the message (e.g., to inform, persuade, entertain, etc.)
"""


def outline_prompt(summary, key_points, audience):
    return f"""
"Using the summary and key points, create a detailed outline for a blog post. The outline should include:

An engaging title that reflects the video's content.
Introduction points that will hook the reader.
Section headings for the body, organized logically.
Bullet points or subheadings under each section to detail what will be covered.
A conclusion that summarizes the content and includes a call to action."

Summary:
{summary}

keypoints:
{key_points}

target audience:
{audience}
"""


def introduction_prompt(outline):
    return f"""
Write an engaging introduction for the blog post that captures the reader's attention. Start with a hook (e.g., a question, interesting fact, or bold statement) and provide a brief overview of what the blog will cover.

Here is the outline shared by the chief editor:

{outline}
"""


def section_writer_prompt(outline, introduction):
    return f"""
For each section in the outline, expand the bullet points into comprehensive paragraphs. Include additional insights, examples, or data to add value beyond the video's content. Ensure the writing is in a conversational tone suitable for the target audience.

Here is the outline given by the chief editor:
{outline}

Here is the introduction to be used:
{introduction}

Points for writing the conclusion:
Craft a conclusion that summarizes the key takeaways from the blog post. Include a compelling call to action that encourages reader engagement (e.g., leave a comment, share the post, explore services, etc.).
"""


def generate_keywords_prompt(sections):
    return f"""
Identify relevant SEO keywords and phrases related to the video's topic. Incorporate these keywords naturally throughout the blog post, including in headings and subheadings.

Blog Post:
{sections}
"""


def add_seo_prompt(blog_post, keywords):
    return f"""
You are an expert seo rich blog post writer for a digital marketing agency.

Incorporate the identified keywords into the blog post:
{keywords}

Blog Post
{blog_post}

Only return the final blog in the markdown format
"""


def add_images_prompt(blog_post):
    return f"""
Go through the video and recommend relevant images, infographics, or charts from the video that could enhance each section of the blog post.

This is the blog post:
{blog_post}

Add the placeholders for these images in the blog post. These placeholder should have the timestamp from the video.

For example:
If you want to add image to the blog post. Add the placeholder in this format: %image_timestamp=MM:SS%
if you want to capture frame at 00:08 then return %image_timestamp=00:08%

IMPORTANT!!!!
Always the timestamp should be in format MM:SS
Only return the final blog in the markdown format
"""


metadata_prompt = """
You are an AI assistant that generates metadata and alt text for blog posts.
Using the provided blog content, write a meta description (150-160 characters) that summarizes the content and entices users to click. "
Also, provide alt text for each suggested image to enhance SEO and accessibility.
"""
