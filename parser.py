print("DEBUG: parser.py is being executed!")
import json
import re


def _extract_json_from_text(text: str) -> str | None:
    """Extract the first JSON object or array from a text string."""
    cleaned = re.sub(r"^```(?:json)?\s*", "", text.strip())
    cleaned = re.sub(r"\s*```$", "", cleaned).strip()

    try:
        json.loads(cleaned)
        return cleaned
    except json.JSONDecodeError:
        pass

    # Find the first occurrence of '{' or '['
    json_start_index = -1
    for i, char in enumerate(cleaned):
        if char == '{' or char == '[':
            json_start_index = i
            break

    if json_start_index == -1:
        return None

    # Attempt to find the matching closing brace/bracket
    # This is a simplified approach and might need more robustness for deeply nested structures
    # but should work for the expected top-level JSON object/array.
    depth = 0
    json_end_index = -1
    for i in range(json_start_index, len(cleaned)):
        if cleaned[i] == '{' or cleaned[i] == '[':
            depth += 1
        elif cleaned[i] == '}' or cleaned[i] == ']':
            depth -= 1
        
        if depth == 0 and (cleaned[i] == '}' or cleaned[i] == ']'):
            json_end_index = i
            break
    
    if json_end_index != -1:
        candidate = cleaned[json_start_index : json_end_index + 1]
        try:
            json.loads(candidate)
            return candidate
        except json.JSONDecodeError:
            pass # Continue to next potential JSON if this one fails

    return None


def parse_gemini_response(response_text: str) -> dict:
    """
    Parses the raw text response from the Gemini API, which is expected to be a JSON string.
    """
    cleaned_text = response_text.strip()
    json_string = _extract_json_from_text(cleaned_text)
    if json_string is None:
        raise ValueError(
            "Failed to extract JSON from Gemini response. "
            f"Response preview: {cleaned_text[:300]!r}"
        )

    try:
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to decode JSON response from Gemini API: {e}")
    except Exception as e:
        raise ValueError(f"An unexpected error occurred during parsing: {e}")