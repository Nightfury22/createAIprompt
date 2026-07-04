import os
import google.genai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

def generate_content_with_gemini(prompt: str) -> str:
    """
    Communicates with the Gemini API to generate content based on the provided prompt.
    Uses the gemini-2.5-flash model.
    """
    try:
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash-001", # Updated to a stable model
            generation_config={
                "temperature": 0.9,
                "top_p": 1,
                "top_k": 1,
                "max_output_tokens": 3000,
            },
            safety_settings=[
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            ],
        )

        response = model.generate_content(prompt)

        if response.parts:
            return response.text
        else:
            # Handle cases where no parts are returned, but perhaps a prompt feedback or other issue occurred.
            print("Gemini API call returned no content parts.")
            if response.prompt_feedback and response.prompt_feedback.block_reason:
                raise ValueError(f"Gemini API blocked content due to: {response.prompt_feedback.block_reason}")
            elif response.candidates:
                # If there are candidates but no parts, it might be due to safety settings blocking content.
                # You might inspect response.candidates[0].finish_reason or safety_ratings here if needed.
                raise ValueError("Gemini API returned candidates but no accessible content. Likely due to safety settings.")
            else:
                raise ValueError("Gemini API returned an empty or unexpected response.")

    except Exception as e:
        raise RuntimeError(f"Error communicating with Gemini API: {e}")