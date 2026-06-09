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
        "X-Title": "OpenRouter Tutorial"
    }
)


def ask_with_openrouter_fallback(prompt: str) -> str:
    response = client.chat.completions.create(
        model="openai/gpt-4o-mini",
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

        # OpenRouter-specific parameters go here
        extra_body={
            "models": [
                "google/gemini-2.5-flash",
                "openai/gpt-4o-mini",
                "deepseek/deepseek-chat"
            ]
        }
    )

    print("Model returned by API:", response.model)

    return response.choices[0].message.content


if __name__ == "__main__":
    user_prompt = "Explain model fallback in OpenRouter in simple terms."

    try:
        result = ask_with_openrouter_fallback(user_prompt)

        print("\nFinal Answer:\n")
        print(result)

    except Exception as e:
        print("\nRequest failed even after fallback attempts.")
        print("Error:")
        print(e)