'''
- chatbot for the live match analysis interface
'''

import os
import dotenv
dotenv.load_dotenv()

from ..general_tools import web_search
from ..General.team_selector import fetch_player_data
from ..General.team_selector import search_player_data

from llama_index.core.agent.workflow import ReActAgent
from llama_index.llms.gemini import Gemini
from llama_index.core import Settings
from llama_index.core.tools import FunctionTool

from ..consts import FAQ_AGENT_SYS_PROMPT

GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]
Settings.llm = Gemini(model="models/gemini-2.0-flash", api_key=GOOGLE_API_KEY)

def fetch_recent_match_updates():
    return

def fetch_full_match_history():
    return

tools = [
    FunctionTool.from_defaults(
        name="",
        fn=web_search,
        description=""
    ),
    FunctionTool.from_defaults(
        name="",
        fn=fetch_player_data,
        description=""
    ),
    FunctionTool.from_defaults(
        name="",
        fn=search_player_data,
        description=""
    ),
    FunctionTool.from_defaults(
        name="",
        fn=fetch_recent_match_updates,
        description=""
    ),
    FunctionTool.from_defaults(
        name="",
        fn=fetch_full_match_history,
        description=""
    )
]

faq_agent = ReActAgent(
    tools = tools,
    llm = Settings.llm,
    system_prompt = FAQ_AGENT_SYS_PROMPT
)
