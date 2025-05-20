'''
Answers FAQs related to platforms and rules.
Has access to tools:
    1. Web Search
    2. RAG over FAQ and Rules documents
'''

import os
import asyncio
import dotenv
dotenv.load_dotenv()

from ..general_tools import web_search, run_rag_workflow

from llama_index.core.agent.workflow import ReActAgent
from llama_index.llms.gemini import Gemini
from llama_index.core import Settings
from llama_index.core.tools import FunctionTool

from ..consts import FAQ_AGENT_SYS_PROMPT

async def rag_over_FAQ(query: str) -> str:
    result = asyncio.run(run_rag_workflow(query, "Data/FAQ"))
    return result

tools = [
    FunctionTool.from_defaults(
        name="Web Search Tool",
        fn=web_search,
        description="Search the internet for answers for the queries related to fantasy cricket platforms"
    ),
    FunctionTool.from_defaults(
        name="Rules and Regulations Documents Search",
        fn=rag_over_FAQ,
        description="Search through the Rules and Regulations Documents of various fantasy cricket websites"
    )
]

GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]
Settings.llm = Gemini(model="models/gemini-2.0-flash", api_key=GOOGLE_API_KEY)

faq_agent = ReActAgent(
    tools = tools,
    llm = Settings.llm,
    system_prompt = FAQ_AGENT_SYS_PROMPT
)