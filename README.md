# 🧠 Hybrid AI Knowledge Assistant

> A production-oriented, full-stack AI system that unifies **document intelligence** and **structured data analytics** into a single conversational interface.

---

## 📌 Overview

The **Hybrid AI Knowledge Assistant** is a context-aware, multi-source AI platform that allows users to interact naturally with both unstructured documents and structured business data. It combines a **Retrieval-Augmented Generation (RAG)** pipeline for documents with a **Pandas Data Agent** for analytics — all through a unified conversational interface with persistent memory.

---

## ✨ Features

### 📄 Document Intelligence (RAG Pipeline)
Supports **PDF**, **DOCX**, and **TXT** file formats.

| Stage | Description |
|-------|-------------|
| Upload | Accepts and parses multi-format documents |
| Chunking | Splits documents into semantically meaningful segments |
| Embeddings | Converts chunks into vector representations via HuggingFace |
| FAISS Indexing | Stores and retrieves vectors efficiently |
| LLM Generation | Produces grounded answers via OpenRouter |

**Capabilities:**
- Semantic search across uploaded documents
- Source-cited, grounded answers
- Multi-turn conversational memory
- OpenRouter LLM integration (GPT-4o-mini)

---

### 📊 Structured Data Intelligence (Pandas Data Agent)
Supports **CSV**, **XLSX**, and **XLS** file formats.

| Stage | Description |
|-------|-------------|
| Upload | Ingests tabular business data |
| Pandas Agent | Runs dynamic Python-based analysis |
| Memory | Retains follow-up query context |
| Answer | Returns precise, computed results |

**Capabilities:**
- Aggregations, filtering, and sorting
- Follow-up query chaining with memory
- Exact numeric analytics on business data

**Example Conversation:**
```
Q: What is the total sales?
Q: Excluding cancelled orders?
Q: Which region has the highest profit?
```

---

## 🏗️ Architecture

```
User Upload
     │
     ▼
File Type Detection
     │
     ├── PDF / DOCX / TXT ──► RAG Pipeline
     │                          ├── Chunking
     │                          ├── HuggingFace Embeddings
     │                          └── FAISS Vector Store
     │
     └── CSV / XLSX / XLS ──► Pandas Data Agent
                                └── Dynamic Analysis
     │
     ▼
OpenRouter LLM (GPT-4o-mini)
     │
     ▼
Answer + Memory + Source Citations
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python, Flask, LangChain |
| **Frontend** | Next.js 14, React, Tailwind CSS |
| **Vector Store** | FAISS |
| **Data Processing** | Pandas |
| **LLM Provider** | OpenRouter API (GPT-4o-mini) |
| **Embeddings** | HuggingFace Embeddings |

---

## 📂 Supported File Types

| Format | Extension | Processing Mode |
|--------|-----------|----------------|
| PDF Document | `.pdf` | RAG Pipeline |
| Word Document | `.docx` | RAG Pipeline |
| Plain Text | `.txt` | RAG Pipeline |
| CSV File | `.csv` | Pandas Data Agent |
| Excel Workbook | `.xlsx` / `.xls` | Pandas Data Agent |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- OpenRouter API Key

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/hybrid-ai-knowledge-assistant.git
cd hybrid-ai-knowledge-assistant
```

### 2. Backend Setup
```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Add your OPENROUTER_API_KEY to .env

# Start the Flask server
python app.py
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

The application will be available at `http://localhost:3000`.

---

## 📸 Screenshots

### Document Intelligence
![Document QA](assets/document_qa.png)

### Structured Data Analytics
![Data Analytics](assets/data_agent.png)

---

## 💡 Example Use Cases

### Document Q&A
```
- "What is NAIRP and what are its objectives?"
- "Summarize the key recommendations from the report."
- "What is the proposed budget outlined in the document?"
```

### Structured Data Analytics
```
- "What is the total revenue for Q3?"
- "Show me sales figures excluding cancelled orders."
- "Which region generated the highest profit last year?"
```

---

## ⚡ Engineering Challenges

Key challenges encountered and solved during development:

- **Hallucination control** — grounding LLM responses strictly to retrieved document chunks to prevent fabricated answers
- **Retrieval relevance** — tuning chunk size, overlap, and embedding strategies to improve semantic search accuracy
- **Hybrid routing** — designing a clean decision layer to correctly direct queries to either the RAG pipeline or the Pandas Data Agent
- **Cross-pipeline memory** — maintaining coherent conversational context across both document and structured data sessions
- **Large file ingestion** — handling heavy PDFs and Excel files without blocking the server or degrading response latency

---

## 🔮 Roadmap

- [ ] Cloud deployment (AWS / GCP / Azure)
- [ ] User authentication & session management
- [ ] Configurable model selector (GPT-4o, Claude, Gemini, etc.)
- [ ] Hybrid semantic + keyword search
- [ ] Role-based document access control
- [ ] Dashboard for analytics visualization

---

## 🤝 Contributing

Contributions are welcome! Please open an issue first to discuss what you'd like to change, then submit a pull request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add your feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request


---

<p align="center">Built with ❤️ using LangChain, FAISS, and OpenRouter</p>