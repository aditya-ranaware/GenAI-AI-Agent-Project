import json
from groq import Groq
from app.config import settings

client = Groq(api_key=settings.groq_api_key)


# 1. The tool: a normal Python function
def add_numbers(a: float, b: float) -> float:
    return a + b


# 2. A description of the tool, so the LLM knows it exists and how to use it
tools = [{
    "type": "function",
    "function": {
        "name": "add_numbers",
        "description": "Add two numbers together",
        "parameters": {
            "type": "object",
            "properties": {
                "a": {"type": "number"},
                "b": {"type": "number"},
            },
            "required": ["a", "b"],
        },
    },
}]

messages = [{"role": "user", "content": "What is 1234.5 plus 6789.25?"}]

# 3. First call: the LLM decides whether to use the tool
response = client.chat.completions.create(
    model=settings.llm_model, messages=messages, tools=tools
)
msg = response.choices[0].message

if not msg.tool_calls:
    print("The LLM answered directly without a tool:", msg.content)
    raise SystemExit

call = msg.tool_calls[0]
print("1) LLM asks to call:", call.function.name, call.function.arguments)

# 4. YOUR code runs the tool
args = json.loads(call.function.arguments)
result = add_numbers(**args)
print("2) Our code ran the tool, result:", result)

# 5. Send the result back so the LLM can write the final answer
messages.append({
    "role": "assistant",
    "content": msg.content or "",
    "tool_calls": [{
        "id": call.id,
        "type": "function",
        "function": {"name": call.function.name, "arguments": call.function.arguments},
    }],
})
messages.append({"role": "tool", "tool_call_id": call.id, "content": str(result)})

final = client.chat.completions.create(
    model=settings.llm_model, messages=messages, tools=tools
)
print("3) Final answer:", final.choices[0].message.content)