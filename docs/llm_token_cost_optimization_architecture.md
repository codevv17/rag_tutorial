# LLM Apps & Agents — Token Cost Optimization Architecture

## 1. Core Idea

In real LLM applications, cost optimization is not just about choosing a cheaper model.

It is an architecture problem.

The main rule is:

> Do not pay the LLM to read, reason, or write anything it does not need to.

A good LLM system uses expensive model intelligence only where it creates real value. Everything else should be handled by caching, retrieval, routing, compression, deterministic code, or cheaper models.

---

## 2. Why Token Cost Becomes Important

LLM apps become expensive because they often include:

- Long system prompts
- Large conversation history
- Repeated tool definitions
- Repeated business rules
- Repeated schemas
- Large documents
- Multiple agent steps
- Retry loops
- Long output responses
- Strong models used for simple tasks

In a small demo, this does not matter much.

In production, with many users and repeated workflows, it becomes a major cost driver.

---

## 3. The Best Mental Model

A cost-optimized LLM app should work like this:

```text
Cheap logic handles simple tasks.
Retrieval brings only relevant context.
Caching avoids repeated work.
Code handles deterministic calculations.
Strong models are used only when needed.
```

Bad architecture:

```text
Send everything to the strongest model every time.
```

Good architecture:

```text
Classify → retrieve → compress → route → answer → validate → cache
```

---

## 4. Strategy 1 — Use the Smallest Capable Model

Do not use the most powerful model for every task.

Use model tiers:

```text
Simple task   → cheap/fast model
Normal task   → medium model
Hard task     → strong model
Risky task    → strong model + validation
Failed task   → fallback model
```

Example:

```text
Intent classification       → small model
Basic summarization         → small/medium model
SQL generation              → medium/strong model
Complex code debugging      → strong model
Critical validation         → strong model
Final formatting            → cheap model or code
```

This is usually one of the biggest cost-saving strategies.

---

## 5. Strategy 2 — Use Model Routing

Before sending the request to a powerful model, classify the task.

Example router categories:

```text
greeting
documentation lookup
SQL generation
code debugging
data analysis
summarization
agent task
unsafe or unsupported task
```

Then route accordingly:

```text
Greeting               → no LLM or cheap model
Documentation lookup   → RAG + cheap/medium model
SQL generation         → medium model
Complex debugging      → strong model
Multi-step planning    → strong model
```

This prevents overusing expensive models.

---

## 6. Strategy 3 — Use Model Fallback Carefully

Fallback means trying another model if the first one fails.

Example:

```text
Try cheap model first.
If it fails, times out, or produces invalid output, try stronger model.
```

But fallback should not be uncontrolled.

Bad fallback:

```text
Always call 3 models for every request.
```

Good fallback:

```text
Call stronger model only when needed.
```

Fallback conditions can include:

- API failure
- Timeout
- Invalid JSON
- Low confidence
- Failed validation
- SQL parser error
- Safety/risk threshold exceeded

---

## 7. Strategy 4 — Use Prompt Caching

Prompt caching helps when you repeatedly send the same stable context.

Stable context can include:

```text
system prompt
developer rules
tool definitions
database schema
business rules
examples
long reference documents
```

Good prompt structure:

```text
Stable instructions
Stable tools
Stable examples
Stable schema/document
Changing user question
```

Bad prompt structure:

```text
Changing timestamp
Changing request ID
Changing user question
Stable schema/document
```

The most important prompt caching rule is:

> Static first. Variable last. Keep the static part exactly the same.

OpenAI mostly handles prompt caching automatically for repeated prefixes.

Claude allows explicit cache markers using `cache_control`.

---

## 8. Strategy 5 — Avoid Sending Full Context Every Time

A common mistake is stuffing too much context into every prompt.

Bad pattern:

```text
Send the entire document set.
Send all database tables.
Send all previous conversation turns.
Send all tool results.
```

Better pattern:

```text
Retrieve only what is relevant.
Rerank the results.
Compress the context.
Send only the useful pieces.
```

For a SQL assistant, instead of sending 300 tables, send:

```text
relevant tables
relevant columns
relationships
business definitions
sample values if needed
```

---

## 9. Strategy 6 — Use RAG Efficiently

RAG should reduce token usage, not increase it.

Bad RAG:

```text
Retrieve top 20 chunks and send all of them.
```

Better RAG:

```text
Retrieve top 20 chunks.
Rerank them.
Keep top 3 to 5.
Compress if needed.
Send only the most relevant context.
```

Better workflow:

```text
User question
→ intent classification
→ retrieve candidate chunks
→ rerank
→ compress
→ answer
```

