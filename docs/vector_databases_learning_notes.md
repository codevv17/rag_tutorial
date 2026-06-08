# Vector Databases — Learning Notes

## 1. What is a Vector Database?

A vector database stores and searches **embedding vectors**.

In RAG, the goal is:

```text
Large document collection
↓
Break into chunks
↓
Convert chunks into embeddings
↓
Store embeddings in a vector database
↓
Retrieve the most relevant chunks for a user question
↓
Send those chunks to the LLM as context
```

A vector database is optimized for:

```text
"Find the chunks closest in meaning to this question."
```

That is different from traditional SQL search, which usually looks for exact values.

---

## 2. What does a vector DB store?

Conceptually, each chunk is like a JSON-style object:

```json
{
  "id": "VH021_page_2_chunk_0",
  "document": "Composting improves soil fertility...",
  "embedding": [-0.005, 0.005, 0.024, "..."],
  "metadata": {
    "source": "VH021.pdf",
    "page": 2
  }
}
```

The main fields are:

```text
id          → unique identifier
document    → actual chunk text
embedding   → numerical vector representation of the chunk
metadata    → source, page number, file name, topic, etc.
```

Important note:

```text
API view:
Looks like JSON/object records.

Internal database view:
May be stored using optimized tables, files, indexes, graphs, or compressed structures.
```

So the JSON-object mental model is correct for learning, but internally each vector DB can store data differently.

---

## 3. Vector DB vs Relational DB vs NoSQL

Vector databases feel closer to NoSQL/document databases than relational databases.

| Concept | Relational DB | MongoDB / NoSQL | Vector DB |
|---|---|---|---|
| Container | Table | Collection | Collection / Index |
| Record | Row | Document | Chunk/vector record |
| Schema | Strict | Flexible | Flexible metadata + vector |
| Search | SQL / joins | JSON queries | Similarity search |
| Main strength | Structured data | Flexible app data | Semantic retrieval |

Simple mental model:

```text
Relational DB:
Find exact rows using SQL.

MongoDB:
Find flexible JSON documents.

Vector DB:
Find semantically similar chunks using embeddings.
```

---

## 4. Is the embedding model part of the vector DB?

Usually, no.

The clean separation is:

```text
Embedding model
= converts text into vectors

Vector database
= stores vectors and retrieves similar vectors
```

But some vector databases, including Chroma, can use an embedding function for you.

### Option 1: Let Chroma create embeddings

```python
collection.upsert(
    ids=ids,
    documents=documents,
    metadatas=metadata
)
```

In this case, Chroma uses the collection's configured embedding function.

### Option 2: Create embeddings yourself

```python
collection.upsert(
    ids=ids,
    documents=documents,
    metadatas=metadata,
    embeddings=embeddings
)
```

In this case, you use your own embedding model, such as OpenAI, Hugging Face, or another model, and Chroma only stores/searches the embeddings.

Simple rule:

```text
Chroma is not the embedding model.
Chroma can use an embedding model for you.
You can also generate embeddings yourself and pass them into Chroma.
```

---

## 5. What is an index in a vector database?

An index is a special data structure that helps the database find similar vectors faster.

Without an index:

```text
Query vector compared against every chunk vector
↓
Slow for large datasets
```

With an index:

```text
Vectors are organized into a searchable structure
↓
Database quickly finds nearby vectors
```

Simple analogy:

```text
Documents/chunks = books
Embeddings = meaning coordinates
Vector index = map for finding nearby meanings quickly
```

In RAG:

```text
User question
↓
Question embedding
↓
Vector index search
↓
Top-k closest chunk embeddings
↓
Return chunk text + metadata
```

---

## 6. Common vector index types

Common names:

```text
Flat
HNSW
IVF
PQ
IVF_PQ
DiskANN
ScaNN
```

### Flat index

```text
Compares query vector against every vector.
Most accurate.
Can be slow at large scale.
```

### HNSW

```text
Graph-based approximate nearest neighbor search.
Fast and commonly used.
Often uses more memory.
```

HNSW mental model:

```text
Each vector is a node.
Similar vectors are connected.
Search jumps through the graph to find close vectors.
```

### IVF

```text
Clusters vectors into groups.
Searches only likely relevant clusters.
Good for large scale.
Requires tuning.
```

### PQ / IVF_PQ

```text
Compresses vectors to reduce memory.
Can reduce accuracy slightly.
Useful for very large vector collections.
```

### ANN

ANN is not one specific index.

```text
ANN = Approximate Nearest Neighbor
```

It is the broad category that includes HNSW, IVF, PQ, and other fast approximate search methods.

---

## 7. Can users choose the index type?

It depends on the vector database.

| Product | Index Control | Simple View |
|---|---|---|
| ChromaDB | Limited | Mostly HNSW with some tuning |
| Pinecone | Mostly managed | Product abstracts index internals |
| Qdrant | Moderate | HNSW-style indexing with tuning/quantization |
| Milvus | High | User can choose HNSW, IVF, PQ, etc. |
| FAISS | High | User directly chooses index type |
| Azure AI Search | Managed | Enterprise search + vector search |
| Databricks Vector Search | Managed | Vector search inside lakehouse |

Simple rule:

```text
Some products hide the index details.
Some products allow tuning.
Some products let you choose the full index strategy.
```

---

## 8. Major vector databases

### ChromaDB

Best for:

