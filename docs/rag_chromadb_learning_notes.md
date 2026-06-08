# RAG + ChromaDB Learning Notes

## 1. Basic RAG Flow

A simple RAG pipeline works like this:

```text
Documents
↓
Document Loader
↓
Raw LangChain Documents
↓
Text Splitter
↓
Chunks
↓
Embeddings
↓
ChromaDB Collection
↓
Retrieve relevant chunks
↓
Send chunks + user question to LLM
↓
Final answer
```

In your current project:

```text
PDF files in data/
↓
PyPDFDirectoryLoader
↓
RecursiveCharacterTextSplitter
↓
Chunks
↓
ChromaDB
↓
Query top chunks
↓
Use retrieved chunks as context for the LLM
```

---

## 2. ChromaDB Mental Model

ChromaDB is a vector database used to store and search text chunks by meaning.

Relational database comparison:

```text
Chroma PersistentClient  ≈ database connection + local database folder
chroma_db/               ≈ database storage location
Collection               ≈ table
Chunk                    ≈ row
id                       ≈ primary key
document/page_content    ≈ text column
metadata                 ≈ JSON-like extra columns
embedding                ≈ vector representation of the text
```

Example:

```python
chroma_client = chromadb.PersistentClient(path="chroma_db")
collection = chroma_client.get_or_create_collection(name="growing_vegetables")
```

Meaning:

```text
Open/create a local Chroma database folder called chroma_db.
Create/get a collection called growing_vegetables.
```

---

## 3. What Chroma Stores

Each record in a Chroma collection usually has:

```text
id          → unique identifier
document    → chunk text
metadata    → source/page/file info
embedding   → numerical meaning vector
```

Example:

```python
collection.upsert(
    ids=["VH021_page_2_chunk_0"],
    documents=["Composting improves soil fertility."],
    metadatas=[{"source": "VH021.pdf", "page": 2}]
)
```

Use `upsert()` when you want to insert or update records.

```text
add()     → insert only
upsert()  → insert if new, update if ID already exists
```

---

## 4. What Is a Collection?

A collection is a table-like container for related chunks and embeddings.

```text
ChromaDB database
└── Collection: growing_vegetables
    ├── Chunk 1
    ├── Chunk 2
    ├── Chunk 3
    └── Chunk 4
```

Use different collections for different knowledge areas if needed.

Example:

```text
growing_vegetables
company_policies
confluence_docs
project_notes
```

---

## 5. Embeddings

An embedding is a numerical vector that represents the meaning of text.

With your current setup, Chroma returned embeddings with shape:

```text
4 x 384
```

Meaning:

```text
4 chunks returned
384 numbers per chunk
```

Important rule:

```text
Embedding dimension is fixed by the model, not by the input length.
```

So:

```text
1 word       → 1 x 384
1 sentence   → 1 x 384
1 paragraph  → 1 x 384
1 chunk      → 1 x 384
```

But the text must be within the model's maximum input limit. If the text is too long, it may be truncated or fail.

---

## 6. Tokens

A token is a small piece of text used by the model.

A token can be:

```text
a full word
part of a word
punctuation
a number
a symbol
space + word
```

Example:

```text
Text:
Composting improves soil.

Possible tokens:
["Com", "post", "ing", " improves", " soil", "."]
```

Pipeline:

```text
Raw text
↓
Tokens
↓
Token IDs
↓
Model processing
↓
Final embedding vector
```

Simple distinction:

```text
Token      = piece of text
Token ID   = number assigned to that token
Embedding  = meaning vector created by the model
```

---

## 7. Query Results in Chroma

When you query Chroma:

```python
results = collection.query(
    query_texts=[user_query],
    n_results=4,
    include=["documents", "metadatas", "embeddings", "distances"]
)
```

The result is nested:

```text
results["documents"][0]     → chunks for the first query
results["documents"][0][0]  → first returned chunk
results["documents"][0][1]  → second returned chunk
```

Why nested?

```text
Outer list = each user query
Inner list = chunks returned for that query
```

Distances:

```text
Lower distance = stronger match
Higher distance = weaker match
```

---

## 8. Document Loaders

A document loader reads data from a source and converts it into LangChain `Document` objects.

A LangChain `Document` usually has:

```text
page_content  → actual text
metadata      → source, page number, file name, URL, etc.
```

Common loaders:

```text
PyPDFDirectoryLoader  → many PDFs from a folder
PyPDFLoader           → one PDF
TextLoader            → .txt or .md files
CSVLoader             → CSV files
Docx2txtLoader        → Word documents
WebBaseLoader         → web pages
DirectoryLoader       → files from a folder
JSONLoader            → JSON files
ConfluenceLoader      → Confluence pages
```

Current example:

```python
from langchain_community.document_loaders import PyPDFDirectoryLoader

loader = PyPDFDirectoryLoader("data")
raw_documents = loader.load()
```

---

## 9. Loading Confluence

Use `ConfluenceLoader` for Confluence pages.

Install:

```bash
pip install langchain-community atlassian-python-api
```

`.env` example:

```env
CONFLUENCE_URL=https://yourcompany.atlassian.net/wiki
CONFLUENCE_USERNAME=your.email@company.com
CONFLUENCE_API_TOKEN=your_api_token_here
```

Python example:

```python
import os
from dotenv import load_dotenv
from langchain_community.document_loaders import ConfluenceLoader

load_dotenv()

loader = ConfluenceLoader(
    url=os.getenv("CONFLUENCE_URL"),
    username=os.getenv("CONFLUENCE_USERNAME"),
    api_key=os.getenv("CONFLUENCE_API_TOKEN"),
    cloud=True
)

documents = loader.load(
    space_key="SPACEKEY",
    include_attachments=False,
    limit=50
)
```

