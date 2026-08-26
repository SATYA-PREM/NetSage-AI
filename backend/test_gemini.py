from backend.config import settings
from google import genai

client = genai.Client(api_key=settings.GEMINI_API_KEY)
response = client.models.generate_content(
    model=settings.GEMINI_MODEL,
    contents="Say hello"
)
print(response.text)