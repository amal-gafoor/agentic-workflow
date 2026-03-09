from prompts import INTENT_PROMPT,REWRITE_PROMPT
from llm_wrapper import safe_llm_call


def classify_intent(question,history,user_id):
    history_text = ''
    for msg in history[-3:]:
        history_text += f"{msg['role']}: {msg['content']}\n"
    prompt = INTENT_PROMPT.format(
        question=question,
        history=history_text
        )
    raw_intent = safe_llm_call(
        user_id=user_id,
        stage='intent',
        prompt= prompt,
        temperature=0,
        max_tokens=10
        )

    if raw_intent is None:
        return 'unknown'
    if "product" in raw_intent:
        return "product_query"
    elif "place" in raw_intent:
        return "place_order"
    elif "status" in raw_intent:
        return "order_status"
    else:
        return "unknown"



def rewrite_query(question,history,user_id):
    history_text = ''
    for msg in history[-3:]:
        history_text += f"{msg['role']}: {msg['content']}\n"

    prompt = REWRITE_PROMPT.format(
        history = history_text,
        question = question
    )

    response = safe_llm_call(
        user_id=user_id,
        stage='rewrite',
        prompt= prompt,
        temperature=0.2,
        max_tokens=50
        )
    
    if response is None:
        return question

    return response