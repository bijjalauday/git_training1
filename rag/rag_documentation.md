# RAG (Retrieval-Augmented Generation) — Complete Guide

> **Audience:** Freshers with basic Python knowledge  
> **Level:** Basic → Intermediate  
> **Goal:** Understand every building block of a RAG system — what it is, why it exists, and which variant to choose and when.

---

## Table of Contents

1. [What is RAG?](#1-what-is-rag)
2. [The RAG Pipeline — Big Picture](#2-the-rag-pipeline--big-picture)
3. [Document Loaders](#3-document-loaders)
4. [Text Splitters](#4-text-splitters)
5. [Embeddings](#5-embeddings)
6. [Vector Stores](#6-vector-stores)
7. [Retrievers](#7-retrievers)
8. [Prompt Templates](#8-prompt-templates)
9. [LLMs (Large Language Models)](#9-llms-large-language-models)
10. [Chains — Connecting Everything (LCEL)](#10-chains--connecting-everything-lcel)
11. [Putting It All Together — End-to-End Flow](#11-putting-it-all-together--end-to-end-flow)
12. [Common Pitfalls and Best Practices](#12-common-pitfalls-and-best-practices)

---

## 1. What is RAG?

### The Problem RAG Solves

Large Language Models (LLMs) like GPT-4 are trained on data up to a certain date. They also don't know anything about **your private documents** — your company reports, internal wikis, PDFs, etc. If you ask an LLM "What is our refund policy?", it simply doesn't know.

Two naive solutions — and why they fail:

| Approach | Problem |
|---|---|
| Fine-tune the LLM on your data | Expensive, slow, requires re-training whenever data changes |
| Put all documents in the prompt | LLMs have token limits; costs explode with large documents |

### What RAG Does

RAG = **Retrieve** relevant pieces of your documents, then **Augment** the LLM's prompt with those pieces, then let the LLM **Generate** the answer.

```
User Question
     ↓
Search your documents for relevant chunks
     ↓
Feed those chunks + the question into the LLM
     ↓
LLM generates a grounded, accurate answer
```

This way:
- The LLM only sees the *relevant* portion of your documents (no token limit explosion)
- It works on **live/private data** without re-training
- You can update documents at any time

---

## 2. The RAG Pipeline — Big Picture

A RAG system has two phases:

### Phase 1 — Indexing (done once, or when documents change)

```
Documents → Load → Split into Chunks → Embed Chunks → Store in Vector DB
```

### Phase 2 — Querying (done every time a user asks a question)

```
User Query → Embed Query → Search Vector DB → Retrieve Top Chunks → Build Prompt → LLM → Answer
```

Each box in these pipelines is a **component** with multiple options. The rest of this guide explains each one.

---

## 3. Document Loaders

### What They Are

Before any processing, you need to **read your documents** into a format Python can work with. Document loaders handle this — they abstract away file formats and give you a unified `Document` object with:
- `page_content` — the text
- `metadata` — file name, page number, source URL, etc.

### Types of Document Loaders

#### 3.1 File-Based Loaders

| Loader | Use Case | Notes |
|---|---|---|
| `TextLoader` | `.txt` files | Simplest loader, no extra dependencies |
| `PyPDFLoader` | `.pdf` files | Splits by page, good for most PDFs |
| `PDFMinerLoader` | `.pdf` files | Better layout preservation than PyPDF |
| `PyMuPDFLoader` | `.pdf` files | Fastest PDF loader, includes rich metadata |
| `Docx2txtLoader` | `.docx` Word files | Extracts raw text from Word documents |
| `UnstructuredWordDocumentLoader` | `.doc` / `.docx` | More robust, handles complex Word layouts |
| `CSVLoader` | `.csv` files | Each row becomes a Document |
| `JSONLoader` | `.json` files | Can use jq-like schema to extract fields |
| `UnstructuredMarkdownLoader` | `.md` files | Handles Markdown with headers, lists |
| `UnstructuredHTMLLoader` | `.html` files | Strips HTML tags, extracts text |
| `UnstructuredPowerPointLoader` | `.pptx` files | Slide-by-slide extraction |
| `UnstructuredExcelLoader` | `.xlsx` files | Sheet and cell extraction |

#### 3.2 Web/URL-Based Loaders

| Loader | Use Case |
|---|---|
| `WebBaseLoader` | Scrapes a webpage (uses BeautifulSoup) |
| `RecursiveUrlLoader` | Crawls a website and all its linked pages |
| `SeleniumURLLoader` | Loads JavaScript-rendered pages |
| `PlaywrightURLLoader` | Like Selenium but uses Playwright — more reliable |
| `WikipediaLoader` | Pulls articles directly from Wikipedia |
| `YoutubeLoader` | Loads transcripts from YouTube videos |

#### 3.3 Database / Cloud Loaders

| Loader | Use Case |
|---|---|
| `S3FileLoader` | Loads files from Amazon S3 |
| `GCSFileLoader` | Loads files from Google Cloud Storage |
| `NotionDBLoader` | Loads pages from a Notion database |
| `ConfluenceLoader` | Loads Confluence wiki pages |
| `SlackDirectoryLoader` | Loads exported Slack conversations |
| `GitHubIssuesLoader` | Loads GitHub issues as documents |
| `SQLDatabaseLoader` | Executes a SQL query and turns rows into Documents |

#### 3.4 The `UnstructuredFileLoader` — Swiss Army Knife

`UnstructuredFileLoader` uses the `unstructured` library which auto-detects file type and handles dozens of formats. Use it as a fallback when you don't know the file type in advance.

```python
# Auto-detects format
loader = UnstructuredFileLoader("mystery_file.rtf")
```

### Comparison: When to Use Which PDF Loader?

| Loader | Speed | Layout Accuracy | Best For |
|---|---|---|---|
| `PyPDFLoader` | Fast | Basic | Simple PDFs, clean text |
| `PDFMinerLoader` | Medium | High | PDFs with complex layouts |
| `PyMuPDFLoader` | Fastest | High + metadata | Production use, need page metadata |
| `UnstructuredFileLoader` | Slow | Best | Scanned PDFs, tables, mixed content |

**Rule of thumb:** Start with `PyPDFLoader`. If text extraction looks wrong (garbled tables, merged columns), switch to `PyMuPDFLoader`. For scanned documents use `Unstructured` with OCR enabled.

---

## 4. Text Splitters

### Why We Split Documents

LLMs have a **context window limit** — the maximum number of tokens they can process at once. Even if a model supports 128k tokens, sending an entire book for every query is wasteful and expensive. More importantly, **similarity search works better on small, focused chunks** than on large, mixed-topic passages.

Good splitting = better retrieval = better answers.

### The Core Concept: Chunk Size and Overlap

```
|--- chunk 1 ---|
              |--- chunk 2 ---|
                            |--- chunk 3 ---|

<-- overlap --> <-- overlap -->
```

- **chunk_size**: How many characters (or tokens) per chunk
- **chunk_overlap**: How many characters are shared between adjacent chunks

Overlap ensures a sentence split across two chunks doesn't lose meaning.

### Types of Text Splitters

#### 4.1 `CharacterTextSplitter`

The simplest splitter. Splits on a single separator (usually `\n\n` or `\n`).

```python
from langchain.text_splitter import CharacterTextSplitter

splitter = CharacterTextSplitter(
    separator="\n\n",
    chunk_size=1000,
    chunk_overlap=200
)
```

**Pros:** Fast, predictable  
**Cons:** Dumb — ignores sentence/paragraph boundaries; a single separator may create very uneven chunks  
**Best for:** Simple plain-text logs, quick prototypes

---

#### 4.2 `RecursiveCharacterTextSplitter` ✅ (Most Recommended)

Tries a list of separators in order: `["\n\n", "\n", " ", ""]`. First tries to split on double newlines (paragraphs), then single newlines, then spaces, then individual characters. This creates the most natural, semantically coherent chunks.

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n", "\n", " ", ""]
)
```

**Pros:** Respects natural language boundaries; adapts to any text format; widely battle-tested  
**Cons:** Still character-based, not semantically aware  
**Best for:** General text documents, PDFs, web pages, markdown — covers 90% of use cases

---

#### 4.3 `TokenTextSplitter`

Splits by **tokens** (not characters). One token ≈ 4 characters in English. Since LLMs think in tokens, this gives you precise control over chunk sizes relative to model limits.

```python
from langchain.text_splitter import TokenTextSplitter

splitter = TokenTextSplitter(
    chunk_size=256,   # tokens, not characters
    chunk_overlap=50
)
```

**Pros:** Precise token-level control, avoids accidentally splitting a 1000-char chunk that contains 1200 tokens  
**Cons:** Slower (needs tokenizer), may split mid-word  
**Best for:** When you need to guarantee chunks fit within model context windows

---

#### 4.4 `MarkdownHeaderTextSplitter`

Splits Markdown documents at header boundaries (`#`, `##`, `###`). Each chunk inherits the header tree as metadata.

```python
from langchain.text_splitter import MarkdownHeaderTextSplitter

headers_to_split_on = [
    ("#", "Header 1"),
    ("##", "Header 2"),
    ("###", "Header 3"),
]
splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
```

**Result:** Each chunk has metadata like `{"Header 1": "Introduction", "Header 2": "Installation"}`

**Pros:** Preserves document structure; metadata-rich chunks; ideal for wikis and docs  
**Cons:** Only works with Markdown  
**Best for:** Documentation sites, README files, Notion exports

---

#### 4.5 `HTMLHeaderTextSplitter`

Same concept as Markdown splitter but for HTML — splits on `<h1>`, `<h2>`, etc.

```python
from langchain.text_splitter import HTMLHeaderTextSplitter

headers_to_split_on = [("h1", "Header 1"), ("h2", "Header 2")]
splitter = HTMLHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
```

**Best for:** Scraped web pages, HTML exports from CMS systems

---

#### 4.6 `RecursiveJsonSplitter`

Designed for JSON data. Recursively splits a JSON object by keys while keeping nested structures intact.

```python
from langchain.text_splitter import RecursiveJsonSplitter

splitter = RecursiveJsonSplitter(max_chunk_size=300)
chunks = splitter.split_json(json_data)
```

**Pros:** Keeps JSON structure valid in each chunk; great for API responses  
**Cons:** Only for JSON  
**Best for:** API documentation, configuration data, structured JSON records

---

#### 4.7 `PythonCodeTextSplitter` / `Language.PYTHON`

Splits code files at function and class boundaries, not random character positions.

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter, Language

splitter = RecursiveCharacterTextSplitter.from_language(
    language=Language.PYTHON,
    chunk_size=1000,
    chunk_overlap=100
)
```

Supported languages: `PYTHON`, `JS`, `TS`, `JAVA`, `C`, `CPP`, `GO`, `RUBY`, `RUST`, `SCALA`, `SWIFT`, `MARKDOWN`, `LATEX`, `HTML`, `SOL`

**Pros:** Keeps functions/methods intact; code stays semantically meaningful  
**Cons:** Language-specific  
**Best for:** Code search, code documentation RAG, developer tools

---

#### 4.8 `SemanticChunker` (Advanced)

Uses embeddings to split text at **semantic boundaries** — splits happen where the topic meaningfully changes, not at arbitrary character positions.

```python
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import OpenAIEmbeddings

splitter = SemanticChunker(OpenAIEmbeddings())
```

**Pros:** Most semantically coherent chunks; preserves context best  
**Cons:** Slow (requires embedding every sentence); expensive; requires an embedding model  
**Best for:** High-quality RAG where retrieval accuracy matters more than speed

---

### Splitter Selection Guide

```
What type of content?
├── General text / PDFs / Web pages → RecursiveCharacterTextSplitter ✅
├── Need precise token control → TokenTextSplitter
├── Markdown documentation → MarkdownHeaderTextSplitter
├── HTML web pages → HTMLHeaderTextSplitter
├── JSON / API responses → RecursiveJsonSplitter
├── Source code → Language-specific RecursiveCharacterTextSplitter
└── Highest quality RAG (money no object) → SemanticChunker
```

### Choosing Chunk Size

| Document Type | Recommended chunk_size | chunk_overlap |
|---|---|---|
| Short news articles | 300–500 chars | 50 |
| General documents | 800–1200 chars | 150–200 |
| Legal / technical docs | 1500–2000 chars | 300 |
| Code | 500–1000 chars | 100 |

**Smaller chunks** = more precise retrieval, but may lose context  
**Larger chunks** = more context per chunk, but retrieval is less precise

---

## 5. Embeddings

### What Are Embeddings?

An embedding is a list of numbers (a vector) that represents the **meaning** of a piece of text. Texts with similar meanings produce vectors that are close together in space. This is what makes semantic search possible.

```
"The dog ran fast"     → [0.12, -0.45, 0.89, ...]  ← these two vectors
"The puppy sprinted"   → [0.11, -0.43, 0.91, ...]  ←   are very close
"The stock market fell" → [-0.72, 0.30, -0.15, ...] ← very different
```

### Types of Embedding Models

#### 5.1 OpenAI Embeddings

```python
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")     # older, cheaper
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")     # newer, better, cheap
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")     # best quality
```

| Model | Dimensions | Cost | Quality |
|---|---|---|---|
| `text-embedding-ada-002` | 1536 | Low | Good |
| `text-embedding-3-small` | 1536 (adjustable) | Very Low | Better |
| `text-embedding-3-large` | 3072 (adjustable) | Medium | Best |

**Pros:** State-of-the-art quality; easy to use; multilingual  
**Cons:** Paid API; your data leaves your servers  
**Best for:** Production apps, multilingual content, highest accuracy needs

---

#### 5.2 HuggingFace Sentence Transformers (Free, Local)

```python
from langchain_community.embeddings import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")        # fast, small
embeddings = HuggingFaceEmbeddings(model_name="all-mpnet-base-v2")       # better quality
embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-large-en-v1.5")  # near-OpenAI quality
```

| Model | Size | Speed | Quality |
|---|---|---|---|
| `all-MiniLM-L6-v2` | 80MB | Very Fast | Good |
| `all-mpnet-base-v2` | 420MB | Medium | Great |
| `BAAI/bge-large-en-v1.5` | 1.3GB | Slow | Excellent |

**Pros:** Free; runs locally; no data leaves your machine; no rate limits  
**Cons:** Requires local compute; setup can be complex; may be slower  
**Best for:** Privacy-sensitive data, offline environments, prototyping on a budget

---

#### 5.3 Google Vertex AI / Gemini Embeddings

```python
from langchain_google_vertexai import VertexAIEmbeddings

embeddings = VertexAIEmbeddings(model_name="textembedding-gecko@003")
```

**Best for:** GCP-based infrastructure, multilingual requirements

---

#### 5.4 Cohere Embeddings

```python
from langchain_cohere import CohereEmbeddings

embeddings = CohereEmbeddings(model="embed-english-v3.0")
```

**Unique feature:** Supports `input_type` — distinguish between embedding documents vs. queries for better retrieval accuracy.

**Best for:** When retrieval quality is critical; alternative to OpenAI

---

#### 5.5 Ollama (Local LLM Embeddings)

```python
from langchain_community.embeddings import OllamaEmbeddings

embeddings = OllamaEmbeddings(model="nomic-embed-text")
```

**Pros:** Fully local, free, easy to run  
**Best for:** Local development, privacy requirements, air-gapped environments

---

### Embeddings Comparison Summary

| Provider | Cost | Privacy | Quality | Setup |
|---|---|---|---|---|
| OpenAI | Paid | Cloud | Excellent | Easy |
| HuggingFace (local) | Free | Local | Very Good | Medium |
| Cohere | Paid | Cloud | Excellent | Easy |
| Ollama | Free | Local | Good | Easy |
| Google Vertex | Paid | Cloud | Excellent | Medium |

**For learning/prototyping:** HuggingFace `all-MiniLM-L6-v2` (free)  
**For production:** OpenAI `text-embedding-3-small` (best cost/quality ratio)  
**For sensitive data:** HuggingFace `BAAI/bge-large-en-v1.5` locally

---

## 6. Vector Stores

### What Is a Vector Store?

A vector store (also called a vector database) is a specialized database that stores embeddings and enables fast **similarity search** — "find me the vectors most similar to this query vector."

Traditional databases search by exact match. Vector databases search by **semantic similarity**.

### How Similarity Search Works

1. Store chunk embeddings indexed by a special algorithm (HNSW, IVF, etc.)
2. When a query comes in, embed the query  
3. Find the `k` stored vectors with the smallest distance to the query vector
4. Return the corresponding text chunks

The most common distance metrics:
- **Cosine similarity** — angle between vectors (most common for text)
- **Euclidean distance (L2)** — geometric distance
- **Dot product** — fast, good for normalized vectors (used by OpenAI models)

### Types of Vector Stores

#### 6.1 Chroma (Recommended for Learning)

```python
from langchain_community.vectorstores import Chroma

# Create and persist
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="./chroma_db"
)

# Load existing
vectorstore = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embeddings
)
```

**Pros:** Open-source; runs locally; zero infrastructure; easy to set up; perfect for prototyping  
**Cons:** Not designed for large scale (millions of documents); single-node  
**Best for:** Local development, learning, small-to-medium datasets (<100k documents)

---

#### 6.2 FAISS (Facebook AI Similarity Search)

```python
from langchain_community.vectorstores import FAISS

vectorstore = FAISS.from_documents(chunks, embeddings)

# Save and load
vectorstore.save_local("faiss_index")
vectorstore = FAISS.load_local("faiss_index", embeddings)
```

**Pros:** Blazing fast; supports billions of vectors; battle-tested at scale; entirely local  
**Cons:** No built-in persistence (you save/load manually); no metadata filtering out of the box  
**Best for:** Large local datasets, high-performance search, offline scenarios

---

#### 6.3 Pinecone

```python
from langchain_pinecone import PineconeVectorStore

vectorstore = PineconeVectorStore.from_documents(
    chunks, embeddings, index_name="my-index"
)
```

**Pros:** Fully managed cloud service; scales to billions of vectors; real-time updates; metadata filtering  
**Cons:** Paid service; data lives in the cloud  
**Best for:** Production applications, teams, serverless architectures

---

#### 6.4 Weaviate

```python
from langchain_weaviate import WeaviateVectorStore

vectorstore = WeaviateVectorStore.from_documents(
    chunks, embeddings, client=weaviate_client
)
```

**Pros:** Open-source + managed cloud; supports hybrid search (keyword + vector); schema-based; GraphQL API  
**Cons:** More complex setup  
**Best for:** When you need hybrid search + rich metadata queries

---

#### 6.5 Qdrant

```python
from langchain_qdrant import QdrantVectorStore

vectorstore = QdrantVectorStore.from_documents(
    chunks, embeddings, url="http://localhost:6333", collection_name="docs"
)
```

**Pros:** Open-source + cloud; high performance; payload filtering; Rust-based (fast)  
**Cons:** Requires running a server (or using cloud)  
**Best for:** Production use cases wanting open-source with cloud options

---

#### 6.6 pgvector (PostgreSQL)

```python
from langchain_postgres import PGVector

vectorstore = PGVector.from_documents(
    chunks, embeddings, connection="postgresql://user:pass@localhost/db"
)
```

**Pros:** Uses your existing PostgreSQL database; combine vector search with regular SQL; ACID compliance  
**Cons:** Not as fast as dedicated vector DBs for very large scale  
**Best for:** Teams already using PostgreSQL; want to avoid new infrastructure

---

#### 6.7 MongoDB Atlas Vector Search

**Best for:** Teams already using MongoDB Atlas

---

### Vector Store Comparison

| Vector Store | Hosting | Scale | Setup | Cost |
|---|---|---|---|---|
| Chroma | Local | Small-Medium | Very Easy | Free |
| FAISS | Local | Large | Easy | Free |
| Pinecone | Cloud | Massive | Easy | Paid |
| Weaviate | Local/Cloud | Large | Medium | Free/Paid |
| Qdrant | Local/Cloud | Large | Medium | Free/Paid |
| pgvector | Local/Cloud | Medium | Easy (with PG) | Free |

**Learning path recommendation:**
1. Start with **Chroma** (zero setup, just works)
2. Move to **FAISS** for larger local datasets
3. Use **Pinecone or Qdrant** when deploying to production

---

## 7. Retrievers

### What Is a Retriever?

A retriever is the component that, given a query, returns the most relevant document chunks. It wraps the vector store and adds search logic.

```python
retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 5}   # return top 5 chunks
)

docs = retriever.invoke("What is the refund policy?")
```

### Types of Retrieval Strategies

#### 7.1 Similarity Search (MMR-disabled)

Returns the `k` chunks with the highest cosine similarity to the query. Simple and fast.

```python
retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 5}
)
```

**Cons:** May return very similar/redundant chunks (5 chunks from the same paragraph)

---

#### 7.2 MMR — Maximum Marginal Relevance

Balances **relevance** and **diversity**. Picks chunks that are relevant to the query but also different from each other, avoiding redundancy.

```python
retriever = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 5, "fetch_k": 20, "lambda_mult": 0.5}
)
```

- `fetch_k`: How many candidates to consider (then pick `k` diverse ones)
- `lambda_mult`: 0 = maximize diversity, 1 = maximize similarity

**Pros:** Less redundant results; covers more aspects of the question  
**Best for:** Long documents with repeating content; when top chunks feel redundant

---

#### 7.3 Similarity Score Threshold

Only returns chunks above a minimum similarity score, avoiding returning irrelevant chunks when the answer isn't in the documents.

```python
retriever = vectorstore.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={"score_threshold": 0.7}
)
```

**Pros:** Avoids hallucination from low-quality retrieval  
**Cons:** May return zero results if nothing is above the threshold  
**Best for:** Q&A systems where "I don't know" is better than a wrong answer

---

#### 7.4 MultiQueryRetriever

Generates multiple variations of the user's question using an LLM, runs all of them, and combines results. Helps when the user's question might not exactly match document vocabulary.

```python
from langchain.retrievers.multi_query import MultiQueryRetriever

retriever = MultiQueryRetriever.from_llm(
    retriever=vectorstore.as_retriever(),
    llm=llm
)
```

Example: "How do I cancel?" might generate:
- "What is the cancellation process?"
- "Steps to terminate my subscription"
- "How to stop service"

**Pros:** Improves recall significantly; handles paraphrasing  
**Cons:** Slower (multiple LLM calls + multiple searches); higher cost  
**Best for:** When recall matters more than speed; complex questions

---

#### 7.5 ContextualCompressionRetriever

First retrieves chunks, then uses an LLM to **compress** each chunk to only the relevant parts before passing to the answer LLM.

```python
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor

compressor = LLMChainExtractor.from_llm(llm)
retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=vectorstore.as_retriever()
)
```

**Pros:** Sends cleaner, more focused context to the LLM; reduces noise  
**Cons:** Extra LLM calls = more expensive and slower  
**Best for:** Very large chunks, or when context window is tight

---

#### 7.6 BM25Retriever (Keyword-Based)

Traditional TF-IDF / BM25 keyword search — no embeddings needed. 

```python
from langchain_community.retrievers import BM25Retriever

retriever = BM25Retriever.from_documents(docs, k=5)
```

**Pros:** Works without embeddings; great for exact keyword matching; no API cost  
**Cons:** No semantic understanding; "automobile" and "car" are unrelated to it  
**Best for:** Configuration files, code, exact-term queries

---

#### 7.7 EnsembleRetriever (Hybrid Search) — Best of Both Worlds

Combines BM25 (keyword) and vector (semantic) retrieval using Reciprocal Rank Fusion. This is currently considered the best retrieval strategy.

```python
from langchain.retrievers import EnsembleRetriever

bm25_retriever = BM25Retriever.from_documents(docs, k=5)
vector_retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

ensemble_retriever = EnsembleRetriever(
    retrievers=[bm25_retriever, vector_retriever],
    weights=[0.5, 0.5]
)
```

**Pros:** Catches both exact matches and semantic matches; best recall  
**Cons:** Slower; more infrastructure  
**Best for:** Production RAG systems where accuracy matters most

---

#### 7.8 ParentDocumentRetriever

Indexes small chunks (for precise retrieval) but returns their larger parent chunks (for richer context to the LLM).

```python
from langchain.retrievers import ParentDocumentRetriever

retriever = ParentDocumentRetriever(
    vectorstore=vectorstore,
    docstore=InMemoryStore(),
    child_splitter=child_splitter,    # small chunks (200 chars)
    parent_splitter=parent_splitter   # large chunks (2000 chars)
)
```

**Pros:** Better of both worlds — precise retrieval + rich context  
**Best for:** When small chunks are too sparse but large chunks hurt retrieval precision

---

### Retriever Selection Guide

```
Start with: similarity (k=5)
If results are redundant: switch to MMR
If getting irrelevant results: add score_threshold
If vocabulary mismatch: use MultiQueryRetriever
For production: EnsembleRetriever (BM25 + Vector)
For precise retrieval + full context: ParentDocumentRetriever
```

---

## 8. Prompt Templates

### Why Prompts Matter in RAG

The retriever finds relevant chunks. The prompt is how you tell the LLM **what to do with those chunks**. A bad prompt leads to hallucinations, ignored sources, or generic answers.

### Types of Prompt Templates in LangChain

#### 8.1 `PromptTemplate` — Simple String Template

```python
from langchain_core.prompts import PromptTemplate

template = """Answer the question based on the context below.

Context: {context}
Question: {question}
Answer:"""

prompt = PromptTemplate.from_template(template)
```

**Best for:** Simple single-turn Q&A

---

#### 8.2 `ChatPromptTemplate` — For Chat Models

Structures messages with roles: `system`, `human`, `assistant`. This is the correct approach for GPT-4, Claude, and Gemini.

```python
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Answer only based on the provided context."),
    ("human", "Context:\n{context}\n\nQuestion: {question}")
])
```

**Why use roles?**
- `system`: Sets LLM behavior/persona — it pays high attention to these instructions
- `human`: The user's input
- `assistant`: Previous AI responses (for multi-turn conversations)

**Best for:** Production RAG with chat models

---

#### 8.3 `MessagesPlaceholder` — For Conversation History

Used in **conversational RAG** where the user asks follow-up questions.

```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Use the context to answer questions."),
    MessagesPlaceholder("chat_history"),   # ← injects previous messages here
    ("human", "Context:\n{context}\n\nQuestion: {question}")
])
```

**Best for:** Chatbots, follow-up question support

---

#### 8.4 `FewShotPromptTemplate` — With Examples

Provides examples of question/answer pairs to guide the LLM's behavior.

```python
from langchain_core.prompts import FewShotPromptTemplate

