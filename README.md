# CampusHelp

CampusHelp is a retrieval-augmented generation (RAG) chatbot for answering questions about college rules, fees, and other academic documents. It retrieves relevant passages from the local document collection, sends only that context to Gemini, and displays the source filenames with each answer.

If the available documents do not contain enough information, CampusHelp returns a safe fallback instead of guessing.

## Features

- Streamlit web interface with login and chat
- Admin-only PDF and DOCX uploads
- Automatic text extraction, chunking, embedding, and vector storage
- Source-cited answers grounded in campus documents
- Fallback response for questions outside the knowledge base
- Local role-based demo authentication

## How It Works

1. An admin uploads a PDF or DOCX file from the web interface.
2. CampusHelp extracts and cleans the text, then splits it into overlapping chunks.
3. Sentence Transformers creates an embedding for each chunk and stores it in ChromaDB.
4. A user asks a question in the chat interface.
5. Relevant chunks are retrieved and provided as context to Gemini.
6. The answer and the source filenames are shown in the chat.

## Requirements

- Python 3.10 or newer
- A Google Gemini API key

## Installation

Clone or download the project, then create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the dependencies:

```powershell
pip install -r requirements.txt
```

Create a file named `.env` in the project root and add your Gemini API key:

```env
GOOGLE_API_KEY=your_api_key_here
```

You can create an API key at [Google AI Studio](https://aistudio.google.com/apikey).

## Running the App

Start the Streamlit interface from the project root:

```powershell
streamlit run app.py
```

Then open the local URL shown by Streamlit, usually `http://localhost:8501`.

### Demo Accounts

| Username | Password | Role | Access |
| --- | --- | --- | --- |
| `admin` | `admin123` | Admin | Upload documents and ask questions |
| `student` | `student123` | User | Ask questions |

These credentials are for local demonstration only. Accounts are stored in `data/users.json` with plain-text passwords and should be replaced before any production use.

## Adding Documents

Admins can upload `.pdf` and `.docx` files through the **Upload Documents** tab. Uploaded files are copied to `data/raw_docs/`, processed immediately, and added to the existing ChromaDB collection. Re-uploading a file with the same name replaces its older chunks.

For initial or batch ingestion, place PDF/DOCX files in `data/raw_docs/` and run:

```powershell
python src/ingest.py
python src/embed.py
```

The processed chunks are written to `data/processed/chunks.json`, and vectors are stored under `vectorstore/chroma_db/`.

## Testing the Query Pipeline

The sample query runner uses the real retrieval and generation pipeline. It requires a populated vector store and a valid `GOOGLE_API_KEY`:

```powershell
python tests/test_queries.py
```

The sample cases cover exam rules, fee information, and questions that should trigger the grounded fallback response.

## Project Structure

```text
CampusHelp/
├── app.py                  # Streamlit application
├── requirements.txt        # Python dependencies
├── data/
│   ├── users.json          # Local demo users and roles
│   ├── raw_docs/           # Uploaded or source PDF/DOCX files
│   └── processed/          # Extracted and chunked document data
├── src/
│   ├── auth.py             # Authentication and role checks
│   ├── embed.py            # Embedding model and ChromaDB operations
│   ├── generate.py         # Gemini answer generation
│   ├── ingest.py           # Document extraction and chunking
│   ├── pipeline.py         # Main user/admin workflow API
│   └── retrieve.py         # Similarity search
├── tests/
│   └── test_queries.py     # End-to-end sample query checks
└── vectorstore/
	└── chroma_db/          # Persistent local vector database
```

## Limitations

- This is a local student/demo project, not a production authentication system.
- Answers depend on the quality and coverage of the uploaded documents.
- Scanned PDFs without extractable text may not produce useful chunks.
- The first embedding-model use may download model files from Hugging Face.
- Gemini usage requires network access and may incur API costs depending on the account.