Start with one page or small limit first, then expand.

---

## 10. Text Splitters

A splitter breaks large documents into smaller chunks before embeddings are created.

Common splitters:

```text
RecursiveCharacterTextSplitter  → best default for normal documents
CharacterTextSplitter           → simple character/paragraph splitting
TokenTextSplitter               → token-based splitting
MarkdownHeaderTextSplitter      → markdown docs
HTMLHeaderTextSplitter          → HTML/web pages
RecursiveJsonSplitter           → JSON data
Code-aware splitters            → code files
```

Best default for your project:

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100,
    length_function=len,
    is_separator_regex=False,
)
```

---

## 11. Chunking Strategies

Chunking strategy means how you break documents into smaller pieces.

### Fixed-size chunking

```text
Split text into chunks of a fixed size.
Example: 500 characters with 100 overlap.
```

### Overlap chunking

```text
Repeat part of the previous chunk in the next chunk.
This prevents losing context at chunk boundaries.
```

### Recursive chunking

```text
Try to split by paragraph, then sentence, then word, then character.
Best default for PDFs and general text.
```

### Token-based chunking

```text
Split by tokens instead of characters.
Better when working with strict model token limits.
```

### Semantic chunking

```text
Split by meaning/topic instead of size.
More advanced, but can improve retrieval quality.
```

### Structure-aware chunking

```text
Split by headings, sections, HTML tags, markdown headers, code functions, etc.
Very useful for documentation and Confluence pages.
```

### Parent-child chunking

```text
Search using small child chunks.
Return larger parent context to the LLM.
```

Useful because:

```text
Small chunks = better search precision
Large parent chunks = better answer context
```

### Q&A chunking

```text
Each question-answer pair becomes one chunk.
Useful for FAQs and support docs.
```

Rule of thumb:

```text
Small chunks  → better precise matching, less context
Large chunks  → more context, weaker precision
Overlap       → reduces boundary loss, increases storage
```

Recommended starting point:

```text
chunk_size=500
chunk_overlap=100
```

---

## 12. Types of RAG

### 1. Basic Vector RAG

```text
Documents → chunks → embeddings → vector DB → retrieve similar chunks → LLM answer
```

This is what you are currently building with ChromaDB.

### 2. Vectorless RAG

RAG without embeddings/vector search.

Uses:

```text
keyword search
full-text search
SQL filters
BM25
metadata search
exact phrase matching
```

Good for:

```text
error codes
policy names
ticket IDs
product SKUs
API fields
SQL column names
```

### 3. Keyword / Full-text RAG

Uses search engines or database full-text search.

Good for exact matches, logs, tickets, code, policies, and names.

### 4. Hybrid RAG

Combines:

```text
vector search + keyword/full-text search
```

This is strong for real enterprise use because it captures both meaning and exact terms.

### 5. RAG with Reranking

Flow:

```text
Retrieve many chunks
↓
Reranker scores them more carefully
↓
Keep best chunks
↓
Send to LLM
```

Useful when initial retrieval returns noisy results.

### 6. Parent-Child RAG

```text
Small child chunks used for retrieval
Large parent chunks sent to the LLM
```

Great for manuals, policies, Confluence pages, and technical docs.

### 7. Graph RAG

Uses relationships between entities.

Example:

```text
Project → uses → System
System → depends on → Database
Policy → applies to → Department
```

Good for enterprise architecture, lineage, dependencies, and connected knowledge.

### 8. SQL / Structured Data RAG

Used when the data is in tables.

Flow:

```text
User question
↓
LLM generates SQL
↓
Database returns result
↓
LLM explains result
```

Best for counts, filters, joins, aggregations, KPIs, and metrics.

### 9. Agentic RAG

The LLM decides which retrieval tool to use.

Example tools:

```text
Vector DB
SQL database
web search
APIs
file search
metadata filters
```

Flow:

```text
Understand question
↓
Choose tool
↓
Retrieve data
↓
Maybe retrieve again
↓
Answer
```

### 10. Multi-hop RAG

Retrieves multiple pieces of evidence step by step.

Useful when one chunk is not enough to answer the question.

### 11. Corrective / Self-reflective RAG

The system checks if retrieved chunks are useful.

If weak:

```text
rewrite query
retrieve again
then answer
```

### 12. Multi-modal RAG

Retrieves from more than text:

```text
images
charts
tables
PDF diagrams
audio transcripts
videos
screenshots
```

---

## 13. Recommended Learning Path

For your current RAG learning journey:

```text
1. Basic Vector RAG
2. Metadata filtering
3. Better chunking
4. Hybrid RAG
5. Reranking
6. Parent-child RAG
7. SQL / structured RAG
8. Agentic RAG
9. Graph RAG
```

For serious enterprise RAG, a strong pattern is:

```text
Hybrid RAG + metadata filters + reranking + citations
```

---

## 14. Final Simple Mental Model

```text
Loader      → brings data into the pipeline
Splitter    → breaks data into chunks
Embedding   → converts chunks into vectors
ChromaDB    → stores and searches chunks by meaning
Retriever   → finds relevant chunks
LLM         → answers using retrieved context
```

Your current project is a great baseline:

```text
PDF → Loader → Splitter → ChromaDB → Query → Top chunks → LLM answer
```

Next practical improvements:

```text
1. Use stable IDs for chunks
2. Store useful metadata
3. Print retrieved chunks and inspect quality
4. Add LLM answer generation
5. Add citations from metadata
6. Experiment with chunk_size and chunk_overlap
7. Later add reranking or hybrid search
```
