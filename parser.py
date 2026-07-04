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

    for start_char, end_char in (("{", "}"), ("[", "]")):
        start_idx = cleaned.find(start_char)
        if start_idx == -1:
            continue

        depth = 0
        for idx in range(start_idx, len(cleaned)):
            if cleaned[idx] == start_char:
                depth += 1
            elif cleaned[idx] == end_char:
                depth -= 1
                if depth == 0:
                    candidate = cleaned[start_idx:idx + 1]
                    try:
                        json.loads(candidate)
                        return candidate
                    except json.JSONDecodeError:
                        break

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