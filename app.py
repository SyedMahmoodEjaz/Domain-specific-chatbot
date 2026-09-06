import logging
import os

import dashscope
import gradio as gr
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("sme_assistant")

# ---- Config from environment ----
API_KEY = os.getenv("DASHSCOPE_API_KEY")
BASE_URL = os.getenv("MODEL_STUDIO_BASE_URL", "https://dashscope-intl.aliyuncs.com/api/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "qwen-max")
KNOWLEDGE_FILE = os.getenv("KNOWLEDGE_FILE", "academy.txt")
SHARE_GRADIO = os.getenv("SHARE_GRADIO", "false").lower() == "true"
SERVER_PORT = int(os.getenv("PORT", "7860"))

if not API_KEY:
    raise ValueError("DASHSCOPE_API_KEY is missing from .env")

dashscope.api_key = API_KEY
dashscope.base_http_api_url = BASE_URL

ASSISTANT_NAME = "S.M.E"
OWNER_NAME = "Syed Mahmood Ejaz"

SYSTEM_PROMPT = (
    f'You are a personal assistant for {OWNER_NAME}, named "{ASSISTANT_NAME}". '
    f"Your expertise is to provide information about {OWNER_NAME}. "
    "You do not provide information outside of this scope. If a question is not "
    'about them, respond with, "I can\'t assist you with that, sorry!"'
)


def load_knowledge_base() -> str:
    """Load the scraped knowledge text the assistant answers from."""
    if not os.path.exists(KNOWLEDGE_FILE):
        logger.warning(
            "%s not found. Run scrape_data.py first, or the assistant "
            "will have no information to answer from.",
            KNOWLEDGE_FILE,
        )
        return ""

    with open(KNOWLEDGE_FILE, "r", encoding="utf-8") as file:
        content = file.read().strip()

    if not content:
        logger.warning(
            "%s is empty. Run scrape_data.py to populate it before "
            "expecting useful answers.",
            KNOWLEDGE_FILE,
        )

    return content


def build_prompt_template(knowledge: str) -> str:
    return knowledge + f"""
    You are my personal assistant, named "{OWNER_NAME}".
    Your expertise is exclusively in providing information about me from the
    links I have given (portfolio and LinkedIn). When someone asks about me,
    tell them about {OWNER_NAME}.
    You do not provide information outside of this scope. If a question is not
    about {OWNER_NAME}, respond with, "I can't assist you with that, sorry!"
    Users may refer to me as SME, Syed, Mahmood, Ejaz, or {OWNER_NAME} -- treat
    all of these as referring to the same person.
    Question: {{question}}
    Answer:
    """


def generate_response(question: str, template: str) -> str:
    full_prompt = template.format(question=question)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": full_prompt},
    ]

    try:
        response = dashscope.Generation.call(
            MODEL_NAME,
            messages=messages,
            result_format="message",
            stream=False,
            incremental_output=False,
        )
    except Exception:
        logger.exception("Error calling DashScope API")
        return "Sorry, something went wrong while contacting the AI service. Please try again."

    if response.get("status_code") == 200:
        return response["output"]["choices"][0]["message"]["content"]

    logger.error(
        "DashScope API error %s: %s",
        response.get("status_code"),
        response.get("message"),
    )
    return "Sorry, the AI service returned an error. Please try again."


def ask_sme_question(question: str) -> str:
    question = (question or "").strip()

    if not question:
        return "Please enter a question."

    knowledge = load_knowledge_base()

    if not knowledge:
        return (
            "I don't have any information loaded yet. "
            "Please run scrape_data.py to build the knowledge base first."
        )

    template = build_prompt_template(knowledge)
    return generate_response(question, template)


iface = gr.Interface(
    fn=ask_sme_question,
    inputs="text",
    outputs="text",
    title="My Personal Assistant",
    description="Ask anything about me and I will assist you.",
)

if __name__ == "__main__":
    iface.launch(server_port=SERVER_PORT, share=SHARE_GRADIO)
