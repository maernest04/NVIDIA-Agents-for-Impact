from ai_agent import AIResourceAgent, NemotronNanoClient


def run_examples():
    # If you have a real Nemotron endpoint, set NEMOTRON_API_URL and NEMOTRON_API_KEY
    client = NemotronNanoClient()
    agent = AIResourceAgent(model_client=client)

    queries = [
        "Where can I buy a parking permit?",
        "What events are on campus today?",
        "Tell me about the CS department office",
    ]

    for q in queries:
        print("Question:", q)
        print("Answer:", agent.run_once(q))
        print("---")


if __name__ == "__main__":
    run_examples()