examples = [
    {"question": "What is our return policy?", "answer": "Products can be returned within 30 days."},
    {"question": "Do you ship internationally?", "answer": "We ship to 50 countries."},
]

prompt = FewShotPromptTemplate(
    examples=examples,
    example_prompt=PromptTemplate.from_template("Q: {question}\nA: {answer}"),
    prefix="Answer questions about our company:\n",
    suffix="Q: {question}\nA:",
    input_variables=["question"]
)
```

**Best for:** When you want the LLM to follow a specific answer format or tone

---

### RAG Prompt Best Practices

1. **Tell the LLM to stay grounded**: "Only use the provided context. Do not make up information."
2. **Handle the no-answer case**: "If the context doesn't contain the answer, say 'I don't have information about this.'"
3. **Ask for source citations**: "Mention which document the information came from."
4. **Set tone/persona**: "You are a customer support agent for Acme Corp."
5. **Keep it focused**: Don't add unnecessary instructions; they dilute the important ones.

---

## 9. LLMs (Large Language Models)

### Role in RAG

The LLM is the **generation** component — it receives the retrieved context + user question from the prompt, and generates a coherent, grounded answer.

### Types of LLMs in LangChain

#### 9.1 OpenAI Models

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)
llm = ChatOpenAI(model="gpt-4", temperature=0.3)
llm = ChatOpenAI(model="gpt-4o", temperature=0.3)        # faster, cheaper than gpt-4
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)   # cheapest, still good
```

