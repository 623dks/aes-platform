import json
import re

def parse_model_output(output_text: str) -> dict:
    """
    Robustly extract the JSON scoring object from the Llama generated text.
    Handles extra text, markdown formatting, and malformed JSON.
    """
    # 1. Clean common formatting artifacts (e.g. ```json ... ```)
    cleaned = output_text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    if cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()

    # 2. Try direct parse
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
        
    # 3. Fallback: regex extraction if model added conversational filler
    # Looks for something roughly matching {"score": X, "justification": "Y"}
    match = re.search(r'\{[^{}]*("score"|\'score\')[^{}]*\}', cleaned)
    if match:
        try:
            # Replace single quotes with double quotes for valid JSON
            json_str = match.group(0).replace("'", '"')
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass
            
    # 4. Final Fallback: naive regex for just the score digit
    score_match = re.search(r'score["\']?\s*:\s*(\d)', cleaned, re.IGNORECASE)
    if score_match:
        return {
            "score": int(score_match.group(1)),
            "justification": "Fallback: Extracted score via regex due to malformed JSON.",
            "raw_output": output_text
        }
        
    # 5. Failure state
    return {
        "score": -1, # Indicates failure
        "justification": "Error: Failed to parse model output.",
        "raw_output": output_text
    }
