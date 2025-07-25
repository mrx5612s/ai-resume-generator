from gemini_api import generate_with_gemini

def generate_cover_letter(data: dict):
    with open("prompts/cover_letter_prompt.txt", "r") as file:
        prompt = file.read().format(**data)
    return generate_with_gemini(prompt)