| Model | Speed | Cost | Quality | Context |
|---|---|---|---|---|
| `gpt-3.5-turbo` | Fast | Cheapest | Good | 16k tokens |
| `gpt-4o-mini` | Fast | Very Cheap | Very Good | 128k tokens |
| `gpt-4o` | Fast | Medium | Excellent | 128k tokens |
| `gpt-4` | Slow | Expensive | Excellent | 8k/128k tokens |

---

#### 9.2 Anthropic Claude

```python
from langchain_anthropic import ChatAnthropic

llm = ChatAnthropic(model="claude-3-haiku-20240307")    # fast, cheap
llm = ChatAnthropic(model="claude-3-sonnet-20240229")   # balanced
llm = ChatAnthropic(model="claude-3-opus-20240229")     # most powerful
```

**Known strengths:** Long context (200k tokens), following complex instructions, less hallucination

---

#### 9.3 Google Gemini

```python
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(model="gemini-pro")
llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro")    # 1M token context!
```

**Known strengths:** Multimodal (text + images), massive context window

---

#### 9.4 Local Models via Ollama

```python
from langchain_community.llms import Ollama

llm = Ollama(model="llama3")
llm = Ollama(model="mistral")
llm = Ollama(model="codellama")  # for code-related RAG
```

**Pros:** Free, fully local, private  
**Cons:** Requires GPU; quality below GPT-4  
**Best for:** Sensitive data, offline environments, learning on a budget

