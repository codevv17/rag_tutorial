import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    default_headers={
        "HTTP-Referer": "http://localhost:3000",
        "X-Title": "OpenRouter Tutorial"
    }
)

# response = client.chat.completions.create(
#     model="openai/gpt-4o-mini",
#     messages=[
#         {
#             "role": "user",
#             "content": "Explain OpenRouter in simple terms."
#         }
#     ],
#     temperature=0.2
# )

# print(response.choices[0].message.content)

models = [
    "openai/gpt-4o-mini",
    "google/gemini-2.5-flash",
    "deepseek/deepseek-chat",
    "anthropic/claude-sonnet-4.6",
    "anthropic/claude-sonnet-4.5"
]

prompt = "Explain RAG in 5 bullet points."

for model in models:
    print("\n" + "=" * 80)
    print(f"MODEL: {model}")

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=500
        )

        print(response.choices[0].message.content)

    except Exception as e:
        print(f"FAILED: {model}")
        print(f"ERROR: {e}")