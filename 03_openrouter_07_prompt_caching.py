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
        "X-Title": "OpenRouter Prompt Caching Tutorial"
    }
)


# Large stable prompt.
# In real projects, this could be coding standards, database schema,
# enterprise rules, or long agent instructions.
STABLE_CONTEXT = """
You are an expert enterprise data engineering assistant.

You help with:
- SQL Server
- Azure Data Factory
- Databricks
- PySpark
- Microsoft Fabric
- Power BI
- Data architecture
- RAG applications
- LLM gateway design

Rules:
1. Give practical code-first answers.
2. Prefer simple, production-friendly solutions.
3. Explain assumptions clearly.
4. Avoid unnecessary complexity.
5. When writing SQL, use readable formatting.
6. When writing Python, include clear function names and basic error handling.

Example project context:
The user is building tutorials for OpenRouter using Python, .env files,
and one Python file per concept. The user has already completed:
- basic OpenRouter calls
- multiple model testing
- streaming
- JSON structured output
- model fallback
- tool calling
- web search
- provider routing

The current topic is prompt caching.
"""


def ask_with_prompt_caching(user_question: str) -> dict:
    start_time = time.time()

    response = client.chat.completions.create(
        model="anthropic/claude-sonnet-4.5",
        messages=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": STABLE_CONTEXT,

                        # Anthropic-style prompt caching breakpoint.
                        # This tells the provider this block is cacheable.
                        "cache_control": {
                            "type": "ephemeral"
                        }
                    }
                ]
            },
            {
                "role": "user",
                "content": user_question
            }
        ],
        temperature=0.2,
        max_tokens=500
    )

    latency_seconds = round(time.time() - start_time, 2)

    return {
        "model": response.model,
        "latency_seconds": latency_seconds,
        "answer": response.choices[0].message.content,
        "usage": response.usage
    }


if __name__ == "__main__":
    questions = [
        "Explain prompt caching in simple terms.",
        "Why is prompt caching useful for RAG applications?",
        "Why is prompt caching useful for AI agents?"
    ]

    for question in questions:
        print("\n" + "=" * 80)
        print("Question:", question)

        try:
            result = ask_with_prompt_caching(question)

            print("Model:", result["model"])
            print("Latency seconds:", result["latency_seconds"])
            print("Usage:", result["usage"])
            print("\nAnswer:")
            print(result["answer"])

        except Exception as e:
            print("Prompt caching request failed.")
            print("Error:")
            print(e)