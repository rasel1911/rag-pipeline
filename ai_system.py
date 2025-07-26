from google import genai
from dotenv import load_dotenv
load_dotenv()

client = genai.Client()

def output_get(content,question):
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f'{content} read this content and give {question} this question answer. only give answer',
    )
    return response.text