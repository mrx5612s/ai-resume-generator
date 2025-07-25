from gemini_api import generate_with_gemini

def generate_resume(data: dict):
    with open("prompts/resume_prompt.txt", "r") as file:
        prompt = file.read().format(**data)
    return generate_with_gemini(prompt)
