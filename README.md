# fantasy-cricket-chatbot
Helps cricket fans make smarter Fantasy Cricket decisions through an intelligent, conversational assistant. It is a chat-based interface that allows users to ask questions, get suggestions, and understand why certain players might be better picks—all in natural language.

### Approach
1. Statistical analysis (Numerical, non generative Machine Learning Models) for determining player performance for more deterministic and explanable results.
    - Team Decider
    - Differential Pick Algorithm
    - Player Comparison

2. In the statistical analysis code, store verbose on names, performace metrics etc when the model is running for explanability dataset (this is called deicison making verbose)

3. Explanability of player picks on the basis of RAG-based agentic chatbot (flow: RAG over Knowledge Base -> apppend final result and decision making verbose in prompt -> ask LLM to generate explanation based on reasoning)

4. Different Agentic workflows on the basis of different types of prompts
    - Statistical Analysis Tools (outlined in (1)) shall be used as tools/sub-agents in the workflow.
    - Knowledge base of rules, regulations, media articles and other related documents maintained. FAQ agent (simple RAG over docs) answers those questions
    - Stats Agent (has 2 tools: simple RAG over docs and CSV or SQL agent), extracts player stats from CSV, player descriptions from docs and does QnA on individual stats without predictive analysis
    - Decion making agent, on the basis of the prompt will decide tool calling sequence (TopoSort?), extract arguments for the functional tools from the query and then run the workflow (dynamic workflows)
    - [OPTIONAL] Match analysis agent: Based on live updates from an API, give analysis with predictions etc
    - [OPTIONAL] Community Chatrooms: Chatrooms with AI integrations (similar to MetaAI on whatsapp) 

5. Integration of live match updates: 
    - Which API to use and from where to extract data
    - Separate Data Buffer for live updates for better retrieval?

6. Datasets:
    - Organized in directories for tree traversal: efficient search

### Relevant Papers
- [Multi-Agentic Framework for Crafting Fantasy 11 Cricket Teams](arxiv.org/pdf/2410.01307)