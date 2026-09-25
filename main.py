"""CLI entry for Meridian Support."""
from __future__ import annotations

from meridian_support.agent import create_support_agent


def main() -> None:
    agent = create_support_agent(debug=False)
    print("Meridian Support CLI. Type 'exit' to quit.\n")
    history: list[tuple[str, str]] = []
    while True:
        user = input("You: ").strip()
        if user.lower() in {"exit", "quit"}:
            print("Bye.")
            break
        if not user:
            continue
        result = agent.invoke({"messages": history + [("human", user)]})
        answer = result["messages"][-1].content
        print(f"\nAgent: {answer}\n")
        history.extend([("human", user), ("ai", answer)])


if __name__ == "__main__":
    main()
