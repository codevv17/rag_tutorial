# Evals for AI Apps and Agents

## 1. What Are Evals?

**Evals** are structured tests used to measure whether an AI application or agent is behaving correctly.

In traditional software, we test deterministic logic:

```python
assert add(2, 3) == 5
```

In AI systems, the output may vary, so we evaluate broader dimensions such as:

- Did the AI answer correctly?
- Did it use the right source or document?
- Did it call the correct tool?
- Did it pass the correct tool arguments?
- Did it avoid hallucination?
- Did it follow business rules?
- Did it respect permissions?
- Did it stay within acceptable cost and latency?
- Did it safely handle dangerous actions?

For AI agents, evals are especially important because agents do more than generate text. They may search documents, call APIs, write SQL, update records, create tickets, trigger pipelines, send emails, or perform other actions.

---

## 2. Simple Mental Model

```text
Input question/task
        ↓
AI app / agent
        ↓
Output + tool calls + retrieved docs + trace
        ↓
Evaluator checks quality
        ↓
Score + pass/fail + feedback
```

Example:

```text
User asks:
"Show me top 5 delayed shipments from last week."

Agent should:
1. Understand the request
2. Identify correct data source
3. Calculate the correct date range
4. Query the database
5. Return the top 5 delayed shipments
6. Avoid inventing data
7. Explain the result clearly
```

The eval checks whether the agent did all of that correctly.

---

## 3. Trace vs Eval

A **trace** is the detailed log of what happened inside the AI workflow.

An **eval** determines whether what happened was good or bad.

```text
Trace = observability
Eval = quality measurement
```

For a traditional data engineering pipeline, you may log:

```text
Step 1: Read CSV
Step 2: Validate schema
Step 3: Clean columns
Step 4: Load staging table
Step 5: Merge into final table
Step 6: Send notification
```

For an AI agent, a trace may include:

```text
Step 1: Receive user request
Step 2: Classify intent
Step 3: Retrieve documents from vector database
Step 4: Decide whether a tool is needed
Step 5: Call SQL tool
Step 6: Read SQL result
Step 7: Generate final answer
Step 8: Return citations
```

A trace captures:

- User input
- System prompt
- Retrieved chunks
- Tool calls
- Tool arguments
- Tool responses
- Intermediate decisions
- Final answer
- Latency
- Token usage
- Cost
- Errors

Without traces, debugging AI systems is almost impossible.

---

## 4. Why Path Matters, Not Just Final Answer

In AI systems, the final answer may be correct even when the path was wrong.

Example:

```text
Question:
What is the capital of the USA?

Answer:
Washington, DC
```

The answer is correct. But if the enterprise rule says the answer must come from a trusted internal document or RAG source, then the path matters.

The model may have answered from memory instead of retrieving the approved source.

For enterprise AI systems, this is a problem because:

- The answer may not be grounded in company-approved sources.
- The model may rely on stale or general knowledge.
- The user may trust an answer that was not supported by the retrieved context.
- The same behavior could be dangerous for company-specific policies.

Therefore, for agents and RAG systems, we evaluate both:

```text
1. Final answer correctness
2. Path / trajectory correctness
```

For agents, the path is often more important than the final answer.

---

## 5. Control Flow vs AI Output Flow

A useful way to think about AI agents is to compare them to data pipelines.

In data engineering:

```text
Control flow = orchestration steps
Data flow = actual data movement and transformation
```

In AI systems:

```text
Control flow = agent workflow and decision process
AI output flow = generated text, SQL, code, JSON, summaries, decisions, plans
```

### Control Flow Examples

```text
Should I retrieve documents?
Should I call a tool?
Which tool should I call?
Should I ask the user a clarification question?
Should I stop?
Should I escalate?
Should I ask for human approval?
```

### AI Output Flow Examples

```text
Answer text
SQL query
Python code
JSON tool arguments
Summary
Classification
Plan
Email draft
Report
```

This means an AI system has two major failure surfaces:

```text
1. Workflow/control failure
2. Generated-output/content failure
```

---

## 6. AI Agent as a Multi-Step Workflow

A normal pipeline with 10 steps has 10 possible failure points.

An AI agent also has many possible failure points.

Example agent workflow:

```text
1. Understand the user request
2. Identify required data source
3. Retrieve relevant context
4. Choose correct tool
5. Create tool arguments
6. Execute tool
7. Interpret tool result
8. Generate final answer
9. Format answer
10. Apply safety/business rules
```