---

#### 9.5 HuggingFace Models

```python
from langchain_community.llms import HuggingFacePipeline
from transformers import pipeline

pipe = pipeline("text-generation", model="mistralai/Mistral-7B-Instruct-v0.2")
llm = HuggingFacePipeline(pipeline=pipe)
```

**Best for:** Custom fine-tuned models, research

---

### `temperature` Parameter Explained

Temperature controls randomness in the LLM's output:

| Temperature | Behavior | Best For |
|---|---|---|
| `0.0` | Deterministic, always same answer | Factual Q&A, RAG retrieval answers |
| `0.3–0.5` | Slightly creative but mostly consistent | General RAG, summaries |
| `0.7–0.9` | Creative, varied | Creative writing |
| `1.0+` | Very random | Brainstorming |

**For RAG:** Use `temperature=0` or low values (0.0–0.3). You want consistent, factual answers, not creative hallucinations.

---

## 10. Chains — Connecting Everything (LCEL)

### What Is LCEL?

**LCEL (LangChain Expression Language)** is a declarative way to compose LangChain components into pipelines using the `|` (pipe) operator — just like Unix pipes.

```python
chain = retriever | format_docs | prompt | llm | output_parser
```

Each component is a **Runnable** that accepts an input and produces an output. The `|` passes the output of one component as the input to the next.

