import sys

from app.agent import run_agent

question = " ".join(sys.argv[1:]) or "Which product earned the most revenue?"
r = run_agent(question, "sales.csv")

print("\n--- Agent steps ---")
for i, s in enumerate(r["steps"], 1):
    print(f"{i}. {s['tool']}  {s['args']}")
    print(f"   -> {s['result'][:150]}")

print("\n--- Answer ---")
print(r["answer"])
print("\nCharts:", r["charts"], "| LLM calls:", r["llm_calls"], "| Time:", r["latency_ms"], "ms")