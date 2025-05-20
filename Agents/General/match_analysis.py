'''
Historical Match analysis agent (in order to do in depth analysis of specific match and player performances)
Has access to tools:
    1. Web search
    2. News API endpoints
    3. Score card fetcher
    4. commentary fetcher
    5. expert analysis fetcher
'''

from ..general_tools import web_search, run_rag_workflow

import os
import dotenv
dotenv.load_dotenv()

from llama_index.core.agent.workflow import ReActAgent
from llama_index.llms.gemini import Gemini
from llama_index.core import Settings
from llama_index.core.tools import FunctionTool

from ..consts import MATCH_ANALYSIS_AGENT_SYS_PROMPT

GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]
Settings.llm = Gemini(model="models/gemini-2.0-flash", api_key=GOOGLE_API_KEY)

def fetch_news():
    return

def fetch_score_card():
    return

def fetch_commentary():
    return

def fetch_experts_analysis():
    return


tools = [
    FunctionTool.from_defaults(
        name="",
        fn=web_search,
        description=""
    ),
    FunctionTool.from_defaults(
        name="",
        fn=fetch_news,
        description=""
    ),
    FunctionTool.from_defaults(
        name="",
        fn=fetch_score_card,
        description=""
    ),
    FunctionTool.from_defaults(
        name="",
        fn=fetch_commentary,
        description=""
    ),
    FunctionTool.from_defaults(
        name="",
        fn=fetch_experts_analysis,
        description=""
    ),

]

matchAnalysis_agent = ReActAgent(
    tools = tools,
    llm = Settings.llm,
    system_prompt = MATCH_ANALYSIS_AGENT_SYS_PROMPT
)