### The `|` Pipe Operator

```python
# This:
chain = prompt | llm | StrOutputParser()

# Is equivalent to:
def chain(input):
    step1 = prompt.invoke(input)
    step2 = llm.invoke(step1)
    step3 = StrOutputParser().invoke(step2)
    return step3
```

### Key LCEL Runnables

#### 10.1 `RunnablePassthrough`

Passes the input through unchanged. Used when you want to pass the query directly without transformation.

```python
from langchain_core.runnables import RunnablePassthrough

chain = {"context": retriever, "question": RunnablePassthrough()} | prompt | llm
```

Here: `context` gets the retrieved docs, `question` gets the original user query unchanged.

---

#### 10.2 `RunnableParallel`

Runs multiple chains in **parallel** and combines their outputs into a dictionary.

```python
from langchain_core.runnables import RunnableParallel

chain_with_sources = RunnableParallel({
    "answer": rag_chain,
    "sources": retriever
})

result = chain_with_sources.invoke("What is RAG?")
# result = {"answer": "RAG is...", "sources": [doc1, doc2, ...]}
```

**Best for:** Getting both answer and sources simultaneously

---

#### 10.3 `RunnableLambda`

Wraps any Python function as a Runnable.

```python
from langchain_core.runnables import RunnableLambda

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# Use in chain:
chain = retriever | RunnableLambda(format_docs) | prompt | llm
```