The goal is to avoid making the model read irrelevant text.

---

## 10. Strategy 7 — Precompute Summaries

If documents, schemas, or business rules are reused often, precompute summaries.

Precompute:

```text
document summary
section summary
table summary
schema summary
business rule summary
column descriptions
FAQ pairs
common examples
```

At runtime, retrieve the smaller summary first.

Example:

```text
Instead of sending a 50-page policy document,
send:
- policy summary
- relevant section
- exact supporting paragraph
```

---

## 11. Strategy 8 — Use Application-Level Caching

Prompt caching is provider-side.

You should also create your own application cache.

Cache things like:

```text
same question + same document version
same SQL generation request
same classification result
same retrieved chunks
same schema summary
same tool output
same embedding result
same final answer
```

Useful cache key components:

```text
hash(system_prompt)
hash(user_question)
document_version
schema_version
model_name
temperature
tool_version
retrieval_version
```

Example:

```text
If the user asks the same refund policy question,
and the policy document version has not changed,
return the cached answer or cached retrieved context.
```

---

## 12. Strategy 9 — Compress Conversation History

Agents become expensive because each turn keeps adding tokens.

Bad pattern:

```text
Send all 50 previous messages every time.
```

Better pattern:

```text
Stable system prompt
Current task state summary
Important facts
Recent 3 to 5 messages
Current user request
```

Good memory structure:

```text
Permanent memory:
Long-term user/project preferences

Working memory:
Current task state

Short-term memory:
Recent messages

Retrieved memory:
Relevant previous details only
```

The key is to preserve meaning without resending everything.

---

## 13. Strategy 10 — Use Code for Deterministic Work

Do not use an LLM for things normal code can do exactly.

Use Python, SQL, or standard logic for:

```text
date calculations
currency formatting
JSON validation
schema validation
regex extraction
sorting
filtering
deduplication
aggregation
unit conversion
SQL execution
file parsing
```

Use LLMs for:

```text
reasoning
ambiguous interpretation
language understanding
planning
summarization
explanation
business-to-technical translation
```

Simple rule:

> If Python or SQL can do it exactly, do not spend LLM tokens on it.

---

## 14. Strategy 11 — Separate Reasoning from Formatting

Do not use an expensive model for simple formatting.

Bad workflow:

```text
Strong model reasons and also formats final JSON.
```

Better workflow:

```text
Strong model performs reasoning.
Code validates and formats output.
Cheap model writes final explanation if needed.
```

Example:

```text
Strong model:
Determine correct business logic.

SQL/Python:
Calculate exact result.

Cheap model:
Explain result in plain English.
```

This is especially useful in analytics, SQL agents, and data engineering agents.

---

## 15. Strategy 12 — Limit Output Tokens

Output tokens can be expensive.

Control the response style.

Examples:

```text
Answer in 5 bullets.
Keep the answer under 200 words.
Return only JSON.
Return only the changed function.
Do not rewrite the whole file.
Return only the final SQL query and 3 explanation bullets.
```

This saves cost and makes the app more predictable.

---

## 16. Strategy 13 — Use Structured Outputs

Structured outputs can reduce retries.

Bad pattern:

```text
Ask model for JSON.
Model returns invalid JSON.
Retry multiple times.
```

Better pattern:

```text
Use schema-based structured output.
Validate the result.
Retry only when validation fails.
```

This is useful for:

```text
classification
extraction
routing
tool arguments
workflow decisions
API payload generation
```

But be careful: very large schemas can increase input tokens unless cached.

---

## 17. Strategy 14 — Reduce Agent Tool-Call Loops

Agents can become expensive because they repeatedly call tools and resend context.

Bad agent pattern:

```text
Search
Read
Search again
Read again
Search again
Summarize
Search again
```

Better agent pattern:

```text
Plan search queries first.
Batch tool calls where possible.
Read only high-value results.
Summarize state after major steps.
Stop when enough evidence exists.
```

Agent cost is often driven more by loops than by model price.

---

## 18. Strategy 15 — Avoid Unnecessary Multi-Agent Systems

Multi-agent systems can become expensive quickly.

Bad pattern:

```text
Planner agent
Research agent
Critic agent
Writer agent
Editor agent
Validator agent
```

Each agent may require another LLM call.

Better pattern:

```text
Use one model call for normal cases.
Add critic or validator only for high-value or risky cases.
```

Use multi-agent architecture only when it improves quality enough to justify the cost.

---

## 19. Strategy 16 — Use Batch Processing for Offline Workloads

Some tasks do not need real-time responses.