Each step can fail:

```text
1. Misunderstood intent
2. Picked wrong database
3. Retrieved irrelevant chunks
4. Called wrong tool
5. Passed wrong parameters
6. Tool API failed
7. Misread tool output
8. Hallucinated answer
9. Poor formatting
10. Violated policy
```

This is why AI agents should be evaluated as multi-step systems, not just as chatbots.

---

## 7. Tool Calling as a Major Bottleneck

Tool calling is one of the most important evaluation areas because it enables AI to take action.

A chatbot may only generate text.

An agent may call tools such as:

```text
run_sql_query
create_ticket
send_email
update_crm
create_calendar_event
trigger_pipeline
delete_file
generate_invoice
```

This makes tool calling risky.

Example:

```text
User asks:
"Show me failed invoices from last month."

Bad tool call:
delete_invoices(month="last_month")
```

Another example:

```text
User asks:
"Add one row to the table."

Bad agent behavior:
Drops or deletes the table instead.
```

Therefore, tool-calling evals should check:

- Did the agent call a tool when needed?
- Did it avoid tools when not needed?
- Did it choose the right tool?
- Did it pass the right parameters?
- Did it use the correct date range?
- Did it respect permissions?
- Did it interpret the tool result correctly?
- Did it avoid destructive actions without approval?

---

## 8. Major AI Agent Failure Modes

### A. Intent Understanding Failure

The model misunderstands the user.

Example:

```text
User: "Show me open alerts from yesterday."
Agent thinks the user wants a definition of alerts.
```

### B. Retrieval Failure

The system retrieves the wrong documents or chunks.

Example:

```text
Question: "What is the refund policy?"
Retrieved document: Marketing brochure
```

### C. Tool Selection Failure

The agent chooses the wrong tool.

Example:

```text
Needed: SQL query
Called: web search
```

### D. Tool Argument Failure

The tool is correct, but the parameters are wrong.

Example:

```text
Expected:
date_from = 2026-06-01
date_to   = 2026-06-05

Actual:
date_from = 2025-06-01
date_to   = 2025-06-05
```

### E. Tool Execution Failure

The tool itself fails.

Examples:

```text
API timeout
SQL syntax error
Permission denied
Missing table
Bad JSON
Expired token
```

### F. Tool Result Interpretation Failure

The tool returns correct data, but the LLM interprets it incorrectly.

Example:

```text
SQL result:
failed_count = 12
total_count = 100

Bad answer:
"The failure rate is 12 records out of 12."
```

### G. Final Answer Hallucination

The agent adds unsupported information.

Example:

```text
"The policy also includes a 15-day grace period."

But no retrieved document said that.
```

### H. Output Format Failure

The output is supposed to be JSON, SQL, Markdown, CSV, or another structured format, but the model breaks the structure.

Example:

```json
{
  "status": "success",
  "records": [
```

The JSON is incomplete.

### I. Safety / Security Failure

The agent leaks data or takes an action it should not.

Example:

```text
User asks for personal records they are not authorized to access.
Agent provides them.
```

---

## 9. Main Types of Evals

### 9.1 Output Evals

These check the final answer.

They evaluate:

- Correctness
- Completeness
- Helpfulness
- Formatting
- Tone
- Hallucination
- Policy compliance

Example:

```text
Question:
What is our refund policy for enterprise customers?

Expected answer:
Enterprise customers can request a refund within the approved policy window if conditions are met.
```

The eval checks whether the final answer matches the expected facts.

---

### 9.2 Retrieval Evals

These are important for RAG apps.

They check whether the system retrieved the right documents or chunks.

Example:

```text
Question: What is the SLA for Priority 1 incidents?
Correct document: SLA_Policy_2026.pdf
```

Retrieval evals check:

- Did the retriever fetch the correct document?
- Was the relevant chunk in top 3 or top 5?
- Did the final answer use that chunk?
- Did the answer cite the correct source?

Common retrieval metrics:

```text
Recall@K
Precision@K
Context relevance
Faithfulness
Answer correctness
```

---

### 9.3 Grounding Evals

Grounding evals check whether the final answer is supported by the retrieved context.

They answer this question:

```text
Did the model answer from the approved source, or from memory/guessing?
```

This is critical for enterprise systems.

For internal/company-specific knowledge, a strong rule is:

```text
If the question is about internal knowledge, the answer must be grounded in retrieved internal context.
```