---

#### 10.4 `StrOutputParser`

Converts the LLM's `AIMessage` response object into a plain Python string.

```python
from langchain_core.output_parsers import StrOutputParser

chain = prompt | llm | StrOutputParser()
result = chain.invoke({"question": "What is RAG?"})
# result is now a plain string, not an AIMessage object
```

---

#### 10.5 `JsonOutputParser`

Parses the LLM output as JSON. Useful when you want the LLM to return structured data.

```python
from langchain_core.output_parsers import JsonOutputParser

chain = prompt | llm | JsonOutputParser()
result = chain.invoke(...)
# result is a Python dict
```

---

#### 10.6 `PydanticOutputParser` (Advanced)

Parses LLM output into a Pydantic model with validation.

```python
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel

class Answer(BaseModel):
    answer: str
    confidence: float
    sources: list[str]

parser = PydanticOutputParser(pydantic_object=Answer)
```

---

### Streaming with LCEL

One major benefit of LCEL is built-in streaming support. Every chain automatically supports `.stream()`:

```python
# Instead of waiting for full response:
answer = chain.invoke(query)

# Stream tokens as they're generated:
for chunk in chain.stream(query):
    print(chunk, end="", flush=True)
```

This gives users a ChatGPT-like experience where text appears progressively.

---

