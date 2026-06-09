import os
import time
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY is missing. Please add it to your .env file.")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
    default_headers={
        "HTTP-Referer": "http://localhost:3000",
        "X-Title": "OpenRouter Provider Routing Tutorial"
    }
)


def ask_with_provider_policy(prompt: str, provider_policy: dict) -> dict:
    start_time = time.time()

    response = client.chat.completions.create(
        model="deepseek/deepseek-chat",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful AI assistant. Answer clearly and concisely."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2,
        max_tokens=500,
        extra_body={
            "provider": provider_policy
        }
    )

    latency_seconds = round(time.time() - start_time, 2)

    return {
        "model": response.model,
        "latency_seconds": latency_seconds,
        "answer": response.choices[0].message.content
    }


if __name__ == "__main__":
    prompt = "Explain provider routing in OpenRouter in 4 simple bullet points."

    provider_policies = {
        "cheapest": {
            "sort": "price",
            "allow_fallbacks": True
        },
        "lowest_latency": {
            "sort": "latency",
            "allow_fallbacks": True
        },
        "highest_throughput": {
            "sort": "throughput",
            "allow_fallbacks": True
        },
        "enterprise_private": {
            "sort": "price",
            "data_collection": "deny",
            "allow_fallbacks": True
        }
    }

    for policy_name, policy in provider_policies.items():
        print("\n" + "=" * 80)
        print(f"Provider policy: {policy_name}")
        print(f"Policy config: {policy}")

        try:
            result = ask_with_provider_policy(prompt, policy)

            print("Model:", result["model"])
            print("Latency seconds:", result["latency_seconds"])
            print("\nAnswer:")
            print(result["answer"])

        except Exception as e:
            print(f"Failed for provider policy: {policy_name}")
            print("Error:")
            print(e)