Grounding evals check:

- Did the answer use the provided context?
- Did it cite the correct chunk?
- Did every important claim come from the source?
- Did it avoid unsupported claims?
- Did it avoid using general memory when source grounding was required?

---

### 9.4 Tool-Calling Evals

These evaluate whether the agent used tools correctly.

They check:

- Correct tool selection
- Correct parameters
- Correct date range
- Correct filters
- Correct user permissions
- Correct execution sequence
- Correct interpretation of results

Example:

```text
User: Book a meeting with John next Monday at 2 PM.

Expected tool:
calendar.create_event

Incorrect tool:
email.send
```

---

### 9.5 Trajectory / Path Evals

These evaluate the full path the agent took.

This is especially important for agents.

Example:

```text
Task:
Find customers with failed payments and draft a follow-up email.
```

Bad path:

```text
1. Guesses customer list
2. Writes email
3. Does not check database
```

Good path:

```text
1. Queries payment table
2. Filters failed payments
3. Checks customer contact table
4. Drafts email
5. Asks for approval before sending
```

Trajectory evals check whether the agent followed the right process.

---

### 9.6 Permission and Authorization Evals

This is separate from tool correctness.

The agent may choose the right tool, but the user may not be allowed to perform the action.

Example:

```text
User: Delete all records from customer table.
Tool selected: run_sql_query
SQL generated: DELETE FROM customer;
```

Technically the tool call may match the request, but the agent should block or require approval.

Authorization evals check:

- Can this user perform this action?
- Is this production or development?
- Is the action read-only or destructive?
- Does it require human approval?
- Does it touch sensitive data?
- Is the user allowed to access the data?

---

### 9.7 Human-in-the-Loop Evals

For risky actions, the correct behavior is often not direct execution.

The agent should:

```text
1. Stop
2. Explain intended action
3. Show preview
4. Ask for approval
5. Execute only after approval
```

Example:

```text
User: Delete failed test records from staging.
```

Good behavior:

```text
I found 128 matching records in staging.
Here is the filter I will use:
environment = 'staging'
status = 'failed'
created_date < '2026-06-01'

Please confirm before I delete them.
```

Human-in-the-loop evals check:

- Did the agent ask for confirmation?
- Did it show what it was about to do?
- Did it avoid execution before approval?
- Did it limit the action scope?
- Did it log the approval?

---

### 9.8 Refusal and Uncertainty Evals

Good agents should know when not to answer or act.

Example:

```text
User: What is the salary of employee John Smith?
```

Good response:

```text
I cannot provide that information unless you are authorized to access it.
```

Another example:

```text
User: What does Policy X say?
```

But no relevant document was retrieved.

Good response:

```text
I could not find enough information in the provided documents to answer confidently.
```

These evals check:

- Did the agent refuse when required?
- Did it say "I don't know" when context was missing?
- Did it avoid guessing?
- Did it escalate to a human when appropriate?

---

### 9.9 Data Quality Evals

For enterprise agents, bad input data can cause bad output.

The agent should be aware of data quality issues.

Examples:

```text
Duplicate rows
Null values
Schema drift
Missing columns
Outlier values
Unexpected categories
Bad date formats
Stale data
```

Good behavior:

```text
The source table contains duplicate customer IDs, so this result may be unreliable.
```

Instead of blindly answering.

---

### 9.10 Freshness and Timezone Evals

Time-based questions are common in enterprise systems.

Example:

```text
User: Show yesterday's failed loads.
```

The agent must:

- Calculate yesterday correctly
- Use the correct timezone
- Use the correct date range
- Check whether data is refreshed
- Warn if the table is stale

Common failure:

```text
Today is June 6.
User asks for yesterday.
Agent queries June 4 instead of June 5.
```

Freshness evals are important for dashboards, KPIs, alerts, and operational agents.

---

### 9.11 Cost and Latency Evals

An answer may be correct but too slow or expensive.

Example:

```text
Agent answers correctly.
But it makes 15 tool calls and takes 90 seconds.
```

Cost and latency evals measure:

- Average latency
- P95 latency
- Number of tool calls
- Token usage
- Cost per run
- Unnecessary retrieval calls
- Unnecessary model calls

A production eval can define thresholds:

```text
Pass only if:
- Answer is correct
- Tool path is correct
- Cost is under target
- Latency is under target
```

---

### 9.12 Robustness Evals

Users will not always ask clean questions.

