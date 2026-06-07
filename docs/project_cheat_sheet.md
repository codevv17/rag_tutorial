# Project Cheat Sheet

## 1. Purpose

- This project demonstrates a simple RAG flow for answering questions about growing vegetables in Florida.
- It prepares PDF chunks in `fill_db.py`, then retrieves existing ChromaDB chunks and sends them to OpenAI in `ask.py`.

## 2. Current RAG Flow

### Step 1: Load documents

- File: `fill_db.py`
- Object/function: `PyPDFDirectoryLoader(DATA_PATH)` and `loader.load()`
- Input: PDF files in `data/`; currently `data/VH021.pdf`
- Output: `raw_documents`
- What it does: Loads PDF pages as LangChain document objects.

### Step 2: Split documents

- File: `fill_db.py`
- Object/function: `RecursiveCharacterTextSplitter` and `split_documents()`
- Chunk size: `300` characters
- Chunk overlap: `100` characters
- Output: `chunks`
- What it does: Creates smaller overlapping document pieces.

### Step 3: Prepare vector DB records

- File: `fill_db.py`
- Prepared values:
  - `documents`: chunk text
  - `metadata`: source and page details
  - `ids`: sequential IDs such as `ID0`
- Current behavior: Prints the prepared values.
- Important: `PersistentClient`, collection creation, and `collection.upsert()` are commented out, so `fill_db.py` does not currently store chunks.

### Step 4: Retrieve context

- File: `ask.py`
- DB/client: `chromadb.PersistentClient(path="chroma_db")`
- Collection: `growing_vegetables`
- Query source: Terminal input stored in `user_query`
- Retrieval method: `collection.query(query_texts=[user_query], n_results=4)`
- Embedding: No custom embedding model is configured; ChromaDB handles query embedding with its collection embedding function.
- Output: The four retrieved document chunks in `results['documents']`

### Step 5: Generate answer

- File: `ask.py`
- Client/model: `OpenAI()` with `gpt-4o`
- Prompt: `system_prompt` tells the model to answer only from retrieved documents and say `I don't know` when needed.
- Context: `str(results['documents'])`
- Output: `response.choices[0].message.content` printed to the terminal.

## 3. Key Files

- `fill_db.py`: Loads PDFs, splits text, prepares ChromaDB records, and prints them.
- `ask.py`: Retrieves ChromaDB context and generates an OpenAI answer.
- `data/VH021.pdf`: Current source PDF.
- `chroma_db/`: Existing persistent ChromaDB files.
- `.env`: Provides `OPENAI_API_KEY` for `ask.py`.
- `pyproject.toml`: Defines Python `>=3.13` and project dependencies.
- `main.py`: Placeholder greeting script; not part of the RAG flow.

## 4. How to Run

Install dependencies:

```bash
uv sync
```

Inspect PDF loading and chunk preparation:

```bash
uv run python fill_db.py
```

Ask a question using the existing ChromaDB collection:

```bash
uv run python ask.py
```

- Required: `data/`, `chroma_db/`, and `.env` containing `OPENAI_API_KEY`.
- Expected output from `fill_db.py`: Raw documents, chunks, metadata, IDs, and text.
- Expected output from `ask.py`: Retrieved chunks followed by the generated answer.

## 5. Notes to Remember

- `fill_db.py` currently prepares data but does not write it to ChromaDB.
- `ask.py` expects the `growing_vegetables` collection to already contain chunks.
- RAG retrieves relevant context before asking the LLM to generate an answer.
- Chunk overlap helps keep context across neighboring chunks.
- ChromaDB uses `chroma_db/` for persistent local storage.
