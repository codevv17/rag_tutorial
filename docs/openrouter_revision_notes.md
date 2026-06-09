# OpenRouter Revision Notes

## 1. What OpenRouter Is

OpenRouter is a model gateway. Instead of using a separate API key and SDK setup for every model provider, you can use one OpenRouter API endpoint and call many different models.

Typical providers/models you can access through OpenRouter include:

- OpenAI models
- Anthropic Claude models
- Google Gemini models
- DeepSeek models
- Meta Llama models
- Qwen models
- Mistral models
- Other hosted open-source models

The main idea:

```text
Your Python App
   ↓
OpenRouter API
   ↓
Selected Model / Provider
   ↓
Response
```

OpenRouter is useful when you want to compare models, switch models, use fallback models, route by price or speed, and build an LLM gateway for your own app.

---

## 2. Basic Python Project Setup

Recommended folder structure:

```text
rag_tutorial/
│
├── .env
├── requirements.txt
├── 01_openrouter_basic.py
├── 02_openrouter_streaming.py
├── 03_openrouter_multiple_models.py
├── 04_openrouter_json_output.py
├── 05_openrouter_model_fallback.py
├── 06_openrouter_tool_calling.py
├── 07_openrouter_web_search.py
├── 08_openrouter_provider_routing.py
└── 09_openrouter_prompt_caching.py
```

`.env` file:

```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

Install packages:

```bash
uv add openai python-dotenv
```

or:

```bash
pip install openai python-dotenv
```

Basic client setup:

```python
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
```

Important point:

```python
base_url="https://openrouter.ai/api/v1"
```

This tells the OpenAI SDK to call OpenRouter instead of OpenAI directly.

---

## 3. Basic Chat Completion

```python
response = client.chat.completions.create(
    model="openai/gpt-4o-mini",
    messages=[
        {"role": "user", "content": "Explain RAG in simple terms."}
    ],
    temperature=0.2,
    max_tokens=500
)

print(response.choices[0].message.content)
```

Best practice: always set `max_tokens` while testing.

Why?

Some models may assume a very large default output size. You saw this with Gemini Flash:

```text
You requested up to 65535 tokens, but can only afford 15981.
```

Fix:

```python
max_tokens=500
```

---

## 4. Multiple Model Testing

Purpose: compare answers from multiple models using the same prompt.

```python
models = [
    "openai/gpt-4o-mini",
    "google/gemini-2.5-flash",
    "deepseek/deepseek-chat"
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
```

Important lesson: do not let one failed model stop the whole tutorial. Use `try/except`.

Common error:

```text
No endpoints found for anthropic/claude-3.5-sonnet
```

Meaning: the model ID is outdated or unavailable. Check OpenRouter model catalog and use current model IDs.

---

## 5. Streaming

Purpose: make responses appear token-by-token, similar to ChatGPT UI.

```python
stream = client.chat.completions.create(
    model="openai/gpt-4o-mini",
    messages=[
        {"role": "user", "content": "Explain vector databases in simple terms."}
    ],
    stream=True,
    max_tokens=500
)

for chunk in stream:
    delta = chunk.choices[0].delta.content
    if delta:
        print(delta, end="", flush=True)
```

Use streaming when building a chatbot UI.

---

## 6. JSON / Structured Output

Purpose: get clean JSON instead of paragraph text.

Useful for:

- Classification
- Data extraction
- Task extraction
- Routing
- Agent workflows
- API responses

Example:

```python
response = client.chat.completions.create(
    model="openai/gpt-4o-mini",
    messages=[
        {
            "role": "system",
            "content": "You extract structured task information. Return only valid JSON."
        },
        {
            "role": "user",
            "content": "Remind me to review Azure pipeline logs tomorrow morning with high priority."
        }
    ],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "task_extraction",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "task": {"type": "string"},
                    "date": {"type": "string"},
                    "priority": {"type": "string"}
                },
                "required": ["task", "date", "priority"],
                "additionalProperties": False
            }
        }
    },
    temperature=0.2,
    max_tokens=500
)

print(response.choices[0].message.content)
```

Key idea: structured output is critical for building real applications, because apps need predictable data, not only natural-language answers.

---

## 7. Model Fallback

Purpose: if one model fails, OpenRouter can try another model.

Example fallback order:

```text
1. openai/gpt-4o-mini
2. deepseek/deepseek-chat
3. google/gemini-2.5-flash
```

Important correction: with the OpenAI Python SDK, OpenRouter-specific parameters such as `models` must go inside `extra_body`.

Wrong:

```python
response = client.chat.completions.create(
    model="openai/gpt-4o-mini",
    models=[
        "openai/gpt-4o-mini",
        "deepseek/deepseek-chat"
    ]
)
```

This gave the error:

```text
Completions.create() got an unexpected keyword argument 'models'. Did you mean 'model'?
```

Correct:

```python
response = client.chat.completions.create(
    model="openai/gpt-4o-mini",
    messages=[
        {"role": "user", "content": "Explain model fallback in simple terms."}
    ],
    temperature=0.2,
    max_tokens=500,
    extra_body={
        "models": [
            "openai/gpt-4o-mini",
            "deepseek/deepseek-chat",
            "google/gemini-2.5-flash"
        ]
    }
)

