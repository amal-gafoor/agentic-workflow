import re
from llm_wrapper import safe_llm_call
from agent.tool_registry import TOOL_REGISTRY, call_tool

# ─────────────────────────────────────────────
# SYSTEM PROMPT
# Teaches the LLM what tools it has and
# exactly what format to follow
# ─────────────────────────────────────────────
def build_system_prompt() -> str:
    # Dynamically build tool descriptions from registry
    tool_descriptions = ""
    for i, (name, data) in enumerate(TOOL_REGISTRY.items(), 1):
        tool_descriptions += f"{i}. {name} — {data['description']}\n"
 
    return f"""You are a helpful customer support assistant for a phone case store.
You answer customer questions about products and store policies.
 
You have access to these tools:
{tool_descriptions}
STRICT FORMAT RULES — follow exactly:
 
When you need to use a tool:
THOUGHT: <your reasoning about what to do>
ACTION: <tool_name>
INPUT: <your search query>
 
When you have enough information to answer the customer:
THOUGHT: I have enough information to answer.
FINAL ANSWER: <your friendly, clear answer to the customer>
 
Important rules:
- Always write THOUGHT before ACTION or FINAL ANSWER
- Never guess product prices or policy details — always use a tool
- If the question is about both a product AND a policy, call both tools one at a time
- Keep your FINAL ANSWER short, friendly, and clear
- If no results found, politely say so
"""

# ─────────────────────────────────────────────
# REACT LOOP
# ─────────────────────────────────────────────
# ─────────────────────────────────────────────
# REACT LOOP
# ─────────────────────────────────────────────
def run_react_agent(
    user_query: str,
    user_id: str = "agent",
    history: list = None,
    max_iterations: int = 5
) -> str:
    """
    Runs the ReAct loop for a customer query.
 
    Flow per iteration:
    1. Ask LLM what to do next
    2. If FINAL ANSWER → return it
    3. If ACTION → call tool → feed result back
    4. Repeat until FINAL ANSWER or max_iterations reached
    """
 
    # Build conversation history text for context
    history_text = ""
    if history:
        for msg in history[-4:]:  # last 4 messages only
            history_text += f"{msg['role']}: {msg['content']}\n"
 
    # Initial prompt combining system prompt + history + query
    system_prompt = build_system_prompt()
 
    full_prompt = f"""{system_prompt}
 
Conversation so far:
{history_text}
Customer: {user_query}
"""
 
    # Conversation turns for this agent run
    turns = [{"role": "user", "content": full_prompt}]
 
    for iteration in range(max_iterations):
        print(f"\n[Agent] Iteration {iteration + 1}")
 
        # Step 1 — call LLM
        llm_output = safe_llm_call(
            user_id=user_id,
            stage=f"react_iter_{iteration + 1}",
            prompt=build_turns_prompt(turns),
            temperature=0.1,
            max_tokens=400
        )
 
        if llm_output is None:
            return "Sorry, I had trouble processing that. Please try again."
 
        print(f"[Agent] LLM output:\n{llm_output}\n")
 
        # Step 2 — check for FINAL ANSWER
        if "FINAL ANSWER:" in llm_output:
            answer = llm_output.split("FINAL ANSWER:")[-1].strip()
            return answer
 
        # Step 3 — parse ACTION and INPUT
        action_match = re.search(r"ACTION:\s*(\w+)", llm_output)
        input_match  = re.search(r"INPUT:\s*(.+)",   llm_output)
 
        if not action_match or not input_match:
            # LLM didn't follow format — nudge it
            turns.append({"role": "assistant", "content": llm_output})
            turns.append({
                "role": "user",
                "content": (
                    "Please follow the exact format:\n"
                    "THOUGHT: ...\nACTION: tool_name\nINPUT: query\n\n"
                    "Or if you have enough info:\n"
                    "THOUGHT: ...\nFINAL ANSWER: your answer"
                )
            })
            continue
 
        tool_name  = action_match.group(1).strip()
        tool_input = input_match.group(1).strip()
 
        print(f"[Agent] Calling tool: {tool_name} | Input: {tool_input}")
 
        # Step 4 — call the tool
        observation = call_tool(tool_name, tool_input, user_id=user_id)
 
        print(f"[Agent] Observation: {observation[:200]}...")
 
        # Step 5 — add LLM output + observation back into turns
        turns.append({"role": "assistant", "content": llm_output})
        turns.append({
            "role": "user",
            "content": (
                f"OBSERVATION:\n{observation}\n\n"
                "Now continue. Either call another tool if needed, "
                "or give the FINAL ANSWER to the customer."
            )
        })
 
    # Max iterations reached
    return "I'm sorry, I wasn't able to find a complete answer. Could you rephrase your question?"

def build_turns_prompt(turns: list) -> str:
    """Converts turn list into a single prompt string for safe_llm_call."""
    prompt = ""
    for turn in turns:
        role = turn["role"].capitalize()
        prompt += f"{role}: {turn['content']}\n\n"
    return prompt.strip()


# ─────────────────────────────────────────────
# TEST
# ─────────────────────────────────────────────
if __name__ == "__main__":
    from rag_pipeline.embeddings import get_embedding_model
    print("Loading embedding model...")
    get_embedding_model()
    print("Ready.\n")
 
    test_queries = [
        "What is the price of the rugged armor case for Samsung?",
        "What is your return policy?",
        "Do you have a wallet case for iPhone? Also how long does delivery take?",
    ]
 
    for query in test_queries:
        print(f"\n{'='*55}")
        print(f"Customer: {query}")
        print(f"{'='*55}")
        answer = run_react_agent(query)
        print(f"\nAgent: {answer}")
        print()