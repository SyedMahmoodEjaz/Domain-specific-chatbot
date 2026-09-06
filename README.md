# S.M.E — Personal Domain-Specific Assistant

A personal AI assistant chatbot that answers questions **only about a specific person** (in this case, Syed Mahmood Ejaz), built by scraping that person's public portfolio and LinkedIn profile and feeding the text into a Qwen model via Alibaba Cloud's DashScope API. Served through a simple Gradio web interface.

If a question falls outside that scope, the assistant is instructed to politely decline rather than hallucinate an answer.

## How It Works

1. `scrape_data.py` visits a list of public URLs (portfolio site, LinkedIn profile), extracts the paragraph text from each, and saves it all into a single knowledge file (`academy.txt`).
2. `app.py` loads that file at question-time, wraps it in a prompt template instructing the model to act as the person's personal assistant and stay strictly in scope, and sends it to the Qwen model (`qwen-max` by default) through DashScope.
3. The Gradio interface (`iface.launch()`) exposes a simple text-in/text-out chat box in the browser.

## Getting Started

### Prerequisites

- Python 3.10+
- An Alibaba Cloud Model Studio / DashScope API key ([console](https://dashscope.console.aliyun.com/))

### Installation

1. **Clone the repo**
   ```bash
   git clone https://github.com/<your-username>/<your-repo-name>.git
   cd <your-repo-name>
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS/Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up your environment variables**
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` and add your `DASHSCOPE_API_KEY`.

5. **Build the knowledge base**

   Edit the `SOURCE_URLS` list in `scrape_data.py` to point at your own portfolio/profile pages, then run:
   ```bash
   python scrape_data.py
   ```
   This creates/updates `academy.txt`, which the assistant reads from at question-time.

   > ⚠️ **LinkedIn note:** LinkedIn blocks most automated/unauthenticated requests and returns a login page instead of your profile content. The script will warn you if this happens. If so, manually copy the relevant text from your profile into `academy.txt` (under a `===== SOURCE: ... =====` heading) instead of relying on the scraper for that page.

6. **Run the app**
   ```bash
   python app.py
   ```
   Gradio will print a local URL (default `http://127.0.0.1:7860`) to open in your browser.

## Configuration

All configuration lives in `.env` (see `.env.example`):

| Variable | Description | Default |
|---|---|---|
| `DASHSCOPE_API_KEY` | Your Model Studio / DashScope API key | *(required)* |
| `MODEL_STUDIO_BASE_URL` | DashScope API base URL | `https://dashscope-intl.aliyuncs.com/api/v1` |
| `MODEL_NAME` | Qwen model to use | `qwen-max` |
| `KNOWLEDGE_FILE` | Path to the scraped knowledge text file | `academy.txt` |
| `SHARE_GRADIO` | Set `true` to get a public `gradio.live` link | `false` |
| `PORT` | Local port Gradio serves on | `7860` |

## Project Structure

```
domain-specific-chatbot/
├── app.py               # Gradio app: loads knowledge base, calls DashScope, serves UI
├── scrape_data.py         # Scrapes source URLs into academy.txt
├── academy.txt             # Generated knowledge base (run scrape_data.py to create/update)
├── requirements.txt
├── .env.example              # Template for required environment variables
└── .gitignore
```

## Known Limitations / Roadmap

- **Full-text stuffing, not true RAG.** The entire contents of `academy.txt` are inserted into every prompt. This is simple and works fine for a small amount of personal info, but won't scale if the knowledge base grows large (you'll eventually hit context-length or cost issues). A proper retrieval-augmented-generation (RAG) setup — chunking the text, embedding it, and retrieving only the relevant chunks per question — would be the natural next step.
- **LinkedIn scraping is unreliable** due to LinkedIn's bot/login protections (see note above).
- **No conversation memory** — each question is answered independently; there's no multi-turn context.
- **No automated tests** currently.

Contributions and suggestions are welcome.

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
