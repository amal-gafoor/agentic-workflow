import re
import json
from llm_wrapper import safe_llm_call

REQUIRED_FIELDS = [
    'NAME',
    'ADDRESS',
    'CITY',
    'DISTRICT',
    'STATE',
    'PINCODE',
    'NUMBER',
    'PHONE MODEL',
    'PRODUCT',
    'COLOUR'
]

def parse_order_text(text):
    extracted = {}

    for field in REQUIRED_FIELDS:
        pattern = rf'{field}\s*:\s*(.*?)(?=\s+[A-Z ]+\s*:|$)'
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            extracted[field.lower().replace(' ','_')] = match.group(1).strip()

    return extracted

def validate_order_data(data):
    missing = []

    for field in REQUIRED_FIELDS:
        key = field.lower().replace(' ', '_')
        if key not in data or not data[key].strip():
            missing.append(field)

    if 'pincode' in data:
        if not data['pincode'].isdigit():
            return False, ['PINCODE must be numeric']

    is_valid = len(missing) == 0 
    return is_valid,missing


def llm_extract_order(text, user_id):
    prompt = f"""
Extract order details from the message.

Fields:
NAME
ADDRESS
CITY
DISTRICT
STATE
PINCODE
NUMBER
PHONE MODEL
PRODUCT
COLOUR

Return a JSON object with these fields as keys.

Message:
{text}
"""
    response = safe_llm_call(
        user_id=user_id,
        stage='extract_order',
        prompt=prompt,
        temperature=0.2,
        max_tokens=100
    )
    try:
        return json.loads(response)
    except Exception:
        return {}