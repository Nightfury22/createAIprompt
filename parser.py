print("DEBUG: parser.py is being executed!")

import json
import re


def _extract_json_from_text(text: str) -> str | None:
    """
    Extract a valid JSON object from Gemini response.
    Handles:
    - ```json ... ```
    - extra text before/after JSON
    - plain JSON
    """

    if not text:
        return None

    cleaned = text.strip()

    # Remove markdown fences
    cleaned = re.sub(r"^```json\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"^```\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    cleaned = cleaned.strip()

    # Fast path
    try:
        json.loads(cleaned)
        return cleaned
    except Exception:
        pass

    # Find first JSON object
    start = cleaned.find("{")

    if start == -1:
        return None

    depth = 0
    in_string = False
    escape = False

    for i in range(start, len(cleaned)):
        ch = cleaned[i]

        if escape:
            escape = False
            continue

        if ch == "\\":
            escape = True
            continue

        if ch == '"':
            in_string = not in_string
            continue

        if in_string:
            continue

        if ch == "{":
            depth += 1

        elif ch == "}":
            depth -= 1

            if depth == 0:
                candidate = cleaned[start : i + 1]

                try:
                    json.loads(candidate)
                    return candidate
                except Exception:
                    return None

    return None


def parse_gemini_response(response_text: str) -> dict:
    """
    Parse Gemini response into dictionary.
    """

    print("\n========== RAW RESPONSE ==========")
    print(response_text)
    print("==================================\n")

    json_string = _extract_json_from_text(response_text)

    if json_string is None:
        raise ValueError(
            "Failed to extract JSON from Gemini response.\n"
            f"Response preview:\n{response_text[:1000]}"
        )

    try:
        parsed_data = json.loads(json_string)

        required_defaults = {
            "title": "",
            "story": "",
            "scenes": [],
            "thumbnail_prompt": "",
            "youtube_description": "",
            "hashtags": [],
        }

        for key, default_value in required_defaults.items():
            parsed_data.setdefault(key, default_value)

        return parsed_data

    except Exception as e:
        raise ValueError(f"JSON parsing failed: {e}")