print("Model returned by API:", response.model)
print(response.choices[0].message.content)
```

Key idea:

```text
Your app sends one request.
OpenRouter tries multiple models behind the scenes.
```

---

## 8. Tool Calling / Function Calling

Purpose: allow the model to request a controlled action, but your Python code executes the action.

The model does not directly run Python. It only says something like:

```text
Call calculate_total_price with quantity=3, unit_price=19.99, tax_rate=0.13
```

Then your app executes the function and sends the result back to the model.

Flow:

```text
User question
   ↓
Model decides tool is needed
   ↓
Your Python code runs the function
   ↓
Tool result is sent back to model
   ↓
Model gives final answer
```

Example function:

```python
def calculate_total_price(quantity: int, unit_price: float, tax_rate: float = 0.0) -> dict:
    subtotal = quantity * unit_price
    tax_amount = subtotal * tax_rate
    total = subtotal + tax_amount

    return {
        "quantity": quantity,
        "unit_price": unit_price,
        "tax_rate": tax_rate,
        "subtotal": round(subtotal, 2),
        "tax_amount": round(tax_amount, 2),
        "total": round(total, 2)
    }
```

Tool schema:

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "calculate_total_price",
            "description": "Calculate total price based on quantity, unit price, and tax rate.",
            "parameters": {
                "type": "object",
                "properties": {
                    "quantity": {"type": "integer"},
                    "unit_price": {"type": "number"},
                    "tax_rate": {"type": "number"}
                },
                "required": ["quantity", "unit_price"],
                "additionalProperties": False
            }
        }
    }
]
```

First model call:

```python
first_response = client.chat.completions.create(
    model="openai/gpt-4o-mini",
    messages=messages,
    tools=tools,
    tool_choice="auto",
    temperature=0.2,
    max_tokens=500
)
```

Key idea:

```text
The model chooses the function.
Your application executes the function.
The model explains the result.
```

Future tools could be:

```python
get_customer_orders()
run_sql_query()
search_documents()
create_calendar_event()
send_email_draft()
check_pipeline_status()
```

---

## 9. Web Search

Purpose: use current internet information when model memory may be outdated.

Use web search for:

- Latest model IDs
- Current pricing
- Recent product updates
- Regulations
- News
- Schedules
- Recently changed documentation

Do not use web search for stable concepts like:

- Explain RAG
- Explain vector database
- Write a Python function
- Explain SQL joins

Example using OpenRouter web plugin:

```python
response = client.chat.completions.create(
    model="openai/gpt-4o-mini",
    messages=[
        {
            "role": "system",
            "content": "Use web search when current information is needed. Include sources when available."
        },
        {
            "role": "user",
            "content": "What are the latest important updates in Microsoft Fabric? Give me 5 bullet points with sources."
        }
    ],
    temperature=0.2,
    max_tokens=800,
    extra_body={
        "plugins": [
            {
                "id": "web",
                "max_results": 5
            }
        ]
    }
)

print(response.choices[0].message.content)
```

Alternative model syntax:

```python
model="openai/gpt-4o-mini:online"
```

Key idea:

```text
Use web search only when freshness matters.
```

---

## 10. Provider Routing

Purpose: control which backend provider serves a selected model.

Model routing means:

```text
Which model should answer?
Example: GPT vs Claude vs DeepSeek vs Gemini
```

Provider routing means:

```text
Who should host/serve that selected model?
Example: cheapest provider vs fastest provider vs stricter data-policy provider
```

OpenRouter can route the same model through different providers based on:

- Price
- Latency
- Throughput
- Availability
- Provider data policy
- Feature support

Example:

```python
response = client.chat.completions.create(
    model="deepseek/deepseek-chat",
    messages=[
        {"role": "user", "content": "Explain provider routing in 4 bullet points."}
    ],
    temperature=0.2,
    max_tokens=500,
    extra_body={
        "provider": {
            "sort": "price",
            "allow_fallbacks": True
        }
    }
)
```

Provider policy examples:

### Cheapest

```python
extra_body={
    "provider": {
        "sort": "price",
        "allow_fallbacks": True
    }
}
```

Use for experiments and batch jobs.

### Lowest latency

```python
extra_body={
    "provider": {
        "sort": "latency",
        "allow_fallbacks": True
    }
}
```

Use for chatbot UI.

### Highest throughput

```python
extra_body={
    "provider": {
        "sort": "throughput",
        "allow_fallbacks": True
    }
}
```

Use when you care about fast token generation.