### A Complete LCEL RAG Chain

```python
def format_docs(docs):
    return "\n\n".join(
        f"[Source: {doc.metadata.get('source', 'unknown')}]\n{doc.page_content}"
        for doc in docs
    )

rag_chain = (
    {
        "context": retriever | format_docs,    # retrieve and format
        "question": RunnablePassthrough()       # pass query as-is
    }
    | prompt          # fill the template
    | llm             # generate response
    | StrOutputParser() # convert to string
)

answer = rag_chain.invoke("What is the cancellation policy?")
```

---

## 11. Putting It All Together — End-to-End Flow

Here is the complete RAG flow with all components labeled:

```
                    ┌─────────────────── INDEXING PHASE ───────────────────┐
                    │                                                        │
  Documents         │   Document          Text           Embedding          │
 (PDF/Word/TXT) ──▶ │   Loader     ──▶   Splitter  ──▶  Model      ──▶    │──▶ Vector Store
                    │  (PyPDF,           (Recursive,     (OpenAI,           │    (Chroma,
                    │   TextLoader)       TokenBased,     HuggingFace)      │     FAISS,
                    │                    Markdown..)                         │     Pinecone)
                    └────────────────────────────────────────────────────────┘

                    ┌─────────────────── QUERYING PHASE ───────────────────┐
                    │                                                        │
  User Query ──────▶│  Embed Query ──▶  Retriever ──▶  Prompt Template ──▶ LLM ──▶ Answer
                    │  (same model        (similarity/     (ChatPrompt         (GPT/Claude/
                    │  as indexing)       MMR/hybrid)       Template)           Ollama)
                    └────────────────────────────────────────────────────────┘
```

