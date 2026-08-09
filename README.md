# Visual Memory Agent
An offline, self-hosted AI agent that uses CLIP and Llama 3.1 to semantically search your local image files.

### Tech Stack
*   **Agent:** Llama 3.1 via Ollama
*   **Vision:** OpenAI CLIP (ViT-base)
*   **Database:** FAISS (Vector Index)
*   **Backend:** FastAPI
*   **Frontend:** Streamlit (Custom Pixel-Art UI)

### How to Run
1. Ensure [Ollama](https://ollama.com) is installed and running on your system.
2. Download the model: `ollama run llama3.1`
3. Run `launchapp.bat`.
4. The first time you run it, it will automatically set up the environment and install dependencies.