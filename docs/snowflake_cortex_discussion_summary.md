# Snowflake Cortex Discussion Summary

## 1. Big Picture Mental Model

Snowflake is positioning Cortex as a **business intelligence and enterprise data AI layer**, not as a fully customizable vector database platform.

The clean mental model is:

```text
Snowflake data platform
    + Cortex Analyst for structured data / SQL questions
    + Cortex Search for semantic and hybrid search over text
    + Cortex Agents for orchestrating Analyst, Search, and LLM responses
    + Semantic Views for governed business meaning
```

Snowflake is trying to help business users ask questions over enterprise data without forcing every company to build its own custom RAG stack, vector database, text-to-SQL pipeline, and agent orchestration framework.

---

## 2. Snowflake Sample Data and Trial Setup

For trial learning, Snowflake provides the shared sample database:

```sql
SNOWFLAKE_SAMPLE_DATA
```

Useful schemas include:

```text
TPCH_SF1
TPCH_SF10
TPCH_SF100
TPCH_SF1000
TPCDS_SF10TCL
TPCDS_SF100TCL
```

Important point:

```text
SNOWFLAKE_SAMPLE_DATA is read-only.
```

You can query it, but you cannot create agents, semantic views, search services, tables, or other custom objects inside it.

Correct pattern:

```text
SNOWFLAKE_SAMPLE_DATA.TPCH_SF1000
    = read-only source data

AI_DEMO_DB.AGENTS_SCHEMA
    = your writable workspace for agents, semantic views, search services, and demos
```

Example:

```sql
USE ROLE ACCOUNTADMIN;

CREATE DATABASE IF NOT EXISTS AI_DEMO_DB;
CREATE SCHEMA IF NOT EXISTS AI_DEMO_DB.AGENTS_SCHEMA;

USE DATABASE AI_DEMO_DB;
USE SCHEMA AGENTS_SCHEMA;
```

Then reference TPCH tables using fully qualified names:

```sql
SELECT COUNT(*)
FROM SNOWFLAKE_SAMPLE_DATA.TPCH_SF1000.ORDERS;
```

---

## 3. Cortex Analyst

Cortex Analyst is for **natural language questions over structured Snowflake tables**.

Simple definition:

```text
Cortex Analyst = natural language → SQL → answer from structured data
```

Example questions:

```text
What is total revenue by customer segment?
Which nation has the most suppliers?
Show order value by region and year.
Which customers have the highest order volume?
```

For TPCH-style schemas, Cortex Analyst is usually the right first tool because TPCH is structured relational data.

Cortex Analyst needs business context so it does not guess incorrectly. That is where a semantic model or semantic view becomes important.

Without semantic context, an AI system may guess:

```text
Revenue = O_TOTALPRICE
```

But your business may define it as:

```text
Revenue = SUM(L_EXTENDEDPRICE * (1 - L_DISCOUNT))
```

Cortex Analyst is designed to use a governed semantic layer so it can generate better SQL and business-correct answers.

---

## 4. Cortex Search

Cortex Search is for **semantic / fuzzy / hybrid search over text data stored in Snowflake**.

Simple definition:

```text
Cortex Search = managed enterprise search over text columns/chunks in Snowflake
```

Good use cases:

```text
Support tickets
Policy documents
Contracts
Product descriptions
Call transcripts
Emails
Knowledge-base articles
PDF text chunks
```

Cortex Search is commonly used as the retrieval layer in RAG applications:

```text
User question
    ↓
Cortex Search retrieves relevant chunks
    ↓
LLM receives those chunks as context
    ↓
LLM generates grounded answer
```

Important distinction:

```text
Cortex Search itself is the retrieval/search layer.
It does not automatically become a full chatbot unless you connect it to an LLM, Cortex Agent, Streamlit app, REST app, or another workflow.
```

---

## 5. Is Snowflake a Vector Database?

The practical answer:

```text
Snowflake is not primarily a dedicated vector database.
Snowflake is a data platform that now includes vector and search capabilities.
```

Snowflake supports:

