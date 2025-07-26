
# RAG Pipeline Setup Guide

Follow these steps to set up and run your RAG pipeline.

## 📦 Step 1: Install Required Python Packages

Make sure you have a `requirements.txt` file in your project’s root directory.

```bash
pip install -r requirements.txt
```

This command installs all necessary packages listed in the file.

## 🔑 Step 2: Set Up Environment Variables

Create a `.env` file in your project root (or open if it already exists). Add your environment variables such as your Neon database url and any API keys.

Example Neon database connection string format:

```
DATABASE_URL=
# Example:
DATABASE_URL="postgresql://neondb_owner:your_password@ep-noisy-hall-12345.us-east-2.aws.neon.tech/neondb?sslmode=require"
```

Possible additional variables to include:

```
GOOGLE_API_KEY=your-openai-api-key
```

Replace placeholders with your actual credentials found in the Neon dashboard or relevant service.

## 🗄️ Step 3: Run the Database Initialization Script

Navigate to your root directory and run:

```bash
python3 db/main.py
```

This script sets up your database schema and tables. Make sure it completes successfully.

## 📚 Step 4: Run the RAG System Jupyter Notebook

If Jupyter is not installed, install it:

```bash
pip install notebook
```

Start Jupyter Notebook:

```bash
jupyter notebook
```

- A browser tab will open. Find and open `rag_system.ipynb`.
- Run all cells: Go to **Cell → Run All** in the menu.
- Ensure all cells execute successfully. This loads data, creates embeddings, and indexes your vector database.


## 🚀 Step 5: Run the FastAPI Application

In a new terminal window (keep Jupyter running if needed):

```bash
uvicorn app/main:app --reload
```

- `app/main:app` refers to the `app` instance inside `main.py`.
- `--reload` restarts the server automatically upon code changes.


## 🌐 Step 6: Access Your Application

- The app usually runs on: `http://127.0.0.1:8000` or `http://localhost:8000`.

Open your browser to that address to access your RAG interface or FastAPI docs.

**Your RAG pipeline is now fully operational!**

## 📚 Step 7: Explore the Applicatio (Demo)

image 1:
<img src="public/image1.png" alt="Logo" width="600"/>

image 2:
<img src="public/image2.png" alt="Logo" width="600"/>




# Alternative using curl commands:
"""
# Create a chunk
curl -X POST "http://localhost:8000/chunks/" \
     -H "Content-Type: application/json" \
     -d '{
       "chunk_id": 1,
       "source_file": "test.pdf",
       "chunk_text": "Sample text",
       "token_count": 5,
       "start_unit": 0,
       "end_unit": 11,
       "embedding_model": "ada-002",
       "embedding": "[0.1, 0.2]"
     }'

# Get all chunks
curl -X GET "http://localhost:8000/chunks/"

# Get specific chunk
curl -X GET "http://localhost:8000/chunks/{chunk-id}"

# Update chunk
curl -X PUT "http://localhost:8000/chunks/{chunk-id}" \
     -H "Content-Type: application/json" \
     -d '{"chunk_text": "Updated text"}'

# Delete chunk
curl -X DELETE "http://localhost:8000/chunks/{chunk-id}"
"""