### Step-by-Step for Beginners

**Indexing (one-time setup):**
1. **Load**: Read files from disk/web → get `Document` objects
2. **Split**: Break large documents into smaller chunks
3. **Embed**: Convert each chunk into a vector using an embedding model
4. **Store**: Save vectors + text in a vector database

**Querying (every user request):**
1. **Embed query**: Convert the user's question into a vector (same model as step 3 above)
2. **Retrieve**: Find the top-k most similar chunk vectors in the database
3. **Augment**: Insert the retrieved text into a prompt template
4. **Generate**: Send prompt to LLM → get answer
5. **Return**: Show the answer to the user

---

## 12. Common Pitfalls and Best Practices

### Pitfalls to Avoid

| Problem | Cause | Fix |
|---|---|---|
| LLM gives wrong answers | Retrieved chunks aren't relevant | Increase k, use MMR or hybrid retrieval |
| LLM hallucinates | Context not grounding the answer | Add "only answer from context" to system prompt |
| Slow responses | Chunk size too large; too many chunks | Reduce k, use smaller chunks |
| Missing information | Chunks split across key sentences | Increase chunk_overlap |
| High cost | Expensive embedding model + large k | Use local embeddings; reduce k |
| "I don't know" for simple questions | threshold too high or chunk too small | Lower score_threshold; adjust chunk size |

### Best Practices

1. **Match embedding models**: Use the same model for indexing AND querying. Never mix models.

2. **Chunk size experimentation**: There is no universal "best" chunk size. Try 500, 1000, and 2000 — evaluate which gives better answers for your specific documents.

3. **Metadata is your friend**: Add file name, page number, section title to chunk metadata. It helps cite sources and enables metadata filtering.

4. **Evaluate retrieval separately**: Before testing the full chain, check what chunks are being retrieved. Bad retrieval = bad answers, regardless of LLM quality.

5. **Temperature = 0 for RAG**: In RAG, you want the LLM to report facts, not be creative. Low temperature is essential.

6. **Never hardcode API keys**: Use `.env` files and `python-dotenv`, or environment variables.
   ```python
   # Bad ❌
   OPENAI_API_KEY = "sk-..."
   
   # Good ✅
   from dotenv import load_dotenv
   load_dotenv()
   # Key is in .env file: OPENAI_API_KEY=sk-...
   ```

7. **Handle empty retrieval**: If no chunks are retrieved (score threshold too high), the LLM will get an empty context. Always handle this case.

8. **Test with adversarial queries**: Try questions whose answers are NOT in the documents. The system should say "I don't know", not hallucinate.

---

## Quick Reference Cheat Sheet

| Component | Learning/Prototyping | Production |
|---|---|---|
| Loader | `PyPDFLoader`, `TextLoader` | `PyMuPDFLoader`, `UnstructuredFileLoader` |
| Splitter | `RecursiveCharacterTextSplitter` | `RecursiveCharacterTextSplitter` + tune chunk_size |
| Embeddings | HuggingFace `all-MiniLM-L6-v2` (free) | OpenAI `text-embedding-3-small` |
| Vector Store | Chroma | Pinecone / Qdrant / pgvector |
| Retriever | `similarity k=5` | `EnsembleRetriever` (BM25 + Vector) |
| LLM | `gpt-3.5-turbo` or Ollama | `gpt-4o-mini` or Claude |
| Chain | Basic LCEL | LCEL with streaming + sources |

---

*This document covers RAG from fundamentals to intermediate concepts. For advanced topics (agentic RAG, graph RAG, re-ranking, fine-tuning embeddings), refer to the LangChain documentation and research papers.*