```text
Native VECTOR data type
Embedding functions
Vector similarity functions
Managed Cortex Search
Cortex Analyst
Cortex Agents
```

But Cortex Search does not expose the same low-level vector-index tuning knobs as dedicated vector databases such as Pinecone, Weaviate, Milvus, or Chroma.

Snowflake hides many details under the hood, such as:

```text
embedding/index management
hybrid ranking
search serving infrastructure
index refresh
some ranking/search quality tuning
```

A dedicated vector database may expose more control over:

```text
HNSW parameters
IVF/PQ indexing
custom distance metrics
ef_search / ef_construction
advanced reranking pipelines
custom chunk-routing strategies
multiple retrievers
low-level vector index layout
```

Best mental model:

```text
Snowflake Cortex Search is a managed enterprise search layer,
not a low-level vector database engineering playground.
```

---

## 6. Chunking Strategy in Cortex Search

In Cortex Search, the rows returned by the service query are the searchable units.

Example:

```sql
CREATE OR REPLACE CORTEX SEARCH SERVICE SUPPORT_TICKET_SEARCH
  ON ISSUE_TEXT
  ATTRIBUTES TICKET_ID, CUSTOMER_NAME, PRODUCT, PRIORITY
  WAREHOUSE = AI_DEMO_WH
  TARGET_LAG = '1 hour'
  AS
    SELECT
      TICKET_ID,
      CUSTOMER_NAME,
      PRODUCT,
      PRIORITY,
      ISSUE_TEXT
    FROM SUPPORT_TICKETS;
```

In this case:

```text
Each row's ISSUE_TEXT = one searchable chunk/unit
```

For support tickets, one row per ticket may be fine.

For long documents, such as policies, contracts, PDFs, or manuals, one full document per row is usually not ideal. You should chunk the document first.

Recommended design:

```sql
CREATE OR REPLACE TABLE POLICY_CHUNKS (
    DOC_ID STRING,
    DOC_TITLE STRING,
    POLICY_CATEGORY STRING,
    VERSION STRING,
    EFFECTIVE_DATE DATE,
    PAGE_NUMBER NUMBER,
    SECTION_HEADING STRING,
    CHUNK_ID NUMBER,
    CHUNK_TEXT STRING,
    SOURCE_FILE STRING,
    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);
```

Then create Cortex Search on `CHUNK_TEXT`:

```sql
CREATE OR REPLACE CORTEX SEARCH SERVICE POLICY_SEARCH_SERVICE
  ON CHUNK_TEXT
  ATTRIBUTES DOC_ID, DOC_TITLE, POLICY_CATEGORY, VERSION, EFFECTIVE_DATE, PAGE_NUMBER, SECTION_HEADING
  WAREHOUSE = AI_DEMO_WH
  TARGET_LAG = '1 hour'
  AS
    SELECT
      DOC_ID,
      DOC_TITLE,
      POLICY_CATEGORY,
      VERSION,
      EFFECTIVE_DATE,
      PAGE_NUMBER,
      SECTION_HEADING,
      CHUNK_ID,
      CHUNK_TEXT
    FROM POLICY_CHUNKS;
```

---

## 7. Ingesting a Policy Document into Snowflake

The recommended RAG pattern is:

```text
Policy PDF/DOCX
   ↓
Upload to Snowflake stage
   ↓
Extract text
   ↓
Split into chunks
   ↓
Store chunks in a Snowflake table
   ↓
Create Cortex Search service on chunk_text
   ↓
Use search results in RAG / Cortex Agent / app
```

There are two good approaches.

### Option A: Snowflake-native approach

Use Snowflake features:

```text
Stage document
AI_PARSE_DOCUMENT / PARSE_DOCUMENT
SPLIT_TEXT_RECURSIVE_CHARACTER
Chunk table
Cortex Search
```

This is good when you want everything governed and stored inside Snowflake.

### Option B: External preprocessing approach

Use LangChain, LlamaIndex, Python, or custom code outside Snowflake:

```text
Extract text externally
Use custom chunking logic
Preserve section headings/page numbers/metadata
Insert chunks into Snowflake table
Create Cortex Search on the table
```

This is useful when you need more control over:

