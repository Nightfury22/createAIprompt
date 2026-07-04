import os
import json

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()


def generate_content_with_gemini(prompt: str) -> str:
    """
    Generate content using Gemini 2.5 Flash.
    """

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not found.")

    try:
        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.9,
                top_p=1.0,
                top_k=1,
                max_output_tokens=8000,
                response_mime_type="application/json",
            ),
        )

        response_text = response.text

        print("\n========== GEMINI RESPONSE ==========")
        print(response_text)
        print("=====================================\n")

        return response_text

    except Exception as e:
        print(f"Gemini API Error: {e}")
        raise RuntimeError(
            f"Error communicating with Gemini API: {e}"
        )