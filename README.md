# RepoPilot Demo

A lightweight Streamlit demo of **RepoPilot**, an AI-powered code repository assistant.

The main RepoPilot project is a full-stack application with separate frontend, backend, and AI services. This repository provides a simplified Streamlit version of the AI functionality for easy deployment and demonstration.

### 🚀 Live Demo: https://repopilotdemolink-cv6x5qntvafjxwd5ag8bzg.streamlit.app/


### 🛠️ Tech Stack

- Python
- Streamlit
- Mistral AI
- LangChain
- ChromaDB
- RAG

### 🧠 How It Works

Code is processed into chunks, converted into embeddings using Mistral, and stored locally in ChromaDB. User queries retrieve relevant code through semantic search, which is then used by the LLM to generate contextual responses.
