import json
import time
import re
import groq
from groq import Groq

from app.config import settings
from app.prompts import build_system_prompt
from app.tools import TOOL_SCHEMAS, run_tool

_client = Groq(api_key=settings.groq_api_key)


def run_agent(question: str, file_name: str, history: list | None = None) -> dict:
    """The agent loop: ask the LLM, run the tools it requests, repeat until it answers."""
    start = time.time()
    messages = [{"role": "system", "content": build_system_prompt(file_name)}]
    messages += history or []
    messages.append({"role": "user", "content": question})

    steps = []   # what the agent did, step by step (the UI shows this later)
    charts = []  # chart files the agent created

    def result(answer: str) -> dict:
        return {
            "answer": answer,
            "charts": charts,
            "steps": steps,
            "llm_calls": llm_calls,
            "latency_ms": int((time.time() - start) * 1000),
        }

    llm_calls = 0
    for _ in range(settings.max_agent_steps):
        # 1) Ask the LLM what to do next
        try:
            llm_calls += 1
            response = _client.chat.completions.create(
                model=settings.llm_model,
                messages=messages,
                tools=TOOL_SCHEMAS,
                temperature=0.1,
            )
        except groq.BadRequestError:
            # The model wrote a badly formatted tool call. Ask it to try again.
            messages.append({"role": "user",
                             "content": "Your last tool call was not valid. Try again with valid arguments."})
            steps.append({"tool": "(retry)", "args": {}, "result": "Model sent an invalid tool call"})
            continue

        msg = response.choices[0].message

        # 2) No tool requested -> this is the final answer
        if not msg.tool_calls:
            return result(msg.content or "")

        # 3) Keep the LLM's request in the conversation
        messages.append({
            "role": "assistant",
            "content": msg.content or "",
            "tool_calls": [{
                "id": tc.id,
                "type": "function",
                "function": {"name": tc.function.name, "arguments": tc.function.arguments},
            } for tc in msg.tool_calls],
        })

        # 4) Run each requested tool with OUR code and send the result back
        for tc in msg.tool_calls:
            name = tc.function.name
            try:
                args = json.loads(tc.function.arguments or "{}")
                output = run_tool(name, args)
            except json.JSONDecodeError:
                args = {}
                output = json.dumps({"error": "Arguments were not valid JSON. Try again."})

            steps.append({"tool": name, "args": args, "result": output[:300]})

                        # The chart file name sits at the start of the result, so it is found even if the result was cut short
            match = re.search(r'"chart_file":\s*"([\w.-]+\.png)"', output)
            if match:
                charts.append(match.group(1))

            messages.append({"role": "tool", "tool_call_id": tc.id, "content": output})

    # Safety stop: the agent used all its steps without giving an answer
    return result("I could not finish this within the step limit. Try asking a more specific question.")