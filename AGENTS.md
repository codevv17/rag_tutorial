# AGENTS.md

## Goal
Keep a short learning-focused RAG cheat sheet that explains what the code does, step by step.

The cheat sheet should help me remember the project months later without reading every file again.

## Main output
Create or update:

```text
docs/project_cheat_sheet.md
```

Keep it brief. Do not write long explanations.

## How to work
When asked to document the repo:

1. Scan the codebase.
2. Identify the main RAG flow.
3. Update `docs/project_cheat_sheet.md` based on the current code.
4. Remove outdated steps if the code changed.
5. Keep examples small and useful.

## RAG steps to look for
Document these only if they exist in the codebase:

1. **Environment / paths**
   - Data folder
   - Vector DB path
   - API keys or config files

2. **Document loading**
   - Loader used
   - Input file/folder
   - Output variable, usually raw documents

3. **Text splitting**
   - Splitter used
   - Chunk size
   - Chunk overlap
   - Output chunks

4. **Embedding**
   - Embedding model/provider
   - Where embeddings are created

5. **Vector database**
   - Chroma or other vector DB client
   - Collection name
   - Add/upsert logic
   - IDs and metadata

6. **Retrieval**
   - User query input
   - Similarity search / retriever
   - Number of results returned

7. **LLM response**
   - Prompt template
   - Model used
   - Context passed to model
   - Final answer returned

8. **Run instructions**
   - Main command
   - Required folders/files
   - Expected output

## Cheat sheet format
Use this format:

```markdown
# Project Cheat Sheet

## 1. Purpose
- One or two lines explaining the project.

## 2. Current RAG Flow
### Step 1: Load documents
- File:
- Object/function:
- What it does:

### Step 2: Split documents
- File:
- Object/function:
- Chunk size:
- Chunk overlap:

### Step 3: Store in vector DB
- File:
- DB/client:
- Collection:
- What is stored:

### Step 4: Retrieve context
- File:
- Query source:
- Retrieval method:

### Step 5: Generate answer
- File:
- Model:
- Prompt:
- Output:

## 3. Key Files
- `file.py`: short purpose

## 4. How to Run
```bash
command here
```

## 5. Notes to Remember
- Important learning points only.
```

## Style rules
- Be brief.
- Use bullets.
- Prefer simple words.
- Do not invent features.
- Do not document unused code as active behavior.
- Mention file names whenever possible.
- Update the cheat sheet whenever the code changes.
- If unsure, write `Needs verification` instead of guessing.
