# 🦅 The Greene Advisor

A strategic, RAG-enabled AI advisor that adopts the writing style, philosophy, and analytical tone of author **Robert Greene**. Tailored for high-stakes decision-making, power dynamics, and Machiavellian strategy.

## 🏛 Architecture & Tech Stack

- **Frontend**: [Streamlit](https://streamlit.io/) with a premium, minimalist custom CSS theme.
- **Orchestration**: [LangChain](https://www.langchain.com/) for RAG pipeline and routing.
- **Intelligence**: [Groq](https://groq.com/) (Llama-3.3-70b-Versatile) for low-latency, high-reasoning strategic output.
- **Knowledge Base**: [ChromaDB](https://www.trychroma.com/) (Vector Store) with `all-MiniLM-L6-v2` HuggingFace Embeddings.
- **Persistence**: Local JSON-based session history tracking with dynamic topic generation.
- **Containerization**: [Podman](https://podman.io/) on **RHEL (Red Hat Enterprise Linux)**.

## 🚀 Key Features

- **The Librarian (Dynamic Router)**: Automatically analyzes user intent to filter the search context towards specific Robert Greene books (e.g., *48 Laws of Power*, *33 Strategies of War*).
- **The Protégé Profile**: A dynamic identity text area in the sidebar that allows the advisor to tailor its Machiavellian advice to your specific background and ultimate trajectory.
- **Persistent Strategems**: Chat sessions are automatically summarized into punchy titles and saved to the `History/` directory for recall across sessions.
- **Premium Interface**: A "Greene" aesthetic with custom typography (Outfit), a white sidebar, and a seamless visual experience.

## 🛠 Deployment (Podman on RHEL)

The project is designed to run in a containerized environment using Podman on RHEL (ubi-minimal base image).

### 1. Environment Configuration
Create a `.env` file in the root directory:
```bash
GROQ_API_KEY=your_api_key_here
```

### 2. Build the Image
```bash
podman build -t greene-advisor .
```

### 3. Run the Container
```bash
podman run -d \
  --name advisor-app \
  -p 8501:8501 \
  -v ./ChromaDB:/app/ChromaDB:Z \
  -v ./History:/app/History:Z \
  --env-file .env \
  greene-advisor
```
*Note: The `:Z` flag is used for SELinux relabeling on RHEL systems.*

## 📂 Project Structure

- `app.py`: Main application logic, UI, and RAG chain.
- `Containerfile`: RHEL-based container configuration.
- `ChromaDB/`: Persistent vector store directory.
- `History/`: Stored strategic session history (JSON).
- `Data/`: Source context library (EPUBs/Text).
- `assets/`: UI branding assets (Logo).

## ⚖ License
"Proceed with absolute truth." 
*This project is for strategic analysis and educational purposes based on the works of Robert Greene.*