```text
learning RAG
local development
small/medium prototypes
simple Python projects
```

Mental model:

```text
ChromaDB = easiest local RAG vector DB.
```

### Pinecone

Best for:

```text
managed production RAG
SaaS apps
teams that do not want to manage infrastructure
high-scale semantic search
```

Mental model:

```text
Pinecone = production SaaS vector DB.
```

### Weaviate

Best for:

```text
open-source vector DB
hybrid search
semantic search + metadata
enterprise knowledge apps
```

Mental model:

```text
Weaviate = open-source AI-native database for semantic and hybrid search.
```

### Qdrant

Best for:

```text
fast open-source production vector search
metadata filtering
self-hosted or cloud deployment
```

Mental model:

```text
Qdrant = fast open-source production vector DB.
```

### Milvus / Zilliz

Best for:

```text
very large-scale vector search
billions of vectors
distributed enterprise deployments
```

Mental model:

```text
Milvus = heavy-duty open-source vector DB.
Zilliz = managed Milvus.
```

### FAISS

Best for:

```text
local experiments
research
custom vector search
in-memory similarity search
```

Mental model:

```text
FAISS = vector search library, not a complete database.
```

### Elasticsearch / OpenSearch

Best for:

```text
hybrid search
keyword search + vector search
logs, documents, enterprise search
```

Mental model:

```text
Elasticsearch/OpenSearch = search engine plus vector search.
```

### PostgreSQL + pgvector

Best for:

```text
apps already using PostgreSQL
small/medium RAG
SQL + structured data + vectors together
```

Mental model:

```text
Postgres + pgvector = vector search inside a relational database.
```

### Azure AI Search

Best for:

```text
Azure enterprise RAG
hybrid search
business documents
Azure OpenAI integration
```

Mental model:

```text
Azure AI Search = enterprise search plus vector search.
```

### Databricks Vector Search

Best for:

```text
Databricks lakehouse
Unity Catalog governed data
Delta tables and enterprise RAG
```

Mental model:

```text
Databricks Vector Search = vector search inside the Databricks ecosystem.
```

---

## 9. How large are production vector databases?

There is no single industry standard. Size depends on:

```text
number of documents
average chunks per document
embedding dimension
metadata size
index type
replication
refresh frequency
```

Practical ranges:

| Scale | Approx. Vector Count | Use Case |
|---|---:|---|
| Small production | 50K – 500K | Department docs, small knowledge base |
| Medium production | 500K – 5M | Company docs, Confluence, SharePoint, PDFs |
| Large production | 5M – 100M | Enterprise search, support history, many tenants |
| Very large scale | 100M – 1B+ | Search platforms, recommendations, massive stores |

For many normal enterprise RAG apps:

```text
100K to 5M vectors is common.
```

For larger enterprise platforms:

```text
5M to 100M vectors is realistic.
```

---

## 10. How to estimate vector count

The number of vectors usually equals the number of chunks.

```text
Number of vectors ≈ Number of documents × Average chunks per document
```

Examples:

```text
10,000 PDFs × 50 chunks each = 500,000 vectors
100,000 Confluence pages × 10 chunks each = 1,000,000 vectors
50,000 documents × 30 chunks each = 1,500,000 vectors
```

The real sizing question is:

```text
How many chunks will I create?
```

---

## 11. Storage estimate

For float32 embeddings:

```text
Storage per vector ≈ dimension × 4 bytes
```

Approximate raw vector sizes:

| Embedding Dimension | Raw Size per Vector |
|---:|---:|
| 384 | ~1.5 KB |
| 768 | ~3 KB |
| 1536 | ~6 KB |
| 3072 | ~12 KB |

Example using 1536-dimensional vectors:

| Vector Count | Raw Vector Storage Only |
|---:|---:|
| 100K | ~600 MB |
| 1M | ~6 GB |
| 10M | ~60 GB |
| 100M | ~600 GB |

Actual storage is often higher because the system also stores:

```text
documents
metadata
indexes
replicas
logs
overhead
```

Real storage may be 2x to 5x the raw vector size.

---

## 12. How to choose a vector database

Ask these questions:

```text
How many chunks/vectors?
What embedding dimension?
Do I need metadata filtering?
Do I need hybrid search?
How often does data refresh?
How many users/queries per day?
Do I need tenant isolation?
Do I need enterprise security/governance?
Do I want managed service or self-hosting?
Is my data already in Azure, Databricks, or PostgreSQL?
```

Simple recommendation:

```text
Learning/local:
ChromaDB

Managed production:
Pinecone

Open-source production:
Qdrant or Weaviate

Very large scale:
Milvus/Zilliz

Existing PostgreSQL app:
pgvector

Azure enterprise:
Azure AI Search

Databricks lakehouse:
Databricks Vector Search
```

---

## 13. Final mental model

```text
Chunk
= piece of document text

Embedding
= numerical meaning of the chunk

Vector DB
= stores embeddings, documents, metadata, and IDs

Index
= fast-search structure for finding similar vectors

Similarity search
= retrieve chunks closest in meaning to the user question

RAG
= retrieve the best context and send it to the LLM
```

The most important idea:

```text
The vector database is not the whole RAG system.
It is one part of the context engineering pipeline.
```

A strong RAG system depends on:

```text
good loading
good chunking
good embedding model
good metadata
good vector/index strategy
good retrieval
good reranking
good prompt/context formatting
good citations
```