### Enterprise/private routing

```python
extra_body={
    "provider": {
        "sort": "price",
        "data_collection": "deny",
        "require_parameters": True,
        "allow_fallbacks": True
    }
}
```

Use when sending internal/private content.

Shortcuts:

```python
model="deepseek/deepseek-chat:floor"   # prefer cheapest provider
model="deepseek/deepseek-chat:nitro"   # prefer faster throughput
```

Big picture:

```text
Your Python App
   ↓
Task Router
   ↓
OpenRouter Model Selection
   ↓
OpenRouter Provider Routing
   ↓
Actual Provider Endpoint
   ↓
Final Response
```

---

## 11. Prompt Caching

Purpose: reduce cost and latency when you repeatedly send the same large prompt prefix.

Useful when your prompt includes stable repeated context like:

- Long system prompt
- Coding standards
- Database schema
- Business rules
- Tool instructions
- RAG instructions
- Enterprise policies

Example pattern:

```text
Stable context: same every time
Dynamic question: changes every request
```

Prompt caching works best when the stable content is at the beginning and does not change.

Good:

```text
System prompt stays exactly the same.
Only the user question changes.
```

Bad:

```text
Adding timestamps to the system prompt.
Changing/reordering schema text.
Mixing dynamic tool results into the cached block.
```

Simple implicit caching style:

```python
response = client.chat.completions.create(
    model="openai/gpt-4o-mini",
    messages=[
        {
            "role": "system",
            "content": STABLE_CONTEXT
        },
        {
            "role": "user",
            "content": user_question
        }
    ],
    temperature=0.2,
    max_tokens=500
)
```

Explicit Anthropic-style cache control example:

```python
response = client.chat.completions.create(
    model="anthropic/claude-sonnet-4.5",
    messages=[
        {
            "role": "system",
            "content": [
                {
                    "type": "text",
                    "text": STABLE_CONTEXT,
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
```

Important distinction:

### Prompt caching

```text
Same large prefix reused.
Different questions can still benefit.
Provider still generates a new answer.
```

### Response caching

```text
Exact same request repeated.
OpenRouter may return the same cached response.
No new generation needed.
```

For now, focus on prompt caching.

---

## 12. Common Errors and Fixes

### Error 1: Outdated model ID

```text
No endpoints found for anthropic/claude-3.5-sonnet
```

Cause: model ID is outdated or unavailable.

Fix: check OpenRouter model catalog and update the model name.

---

### Error 2: Not enough credits / huge max token request

```text
This request requires more credits, or fewer max_tokens.
You requested up to 65535 tokens...
```

Cause: provider assumes a very large output size.

Fix:

```python
max_tokens=500
```

---

### Error 3: `models` keyword not accepted

```text
Completions.create() got an unexpected keyword argument 'models'. Did you mean 'model'?
```

Cause: OpenAI Python SDK does not accept OpenRouter-specific `models` directly.

Fix:

```python
extra_body={
    "models": [
        "openai/gpt-4o-mini",
        "deepseek/deepseek-chat"
    ]
}
```

---

## 13. Recommended Learning Sequence

You followed this sequence:

```text
1. Basic OpenRouter call
2. Multiple model comparison
3. Streaming
4. JSON / structured output
5. Model fallback
6. Tool calling
7. Web search
8. Provider routing
9. Prompt caching
```

Recommended next topics:

```text
10. Usage logging with SQLite
11. Cost and latency tracking
12. Simple model router in Python
13. LangChain integration
14. LangGraph workflow
15. RAG with OpenRouter
16. FastAPI app around OpenRouter
17. Evaluation and model comparison dashboard
```

---

## 14. Practical Architecture for Your Future App

A clean architecture would look like this:

```text
Frontend / API Client
        ↓
FastAPI Backend
        ↓
Task Classifier / Router
        ↓
OpenRouter Client
        ↓
Model Fallback + Provider Routing
        ↓
Tools / RAG / Web Search if needed
        ↓
Response Formatter
        ↓
Logging + Evaluation
```

Possible app components:

```text
LangChain / LangGraph  → workflow orchestration
OpenRouter             → model gateway
Vector DB              → RAG/document search
SQLite/Postgres        → logging and evaluation
FastAPI                → backend API
Streamlit/React        → frontend UI
```

---

## 15. Core Mental Model

OpenRouter is not just a way to call a model.

It can become the model gateway layer in your application.

```text
Single model call:
Your app → one model

OpenRouter gateway:
Your app → OpenRouter → model selection → provider routing → fallback → response
```

The real value is flexibility:

```text
Use cheaper models for simple tasks.
Use stronger models for reasoning.
Use fallback when one model fails.
Use provider routing for cost/speed/privacy.
Use tools when actions are needed.
Use web search when current information is needed.
Use prompt caching when large repeated context is used.
```

That is the foundation of a production-ready LLM gateway.