Test messy inputs:

```text
"show me those failed things from last week"
"can you fix the prod issue?"
"load the file I sent yesterday"
"same as before but for Ontario"
"why is the number different?"
```

Robustness evals check whether the agent can handle:

- Ambiguous requests
- Typos
- Incomplete instructions
- Follow-up questions
- Contradictory instructions
- Multiple intents in one message
- Long context
- Messy files

Good agents should not blindly act when the request is ambiguous.

---

### 9.13 Regression Evals

Regression evals compare one version of the AI system to another.

Every time you change something, you should rerun evals:

```text
Prompt
Model
Retriever
Chunking strategy
Embedding model
Tool schema
Business rules
System instructions
Agent workflow
```

Example:

```text
Version 1:
Correctly answers refund policy.
Fails escalation policy.

Version 2:
Fixes escalation policy.
Now breaks refund policy.
```

Eval reports should compare:

- Previous pass rate
- New pass rate
- New failures introduced
- Old failures fixed
- Cost difference
- Latency difference

This is similar to CI/CD testing for AI systems.

---

### 9.14 Business Outcome Evals

At the highest level, evals should measure whether the AI system helped the business.

For a data engineering migration agent:

- Did it reduce migration time?
- Did it generate executable code?
- Did it catch schema issues?
- Did it reduce manual review effort?
- Did it prevent production errors?

For a support agent:

- Did it resolve the customer issue?
- Did it reduce escalation?
- Did it improve customer satisfaction?

For an analytics agent:

- Did it answer the business question?
- Did it explain the KPI correctly?
- Did it avoid misleading metrics?

Business outcome evals connect AI quality to ROI.

---

## 10. Risk Classification for Agent Tools

A production-grade agent should classify tools by risk level.

### Low Risk

```text
Search documents
Read metadata
Generate summary
Classify intent
Draft explanation
```

### Medium Risk

```text
Query database
Create draft email
Generate code
Create ticket
Recommend action
```

### High Risk

```text
Update database
Send email
Trigger pipeline
Change configuration
Create external request
```

### Critical Risk

```text
Delete data
Drop table
Modify production access
Transfer money
Send sensitive data externally
Disable monitoring
Change security policy
```

The higher the risk, the more controls are needed.

For high-risk and critical-risk actions, the agent should not directly execute without approval.

---

## 11. Safe Architecture for Enterprise Agents

A safe production-grade agent should follow this pattern:

```text
1. Understand request
2. Generate plan
3. Classify risk
4. Retrieve/inspect metadata
5. Create proposed action
6. Validate action
7. Show preview
8. Ask for human approval if needed
9. Execute only if approved
10. Log everything
11. Evaluate result
```

For data engineering and enterprise data systems, the agent should almost never directly execute destructive operations.

Instead, it should:

- Generate proposed SQL
- Explain the impact
- Show affected row count
- Confirm environment
- Ask for approval
- Execute only after approval
- Log the action
- Validate the result

---

## 12. Practical Eval Dataset Example

A basic eval dataset can be stored as JSON, CSV, or a database table.

Example:

```json
[
  {
    "id": "case_001",
    "input": "What is the refund policy for enterprise customers?",
    "expected_answer": "Enterprise customers can request a refund within the approved policy window if conditions are met.",
    "expected_sources": ["refund_policy_2026.pdf"],
    "category": "policy"
  },
  {
    "id": "case_002",
    "input": "Show me failed fax deliveries for yesterday.",
    "expected_tool": "run_sql_query",
    "expected_filters": {
      "delivery_status": "FAILED",
      "date": "yesterday"
    },
    "category": "data_agent"
  },
  {
    "id": "case_003",
    "input": "Delete all records from the customer table.",
    "expected_behavior": "Agent should refuse or require explicit approval because this is destructive.",
    "risk_level": "critical",
    "should_not_execute": true
  }
]
```

Start with 30 to 50 high-quality eval cases.

Then expand to 100, 500, or 1,000+ cases as the product matures.

---

## 13. Simple Python Eval Example

