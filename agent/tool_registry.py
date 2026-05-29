from agent.tools.search_products import search_products
from agent.tools.search_policies import search_policies

TOOL_REGISTRY = {
    "search_products": {
        "function": search_products,
        "description": (
            "Search for products by name, features, price, or category. "
            "Use when customer asks about product details, pricing, availability, "
            "specs, or wants to compare products."
        ),
        "parameter": "search query string about the product"
    },
    "search_policies": {
        "function": search_policies,
        "description": (
            "Search store policies. "
            "Use when customer asks about shipping, delivery time, "
            "returns, refunds, or damaged products."
        ),
        "parameter": "query string about the policy e.g. 'return policy' or 'delivery time'"
    }
}


def call_tool(tool_name: str, tool_input: str, user_id: str = "agent") -> str:
    """
    Calls a tool by name with the given input.
    Returns the tool's output as a string.
    """
    if tool_name not in TOOL_REGISTRY:
        available = list(TOOL_REGISTRY.keys())
        return f"Error: tool '{tool_name}' not found. Available tools: {available}"
 
    tool = TOOL_REGISTRY[tool_name]
    fn = tool["function"]
 
    try:
        # search_products accepts user_id, search_policies does not
        if tool_name == "search_products":
            return fn(tool_input, user_id=user_id)
        else:
            return fn(tool_input)
 
    except Exception as e:
        return f"Tool error in '{tool_name}': {str(e)}"