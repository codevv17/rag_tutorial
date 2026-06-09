# Prompt Caching — Simple Revision Notes

## 1. What Is Prompt Caching?

Prompt caching is a way for an LLM provider to reuse the computation from a repeated prompt prefix.

Instead of making the model process the same long instructions, schemas, documents, examples, or tool definitions again and again, the provider can reuse the previously processed part.

Simple mental model:

> Do not make the model reread the same textbook chapter every time. Keep the textbook chapter the same, put it first, and only change the question at the end.

---

## 2. Why Prompt Caching Matters

Prompt caching helps with:

- Lower latency
- Lower cost
- Better performance for long prompts
- More efficient agent workflows
- Repeated use of long context such as schemas, documents, rules, examples, and tool definitions

It is especially useful when you repeatedly send a large stable context with a small changing user question.

Example:

```text
Stable context:
- System instructions
- Coding rules
- Project files
- Database schema
- Examples

Changing part:
- User's latest question
```

---

## 3. The Core Principle

Prompt caching usually works by matching the beginning of the prompt.

It does not magically understand what is static or variable. The provider compares the token prefix of the new request against recently seen prompts.

If the beginning is the same, it can reuse cached computation.

Good structure:

```text
1. Stable system instructions
2. Stable developer instructions
3. Stable examples
4. Stable schema/document/context
5. Changing user question
```

Bad structure:

```text
1. Changing user question
2. Stable system instructions
3. Stable schema/document/context
```

The second version is bad because the prompt starts differently each time, so the prefix match breaks.

---

## 4. How Does the Model Know What Is Static?

The model does not really "know" semantically.

It is not thinking:

```text
This part is static.
This part is variable.
```

Instead, the provider checks something like:

```text
Have I seen this exact token prefix recently?
```

If yes, it can reuse the cached prefix.

So your job as a developer is to structure prompts so the stable parts come first and stay unchanged.

---

## 5. What Can Break Prompt Caching?

Prompt caching can fail or become less effective if you put changing content before the stable content.

Common cache-breaking examples:

```text
Current timestamp
Request ID
Random UUID
User-specific temporary text
Dynamic JSON with changing order
Different spacing or formatting
Different message order
Changing examples
Changing tool definitions
```

Example of a bad prompt:

```text
Request ID: abc123
Today is June 8, 2026

Stable instructions...
Long schema...
User question...
```

Because the request ID and date change, the beginning of the prompt changes.

Better:

```text
Stable instructions...
Long schema...

Variable metadata:
Request ID: abc123
Today is June 8, 2026

User question...
```

---

## 6. OpenAI Prompt Caching

In the OpenAI API, prompt caching is mostly automatic.

You usually do not manually create a cache or pass something like:

```python
cache=True
```

Instead, you structure your prompt properly and OpenAI detects repeated prefixes automatically for supported models.

Example:

```python
from openai import OpenAI

client = OpenAI()

STATIC_CONTEXT = '''
You are a helpful SQL tutor.

Rules:
- Explain simply.
- Use SQL Server examples.
- Avoid unnecessary complexity.

Database schema:
...
'''

response = client.responses.create(
    model="gpt-4.1-mini",
    input=[
        {"role": "system", "content": STATIC_CONTEXT},
        {"role": "user", "content": "Explain joins in SQL Server."}
    ]
)

print(response.output_text)
```

Next request:

```python
response = client.responses.create(
    model="gpt-4.1-mini",
    input=[
        {"role": "system", "content": STATIC_CONTEXT},
        {"role": "user", "content": "Explain indexes in SQL Server."}
    ]
)
```

The stable system context remains the same, so OpenAI has a better chance of reusing cached prefix computation.

---

## 7. How to Check OpenAI Cache Usage

OpenAI responses can show cached input tokens in usage details.

Conceptually, you may see something like:

```python
response.usage.input_tokens_details.cached_tokens
```

or in some response formats:

```json
{
  "prompt_tokens_details": {
    "cached_tokens": 1920
  }
}
```

Meaning:

```text
cached_tokens = number of input tokens reused from cache
```

If this number is greater than zero, prompt caching was used.

---

## 8. Claude Prompt Caching

Claude supports prompt caching more explicitly.

With Claude, you can mark where the cache should apply using:

```json
"cache_control": {"type": "ephemeral"}
```

This tells Claude:

> Cache up to this point.

---

## 9. Claude Explicit Cache Example

Example with a long SQL schema:

```python
import anthropic

client = anthropic.Anthropic()

long_schema = '''
CREATE TABLE customers (...);
CREATE TABLE orders (...);
CREATE TABLE products (...);
-- imagine this is a very long schema
'''

response = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=1000,
    system=[
        {
            "type": "text",
            "text": '''
You are a senior SQL tutor.
Use SQL Server syntax.
Explain clearly and practically.
'''
        },
        {
            "type": "text",
            "text": long_schema,
            "cache_control": {"type": "ephemeral"}
        }
    ],
    messages=[
        {
            "role": "user",
            "content": "Write a query to show total sales by customer."
        }
    ]
)
```

In this case, Claude can cache the prompt prefix up to and including the `long_schema` block.

Next time, if the instructions and schema are exactly the same, but the user question changes, Claude can reuse the cached prefix.

---

## 10. Claude Automatic Cache Example

Claude also supports a simpler top-level cache control approach:

```python
response = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=1000,
    cache_control={"type": "ephemeral"},
    system="You are a helpful SQL tutor. Explain things simply.",
    messages=[
        {
            "role": "user",
            "content": "Explain joins in SQL Server."
        }
    ]
)
```

This asks Claude to apply caching automatically where appropriate.

---

## 11. Claude Cache Usage Fields

Claude responses can include fields like:

```python
response.usage.cache_creation_input_tokens
response.usage.cache_read_input_tokens
response.usage.input_tokens
response.usage.output_tokens
```

Meaning:

```text
cache_creation_input_tokens
= tokens written into cache for the first time

cache_read_input_tokens
= tokens reused from cache
```

Typical pattern:

```text
First request:
High cache_creation_input_tokens

Second similar request:
High cache_read_input_tokens
```

---

## 12. OpenAI vs Claude

| Feature | OpenAI | Claude |
|---|---|---|
| Caching style | Mostly automatic | Explicit or automatic |
| Developer marks cache boundary? | Usually no | Yes, with `cache_control` |
| Best practice | Keep stable prefix identical | Mark stable block with cache control |
| Usage signal | `cached_tokens` | `cache_creation_input_tokens`, `cache_read_input_tokens` |
| Main mental model | Repeated prefix detection | Cache up to marked block |

---

## 13. OpenRouter and Prompt Caching

OpenRouter is a routing layer between your application and multiple model providers.

Prompt caching behavior depends on the underlying provider and model.

For example:

```text
Your app → OpenRouter → OpenAI model
Your app → OpenRouter → Anthropic model
Your app → OpenRouter → Google model
```

Each provider may handle caching differently.

So for learning prompt caching clearly:

```text
Start with OpenAI API directly
or
Start with Anthropic Claude API directly
```

Once the concept is clear, you can use OpenRouter if you want multi-provider routing.

---

## 14. Best Practices

Use this structure:

```text
1. Tools / tool definitions
2. System instructions
3. Developer rules
4. Long stable documents
5. Examples
6. Variable user question
```

Keep these stable:

```text
- Same order
- Same formatting
- Same whitespace where possible
- Same JSON key order
- Same tool definitions
- Same system prompt
```

Move these near the end:

```text
- User question
- Current date
- Request ID
- Temporary metadata
- Dynamic filters
- Short-lived context
```

---

## 15. Simple Developer Rule

Use this rule:

> Static first. Variable last. Keep the static part exactly the same.

That is the most important idea behind prompt caching.

---

## 16. Practical Use Cases

Prompt caching is useful for:

- Coding agents
- RAG systems with repeated documents
- SQL assistants with repeated schemas
- Legal or policy assistants with long documents
- Enterprise assistants with long system instructions
- Multi-turn conversations
- Tool-using agents
- Long evaluation prompts
- Repeated JSON schema validation
- Repeated business rule processing

---

## 17. Example: SQL Assistant Prompt Structure

Good design:

```text
SYSTEM:
You are a SQL Server expert.
Explain clearly.
Use simple examples.

DATABASE SCHEMA:
[large schema here]

BUSINESS RULES:
[stable business rules here]

EXAMPLES:
[stable examples here]

USER:
Write a query to calculate revenue by month.
```

Next request:

```text
SYSTEM:
Same

DATABASE SCHEMA:
Same

BUSINESS RULES:
Same

EXAMPLES:
Same

USER:
Write a query to find inactive customers.
```

This is cache-friendly because the prefix remains the same.

---

## 18. Final Mental Model

Prompt caching means:

```text
The model/provider remembers the expensive computation for a repeated beginning of the prompt.
```

OpenAI:

```text
Mostly automatic repeated-prefix caching.
```

Claude:

```text
Explicit cache boundary using cache_control, plus automatic options.
```

Your job:

```text
Put stable context first.
Keep it identical.
Put changing user-specific content at the end.
```
