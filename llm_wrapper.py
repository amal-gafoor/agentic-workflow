import time 
from config  import get_groq_client,GROQ_MODEL
from monitoring import log_llm_usage

client = get_groq_client()

def safe_llm_call(user_id, stage, prompt, temperature, max_tokens):

    try:
        start = time.time()
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{'role': 'user', 'content': prompt}],
            temperature= temperature,
            max_tokens=max_tokens
        )

        latency = time.time() - start

        log_llm_usage(user_id, stage, response, latency)

        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f'[LLM ERROR] stage:{stage} | User: {user_id} | Error: {e}')
        return None