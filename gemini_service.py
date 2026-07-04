import os
from google import genai
from dotenv import load_dotenv

load_dotenv()


def generate_content_with_gemini(prompt: str) -> str:
    """Communicate with the Gemini API and return the generated text."""
    try:
        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

        response = client.models.generate_content(
            model="gemini-1.5-flash-latest",
            contents=prompt,
            config={
                "temperature": 0.9,
                "top_p": 1.0,
                "top_k": 1,
                "max_output_tokens": 3000,
            },
        )

        print(f"Raw Gemini Response:\n---\n{response.text}\n---")
        return response.text

    except Exception as e:
        print(f"Gemini API error: {e}")
        raise RuntimeError(f"Error communicating with Gemini API: {e}")