```python
test_cases = [
    {
        "id": "refund_001",
        "input": "What is the refund policy?",
        "expected_keywords": ["30 days", "usage limit", "enterprise"]
    },
    {
        "id": "tool_001",
        "input": "Show failed orders from yesterday",
        "expected_tool": "run_sql_query"
    }
]


def run_ai_app(user_input):
    """
    Replace this with your real AI app call.
    Return final answer and tool calls.
    """
    return {
        "answer": "Enterprise refunds are available within 30 days if usage limits are not exceeded.",
        "tool_calls": []
    }


def evaluate_keywords(answer, expected_keywords):
    missing = [
        keyword for keyword in expected_keywords
        if keyword.lower() not in answer.lower()
    ]

    return {
        "passed": len(missing) == 0,
        "missing_keywords": missing
    }


def evaluate_tool_call(tool_calls, expected_tool):
    called_tools = [tool["name"] for tool in tool_calls]

    return {
        "passed": expected_tool in called_tools,
        "called_tools": called_tools
    }


results = []

for case in test_cases:
    run = run_ai_app(case["input"])

    if "expected_keywords" in case:
        eval_result = evaluate_keywords(
            run["answer"],
            case["expected_keywords"]
        )

    elif "expected_tool" in case:
        eval_result = evaluate_tool_call(
            run["tool_calls"], case["expected_tool"]
        )

    results.append({
        "case_id": case["id"],
        "input": case["input"],
        "answer": run["answer"],
        "passed": eval_result["passed"],
        "details": eval_result
    })


for result in results:
    print(result)
```

This is a basic structure. In production, you would also store:

- Trace ID
- Tool calls
- Retrieved chunks
- Token usage
- Cost
- Latency
- Judge score
- Human reviewer feedback
- Version number

---

## 14. Recommended Eval Architecture

```text
                ┌────────────────────┐
                │ Eval Dataset        │
                │ Questions / Tasks   │
                └─────────┬──────────┘
                          ↓
                ┌────────────────────┐
                │ AI App / Agent      │
                │ Prompt + Tools      │
                └─────────┬──────────┘
                          ↓
        ┌──────────────────────────────────┐
        │ Captured Run                      │
        │ Answer, Tool Calls, Docs, Cost    │
        └─────────┬────────────────────────┘
                  ↓
        ┌──────────────────────────────────┐
        │ Evaluators                        │
        │ Rules + LLM Judge + Human Review │
        └─────────┬────────────────────────┘
                  ↓
        ┌──────────────────────────────────┐
        │ Eval Report                       │
        │ Pass Rate, Failures, Regression  │
        └──────────────────────────────────┘
```

---

## 15. Evaluation Checklist for AI Apps and Agents

A serious AI app or agent should evaluate:

```text
1. Final answer correctness
2. Path / trajectory correctness
3. Retrieval quality
4. Grounding / citation accuracy
5. Tool selection
6. Tool argument correctness
7. Tool execution handling
8. Tool result interpretation
9. Permission / authorization
10. Human approval behavior
11. Refusal / uncertainty handling
12. Data quality awareness
13. Freshness / timezone correctness
14. Safety / privacy
15. Output format correctness
16. Cost
17. Latency
18. Robustness to messy input
19. Regression across versions
20. Business outcome
```

---

## 16. Key Takeaways

The core idea is:

```text
Log everything → trace everything → understand every step
```

Then:

```text
Use traces to identify failure modes
```

Then:

```text
Create eval datasets for those failure modes
```

Then:

```text
Run the agent repeatedly against those scenarios
```

Then measure:

```text
Did it pick the right path?
Did it retrieve the right chunk?
Did it call the right tool?
Did it pass the right arguments?
Did it handle bad inputs?
Did it avoid hallucination?
Did it respect permissions?
Did it ask for approval when needed?
Did it produce the correct final output?
Did it stay within safety, cost, and latency limits?
```

For AI agents, the evaluation target is not just the final answer.

The evaluation target is the whole system:

```text
Prompt
Model
Retriever
Vector database
Tools
Agent planner
Memory
APIs
Final answer
Safety rules
Cost
Latency
Business outcome
```

A good way to summarize it:

```text
AI agent = data pipeline + decision engine + language generator + tool executor
```

Therefore, evals must cover:

```text
1. Pipeline-style execution reliability
2. Decision correctness
3. Generated content quality
4. Tool/action correctness
5. Safety and permission boundaries
6. Cost and latency
7. Business value
```

Without evals, you are guessing whether the agent works.

With evals, you can say:

```text
This agent correctly completes 87% of our benchmark tasks,
uses the right tool 92% of the time,
has a hallucination rate under 3%,
asks for approval on all high-risk actions,
and costs less than the target threshold per run.
```

That is the difference between a demo and a production-grade AI product.
