# orchestration for the general chatbot

import os
import dotenv
dotenv.load_dotenv()

from llama_index.core.agent.workflow import ReActAgent
from llama_index.core.workflow import Context
from llama_index.llms.gemini import Gemini
from llama_index.core import Settings
from llama_index.core.tools import BaseTool, FunctionTool
from .faq import faq_agent
from .match_analysis import matchAnalysis_agent
from .team_selector import teamSelector_agent
from ..consts import TEAM_SELECTOR_AGENT_DESC, FAQ_AGENT_DESC, MATCH_ANALYSIS_AGENT_DESC, GENERAL_AGENT_SYS_PROMPT

GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]
Settings.llm = Gemini(model="models/gemini-2.0-flash", api_key=GOOGLE_API_KEY)

def orchestrate(query):
    agent_output_to_tool = lambda x, description: FunctionTool.from_defaults(name = f"{x}", fn = x.chat(query).response, description = description)

    teamSelector_tool = agent_output_to_tool(teamSelector_agent, query, TEAM_SELECTOR_AGENT_DESC)
    faq_tool = agent_output_to_tool(faq_agent, query, FAQ_AGENT_DESC)
    matchAnalysis_tool = agent_output_to_tool(matchAnalysis_agent, query, MATCH_ANALYSIS_AGENT_DESC)

    tools = [teamSelector_tool, faq_tool, matchAnalysis_tool]

    main_agent = ReActAgent(
        tools = tools,
        llm = Settings.llm,
        system_prompt = GENERAL_AGENT_SYS_PROMPT
    )

    return main_agent.chat(query).response

if __name__ == "__main__":
    query = ""
    response = orchestrate(query)
    print(response)