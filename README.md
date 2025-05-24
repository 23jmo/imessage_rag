# iMessage Gift Insight App

This command-line Python application indexes iMessage conversations from the macOS `chat.db` SQLite database, filters them by contact, embeds and stores those messages in a vector database, and uses retrieval-augmented generation (RAG) to answer user-defined questions such as personalized gift suggestions.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and add your OpenAI API key.
3. Run the main script:
   ```bash
   python main.py --help
   ```

## Features

- iMessage access and filtering
- Embedding and vector storage
- RAG-based querying
- LLM integration (OpenAI)

See the PRD for full details.
