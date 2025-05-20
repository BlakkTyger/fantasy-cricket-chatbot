'''
Team Selector Agent.
Has access to the following tools:
    1. Team Builder Ensemble: Black Box Machine Learning ensemble for selecting best 11 out of 22
    2. Player Data Fetch RAG: Fetching player data from a csv file
    3. Player Data Fetch Search: Search the internet for performance of player in specific conditions and in recent times
    4. Match Conditions Search: search about the match conditions like pitch quality, ground size, weather etc to have an in depth analysis
    5. Differential Pick Tool: Select differential picks.
'''

import os
import dotenv
dotenv.load_dotenv()

from llama_index.core.agent.workflow import ReActAgent
from llama_index.llms.gemini import Gemini
from llama_index.core import Settings
from llama_index.core.tools import FunctionTool

from ..consts import TEAM_SELECTOR_AGENT_SYS_PROMPT

GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]
Settings.llm = Gemini(model="models/gemini-2.0-flash", api_key=GOOGLE_API_KEY)

def team_builder():
    return

def fetch_player_data():
    return

def search_player_data():
    return

def search_match_conditions():
    return

def get_differential_pick():
    return

tools = [
    FunctionTool.from_defaults(
        name="",
        fn=team_builder,
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
        fn=search_match_conditions,
        description=""
    ),
    FunctionTool.from_defaults(
        name="",
        fn=get_differential_pick,
        description=""
    ),

]

teamSelector_agent = ReActAgent(
    tools = tools,
    llm = Settings.llm,
    system_prompt = TEAM_SELECTOR_AGENT_SYS_PROMPT
)