Examples:

```text
classifying 100,000 tickets
summarizing old documents
extracting fields from forms
generating embeddings
evaluating model outputs
nightly data quality checks
```

These should use batch or async processing where available.

Use real-time API for user-facing interactions.

Use batch API for background jobs.

---

## 20. Strategy 17 — Use Embeddings Before Generation

Embeddings are usually cheaper than generation models.

Use embeddings to narrow the search space before asking the LLM to reason.

Pattern:

```text
User question
→ embedding search
→ retrieve top candidates
→ rerank
→ send only best context to LLM
```

This prevents the LLM from reading unnecessary documents.

---

## 21. Strategy 18 — Fine-Tune Only for Repeated Patterns

Fine-tuning can reduce prompt size when you repeatedly include examples or formatting rules.

Before fine-tuning:

```text
Send 20 examples every request.
```

After fine-tuning:

```text
Send shorter prompt.
Model already knows the style/pattern.
```

Fine-tuning can help with:

```text
classification
extraction
style consistency
domain-specific formatting
repeated task patterns
```

Fine-tuning is less useful when the app needs fresh knowledge, retrieval, or complex reasoning.

---

## 22. Strategy 19 — Validate Before Escalating

Use cheaper validation methods before calling a strong model.

Example SQL workflow:

```text
Cheap/medium model generates SQL.
SQL parser validates syntax.
Rules engine checks forbidden operations.
If simple and valid, accept.
If risky or complex, strong model reviews.
```

This is better than always using the strongest model.

---

## 23. Strategy 20 — Measure Cost Per Workflow

Do not only compare model price per million tokens.

Measure the entire workflow.

Track:

```text
input tokens
output tokens
cached tokens
reasoning tokens
number of model calls
tool calls
retry count
latency
cache hit rate
success rate
cost per successful task
```

Important question:

```text
How much does it cost to successfully complete one user task?
```

A cheaper model with many retries may cost more than a stronger model that succeeds once.

---

## 24. Recommended Cost-Optimized Architecture

A strong production architecture looks like this:

```text
1. User request
2. Cheap router/classifier
3. Decide workflow
4. Retrieve relevant context only
5. Rerank and compress context
6. Use smallest capable model
7. Use prompt caching for stable context
8. Use deterministic code/tools where possible
9. Validate output
10. Cache result and tool outputs
11. Escalate to stronger model only if needed
```

This is much better than:

```text
Send everything to the strongest model every time.
```

---

## 25. Example Architecture for an Enterprise SQL Agent

```text
User asks business question
→ Cheap model classifies intent
→ Retrieve relevant tables and business definitions
→ Compress schema context
→ Medium model generates SQL
→ SQL parser validates query
→ Security rules check read-only access
→ Execute query
→ Python calculates final metrics if needed
→ Cheap model explains result
→ Strong model reviews only if query is complex/risky
→ Cache final answer and SQL pattern
```

This keeps cost low while preserving quality and safety.

---

## 26. Example Architecture for a RAG Chatbot

```text
User asks question
→ Router identifies domain
→ Embedding search retrieves candidate chunks
→ Reranker selects best chunks
→ Context compressor shortens chunks
→ Medium model answers
→ Citation validator checks support
→ Cache answer by question + document version
```

This avoids sending entire documents to the model.

---

## 27. Example Architecture for a Coding Agent

```text
User asks for code change
→ Router identifies task type
→ Retrieve relevant files only
→ Summarize large files if needed
→ Medium/strong model proposes patch
→ Code formatter/linter runs
→ Tests run
→ Model retries only if tests fail
→ Final response includes changed files only
```

This avoids rewriting the entire codebase and reduces retries.

---

## 28. Common Mistakes

Avoid these:

```text
Using the strongest model for every task
Sending all documents into every prompt
Sending full conversation history forever
Using LLMs for exact calculations
Not using prompt caching
Not caching tool results
Allowing uncontrolled agent loops
Using too many agents
Writing long outputs by default
Retrying without understanding failure reason
Not measuring cost per successful workflow
```

---

## 29. The Simple Rule

The most important token-cost rule is:

> Pay for intelligence only where intelligence is needed.

Everything else should be:

```text
cached
retrieved
compressed
routed
validated
computed with code
or handled by a cheaper model
```

---

## 30. Final Mental Model

A cost-optimized LLM app is not just:

```text
Prompt → Model → Answer
```

It is:

```text
Request
→ classify
→ retrieve
→ compress
→ route
→ generate
→ validate
→ cache
→ respond
```

This is the difference between a demo chatbot and a production-grade LLM application.
