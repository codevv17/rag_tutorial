import os
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
        "X-Title": "OpenRouter Web Search Tutorial"
    }
)


def ask_with_web_search(prompt: str) -> str:
    response = client.chat.completions.create(
        model="openai/gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful AI assistant. "
                    "Use web search when current information is needed. "
                    "Include sources when available."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2,
        max_tokens=800,

        # OpenRouter-specific web plugin
        extra_body={
            "plugins": [
                {
                    "id": "web",
                    "max_results": 5
                }
            ]
        }
    )

    return response.choices[0].message.content


if __name__ == "__main__":
    user_prompt = "What are the latest important updates in Microsoft Fabric? Give me 5 bullet points with sources."

    try:
        answer = ask_with_web_search(user_prompt)

        print("\nFinal Answer:\n")
        print(answer)

    except Exception as e:
        print("\nWeb search request failed.")
        print("Error:")
        print(e)