```text
section-aware chunking
page-aware chunking
custom metadata extraction
OCR workflows
specialized chunk sizes by document type
policy-specific parsing rules
```

Best answer:

```text
Yes, create chunks first, insert each chunk as one row in Snowflake, then create Cortex Search on that chunk table.
```

---

## 8. Cortex Agents

Cortex Agents are for orchestration.

Simple definition:

```text
Cortex Agent = planner/orchestrator that can use tools such as Cortex Analyst and Cortex Search
```

Example:

```text
Question:
Why did revenue drop in the Northeast region?

Agent may:
1. Use Cortex Analyst to query revenue by region from structured tables.
2. Use Cortex Search to search support tickets or complaint notes.
3. Combine both results.
4. Return a business explanation.
```

This makes the agent useful when a question requires both:

```text
structured data analysis
+
unstructured text/document retrieval
```

Cortex Agents are not just text-to-SQL. They are designed to coordinate multiple tools and produce a final answer.

---

## 9. Cortex Analyst vs Cortex Search vs Cortex Agent

| Capability | Primary Purpose | Best For |
|---|---|---|
| Cortex Analyst | Natural language to SQL | Structured tables, metrics, BI questions |
| Cortex Search | Semantic/hybrid search | Documents, tickets, policies, text chunks |
| Cortex Agent | Tool orchestration | Multi-step questions using structured + unstructured data |
| Semantic View | Governed business model | Metrics, dimensions, relationships, business meaning |

Simple mental model:

```text
Cortex Analyst = data analyst who writes SQL
Cortex Search = search engine over enterprise text
Cortex Agent = manager that decides which specialist/tool to use
Semantic View = governed business dictionary + join/metric layer
```

---

## 10. Semantic Views

A Semantic View is Snowflake's business-friendly semantic layer over raw tables.

It defines:

```text
logical tables
relationships/joins
dimensions
facts
metrics
synonyms
comments/business meaning
```

This is very similar to the manual workflow of giving an AI coding agent:

```text
DDL
data dictionary
high-level table list
business meaning
join guidance
metric definitions
```

Your Codex workflow:

```text
Feed agent DDL + data dictionary + table list
    ↓
Agent picks relevant tables
    ↓
Agent understands joins
    ↓
Agent writes SQL
```

Snowflake formalizes this as:

```text
Physical tables
    ↓
Semantic View
    ↓
Cortex Analyst generates SQL using governed business context
```

The main difference:

```text
Your Codex approach = prompt-based semantic context
Snowflake Semantic View = database-native semantic context
```

Semantic Views help prevent the AI from guessing business logic incorrectly.

Example ambiguity:

```text
What is revenue?
```

Possible definitions:

```text
O_TOTALPRICE
L_EXTENDEDPRICE
L_EXTENDEDPRICE * (1 - L_DISCOUNT)
L_EXTENDEDPRICE * (1 - L_DISCOUNT) * (1 + L_TAX)
```

A Semantic View lets the organization define the official version.

---

## 11. Cortex Pricing Mental Model

Snowflake Cortex pricing is generally expressed in Snowflake credits.

For many Cortex AI functions, the cost is driven by tokens processed:

```text
Cortex cost = tokens processed × credit rate
```

For LLM-style functions, cost may consider:

```text
input tokens
output tokens
model/function used
warehouse cost for surrounding SQL
```

Important distinction:

```text
Warehouse compute may still apply for scanning/filtering/joining data.
Cortex AI service cost applies for model/search/LLM processing.
```

Cortex Analyst and other higher-level products may have their own pricing model, so always check the current Snowflake consumption table and usage views.

Useful usage views include Cortex-specific account usage history views, depending on the feature used.

---

## 12. Why Snowflake's Approach Makes Sense

Snowflake is not trying to give every user full control over vector database internals.

It is trying to provide:

```text
governed enterprise AI
BI-friendly natural-language analytics
managed semantic search
secure data access
less infrastructure management
less custom RAG engineering
```

That is why Snowflake hides many low-level retrieval details and emphasizes:

