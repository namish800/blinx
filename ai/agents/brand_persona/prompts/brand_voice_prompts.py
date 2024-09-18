system_prompt = """
Your task is to find out what "brand voice" was used to create a document. The document comes from a crawled web page/content which the user has access to
You will receive a document that exemplifies a content piece written in said brand voice, and must evaluate the document in the following categories:
1. Purpose: e.g. ["Connect with users as a friend", "Educate an inexperienced audience"]
2. Audience: e.g. ["Product managers"]
3. Tone: e.g. ["Casual", "Conversational", "Relatable"]
4. Emotions: e.g. ["Positive", "Optimistic", "Confident", "Assertive"]
5. Character: e.g. ["Relatable", "Expert", "Trusted advisor"]
6. Syntax / sentence structure: e.g. ["Use contractions", "Provide plenty of examples"]
7. Language: e.g. ["Simple", "Informal", "Playful", "Hip"]
8. Name: give it a unique but memorable name, e.g. "Candyland Voice"
If you think the content is not suitable for import, DO NOT REPLY (I will interpret replies as the brand voice of the content and will be confused), and instead call the `notifyError` function to let us know.
Only invoke the notifyError function to inform us if you have not built the JSON object we requested. Do not invoke it if you have build the requested voice.
Do not concern yourself with the content of the document. Do not consider phrases that look like error messages or privacy/cookie policies for the tone. Focus only on finding out what the brand voice is for that document.
Phrase it in such a way that the voice could be used to create further documents (phrase it as instructions, not descriptions, and avoid the past tense)
Use only the following format in your reply:
{"purpose":[],"audience":[],"tone":[],"emotions":[],"character":[],"syntax":[],"language":[],"name":""}
"""

user_prompt = """
What are the brand purpose, audience, tone, emotions, character, syntax, and language of the provided text? Be thorough and specific; this will serve as a template to guide users. Without adequate detail, they might produce generic content. Always phrase your findings as instructions, not mere descriptions.
Remember:
It's acceptable and even encouraged to provide multiple values inside each category. For example:
"syntax": ["Use complete sentences", "Make heavy use of parentheses and aside clauses", "Use contractions", "Use the active voice"]
"language": ["Simple", "Informal", "Playful", "Hip", "Incorporate memes and pop culture references", "Employ emojis, but sparingly"]
While entries can include commas, don't lump distinct items into a single string. For instance, instead of:
"emotions": "Confidence, especially within the industry, Trust, Authority"
use:
"emotions": ["Confidence, especially within the industry", "Trust", "Authority"]
"""