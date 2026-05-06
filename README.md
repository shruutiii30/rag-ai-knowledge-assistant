# 🤖 RAG-Based AI Knowledge Base Assistant

An end-to-end **Retrieval-Augmented Generation (RAG)** system that allows users to upload multiple PDF documents and ask natural language questions to receive **context-aware answers with source attribution**.

This project combines **Flask APIs, semantic search, FAISS vector database, HuggingFace embeddings, and a modern frontend UI** to create a real-world AI knowledge assistant.

---

# 🚀 Features

✅ Upload multiple PDF documents  
✅ Extract and preprocess document text  
✅ Intelligent chunking with overlap  
✅ Semantic search using embeddings  
✅ Fast vector retrieval with FAISS  
✅ Context-aware question answering  
✅ Source citation (page + content preview)  
✅ Chat memory for follow-up questions  
✅ Persistent vector storage  
✅ Full-stack frontend integration  

---

# 🧠 System Architecture

```text
User
 ↓
Frontend UI
 ↓
Flask APIs
 ↓
Document Processing
 ↓
Chunking
 ↓
Embeddings
 ↓
FAISS Vector Store
 ↓
Retrieval
 ↓
LLM Answer Generation
 ↓
Answer + Sources
```

---

# 🛠️ Tech Stack

## Backend
- Python
- Flask
- LangChain

## AI / NLP
- HuggingFace Transformers
- HuggingFace Embeddings
- Retrieval-Augmented Generation (RAG)

## Vector Database
- FAISS

## Document Processing
- PyPDF

## Frontend
- React
- Tailwind CSS

## Testing
- Postman

---

# 📂 Project Structure

```text
AI-Knowledge-Assistant/
│
├── app.py
├── ingestion.py
├── chunking.py
├── embeddings.py
├── retrieval.py
├── llm.py
├── requirements.txt
│
├── frontend/
│   ├── src/
│   ├── package.json
│
├── data/
├── faiss_index/
│
└── README.md
```

---

# ⚙️ Installation

## 1. Clone Repository

```bash
git clone <your-github-repo-url>
cd <project-folder>
```

---

## 2. Create Virtual Environment

### Windows

```bash
python -m venv ragenv
ragenv\Scripts\activate
```

---

## 3. Install Backend Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Run Backend

```bash
python app.py
```

Backend runs on:

```text
http://127.0.0.1:5000
```

---

## 5. Run Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on:

```text
http://localhost:5173
```

---

# 📌 API Endpoints

## Upload Documents

### POST `/upload`

Uploads multiple PDFs.

---

## Process Documents

### POST `/process`

Processes uploaded files:
- Extraction
- Cleaning
- Chunking
- Embedding
- Storage

---

## Ask Questions

### POST `/ask`

Returns:
- Answer
- Source references

---

# 🔍 Example Questions

Try asking:

- What is this document about?
- What is NAIRP?
- What are the key recommendations?
- What budget is proposed?
- How can this help AI research?

---

# ⚠️ Challenges Faced

During development, the following real-world issues were handled:

### 1. LangChain Import Changes
Updated imports due to package restructuring.

### 2. OpenAI API Quota Limits
Switched to local HuggingFace embeddings.

### 3. Retrieval API Changes
Updated deprecated methods to newer interfaces.

### 4. Frontend–Backend Integration
Handled CORS and API communication.

### 5. Model Limitations
Used lightweight local models for cost-efficient inference.

---

# 📈 Future Improvements

- Upgrade to production LLMs
- Add reranking models
- Deploy on cloud
- Add authentication
- Support DOCX, TXT, CSV

---

# 💼 Resume Highlights

This project demonstrates:

- AI system design
- Retrieval-Augmented Generation
- Semantic search
- Backend API engineering
- Frontend integration
- Production-style debugging