```text
semantic views
Cortex Analyst
Cortex Search
Cortex Agents
Snowflake governance/RBAC
enterprise data inside Snowflake
```

This is a strong pattern for business intelligence because most business users do not want to manage vector indexes, chunking algorithms, or embedding pipelines. They want reliable answers from governed enterprise data.

---

## 13. Service Opportunity for Neso Data

This discussion points to a strong consulting/service opportunity:

```text
AI-ready semantic layer and governed natural-language analytics for enterprise data platforms
```

Better business positioning:

```text
We make your enterprise data ready for Copilot, Cortex, Genie, and AI agents.
```

Possible packaged service names:

```text
Agent-Ready Analytics Modernization
AI-Ready Semantic Layer Implementation
Copilot-Ready Data Platform Assessment
Snowflake Cortex Analyst & Agent Readiness
Databricks Genie & Unity Catalog Semantic Layer Implementation
Fabric Copilot Readiness Assessment
```

Target platforms:

```text
Snowflake
Microsoft Fabric
Power BI
Azure Synapse
Databricks
```

The product features exist in these platforms, but companies still need help with:

```text
cleaning up business definitions
creating governed metrics
mapping joins
building semantic models
validating AI-generated SQL
creating prompt/AI instructions
setting up security/RLS/RBAC
curating test questions
monitoring answer quality
rolling out to business users
```

This is where a service company can create value.

---

## 14. Equivalent Concepts in Other Platforms

### Snowflake

```text
Semantic Views
Cortex Analyst
Cortex Search
Cortex Agents
```

### Microsoft Fabric / Power BI

```text
Power BI Semantic Models
Copilot over semantic models
Fabric Data Agents
AI Instructions
Verified Answers
Prep data for AI
```

### Databricks

```text
Unity Catalog
Metric Views
AI/BI Genie Spaces
trusted assets
business semantics
example queries and instructions
```

### Azure Synapse

Classic Synapse does not have the same modern built-in agent/semantic AI layer. For Synapse clients, the opportunity is to modernize their analytics layer toward:

```text
Power BI Semantic Models
Microsoft Fabric
Azure AI Foundry agents
Databricks/Snowflake-style governed semantic layers
```

---

## 15. Recommended Learning Path

For your Snowflake trial, the recommended sequence is:

```text
1. Query TPCH_SF1000 with normal SQL.
2. Create your own AI_DEMO_DB workspace.
3. Build a Semantic View over a small TPCH subset.
4. Try Cortex Analyst for natural-language SQL questions.
5. Create a small support ticket table.
6. Create Cortex Search on the ticket text column.
7. Upload/chunk a policy document and create Cortex Search on chunks.
8. Create a Cortex Agent that uses both Analyst and Search.
9. Use this as a demo for your service offering.
```

---

## 16. Final Mental Model

The full architecture looks like this:

```text
Structured enterprise tables
    ↓
Semantic View
    ↓
Cortex Analyst
    ↓
SQL-based business answers

Unstructured/text data
    ↓
Chunk table
    ↓
Cortex Search
    ↓
Relevant retrieved context

Cortex Agent
    ↓
Uses Analyst + Search + LLM reasoning
    ↓
Final business answer
```

The key insight:

```text
Snowflake has productized the same pattern that data engineers and AI engineers were manually building:
DDL + data dictionary + joins + metrics + embeddings + retrieval + LLM orchestration.
```

But Snowflake has packaged it in a governed, SQL-native, enterprise-friendly way.

---

## References

- Snowflake Cortex Analyst: https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst
- Snowflake Cortex Agents: https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents
- Snowflake Cortex Search overview: https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-search/cortex-search-overview
- CREATE CORTEX SEARCH SERVICE: https://docs.snowflake.com/en/sql-reference/sql/create-cortex-search
- Snowflake Semantic Views overview: https://docs.snowflake.com/en/user-guide/views-semantic/overview
- CREATE SEMANTIC VIEW: https://docs.snowflake.com/en/sql-reference/sql/create-semantic-view
- Snowflake Cortex AI SQL functions: https://docs.snowflake.com/en/user-guide/snowflake-cortex/aisql
