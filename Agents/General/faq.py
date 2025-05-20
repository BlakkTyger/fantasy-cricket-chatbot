'''
Answers FAQs related to platforms and rules.
Has access to tools:
    1. Web Search
    2. RAG over FAQ and Rules documents
'''

import os
import dotenv
dotenv.load_dotenv()

from ..general_tools import web_search, run_rag_workflow

from llama_index.core.agent.workflow import ReActAgent
from llama_index.llms.gemini import Gemini
from llama_index.core import Settings
from llama_index.core.tools import FunctionTool

from ..consts import FAQ_AGENT_SYS_PROMPT

def rag_over_FAQ():
    return

tools = [
    FunctionTool.from_defaults(
        name="",
        fn=web_search,
        description=""
    ),
    FunctionTool.from_defaults(
        name="",
        fn=rag_over_FAQ,
        description=""
    )
]

GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]
Settings.llm = Gemini(model="models/gemini-2.0-flash", api_key=GOOGLE_API_KEY)

faq_agent = ReActAgent(
    tools = tools,
    llm = Settings.llm,
    system_prompt = FAQ_AGENT_SYS_PROMPT
)