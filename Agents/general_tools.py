# contains the functions for web_search and RAG tools which will be used as tools of various agents 

#TODO Chunking
#TODO Modularization into: Chunking, Indexing, Retrieval
#TODO Explore Advanced RAG techniques

import os
import dotenv
import asyncio
from datetime import datetime
dotenv.load_dotenv('..')

from llama_index.core import (
    SimpleDirectoryReader,
    VectorStoreIndex,
    StorageContext,
    load_index_from_storage
)
from llama_index.core.agent.react import ReActAgent
from llama_index.core.workflow import (
    step,
    Context,
    Workflow,
    Event,
    StartEvent,
    StopEvent
)
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.chat_engine import SimpleChatEngine
from llama_index.core import Settings

from llama_index.postprocessor.cohere_rerank import CohereRerank

from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from google.genai.types import EmbedContentConfig
from llama_index.llms.google_genai import GoogleGenAI

from llama_index.utils.workflow import draw_all_possible_flows

from tavily import TavilyClient

GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]
COHERE_API_KEY = os.environ["COHERE_API_KEY"]
TAVILY_API_KEY = os.environ["TAVILY_API_KEY"]

Settings.embed_model = embedding_model = embed_model = GoogleGenAIEmbedding(
    model_name="text-embedding-004",
    embed_batch_size=100,
    api_key=GOOGLE_API_KEY
)
Settings.llm = GoogleGenAI(
    model="gemini-2.0-flash",
    api_key=GOOGLE_API_KEY
)

def web_search(query: str) -> dict:
    """
    Perform a web search to gather additional information.

    Args:
        query (str): The search query string.

    Returns:
        dict: A dictionary containing the search results with keys: 'title', 'url', 'content', 'score', 'raw_content'
    """

    tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
    response = tavily_client.search(query)
    return response['results']

# Event classes
class JudgeEvent(Event):
    query: str

class BadQueryEvent(Event):
    query: str

class ParallelRAGEvent(Event):
    query: str

class ResponseEvent(Event):
    query: str
    response: str
    source: str

class SummarizeEvent(Event):
    query: str
    response: str

class ComplicatedWorkflow(Workflow):
    def __init__(self, directory_path, persist_dir, *args, **kwargs):
        self.directory_path = directory_path
        self.persist_dir = persist_dir
        self.final_result = None  # To store the final output
        super().__init__(*args, **kwargs)

    def load_or_create_index(self, directory_path, persist_dir):
        embedding_model = GoogleGenAIEmbedding(
                            model_name="text-embedding-004",
                            embed_batch_size=100,
                            api_key=GOOGLE_API_KEY
                        )
        
        if os.path.exists(persist_dir):
            print("Loading existing index...")
            storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
            index = load_index_from_storage(storage_context)
        else:
            print("Creating new index...")
            documents = SimpleDirectoryReader(directory_path).load_data()
            
            index = VectorStoreIndex.from_documents(
                documents, 
                embed_model=embedding_model
            )
            
            index.storage_context.persist(persist_dir=persist_dir)
        
        return index

    @step(pass_context=True)
    async def judge_query(self, ctx: Context, ev: StartEvent | JudgeEvent) -> BadQueryEvent | ParallelRAGEvent:
        if not hasattr(ctx.data, "llm"):
            llm = GoogleGenAI(
                        model="gemini-2.0-flash",
                        api_key=GOOGLE_API_KEY
                    )
            ctx.data["llm"] = llm
            print(os.path.abspath(self.directory_path))
            print(os.path.abspath(self.persist_dir))
            ctx.data["index"] = self.load_or_create_index(
                self.directory_path,
                self.persist_dir
            )
            ctx.data["judge"] = SimpleChatEngine.from_defaults(
                llm=llm,
                embed_model=GoogleGenAIEmbedding(
                            model_name="text-embedding-004",
                            embed_batch_size=100,
                            api_key=GOOGLE_API_KEY
                        )
            )

        response = ctx.data["judge"].chat(f"""
            Given a user query, determine if this is likely to yield good results from a RAG system as-is. If it's good, return 'good', if it's bad, return 'bad'.
            Good queries use a lot of relevant keywords and are detailed. Bad queries are vague or ambiguous.

            Here is the query: {ev.query}
            """)
        if response == "bad":
            return BadQueryEvent(query=ev.query)
        else:
            return ParallelRAGEvent(query=ev.query)

    @step(pass_context=True)
    async def improve_query(self, ctx: Context, ev: BadQueryEvent) -> JudgeEvent:
        response = ctx.data["llm"].complete(f"""
            This is a query to a RAG system: {ev.query}

            The query is bad because it is too vague. Please provide a more detailed query that includes specific keywords and removes any ambiguity.
        """)
        return JudgeEvent(query=str(response))

    async def _naive_rag(self, index, query, embed_model):
        engine = index.as_query_engine(
            similarity_top_k=5,
            embed_model=embed_model
        )
        response = await engine.aquery(query)
        print("Naive response:", response)
        return ResponseEvent(query=query, source="Naive", response=str(response))

    async def _high_top_k(self, index, query, embed_model):
        engine = index.as_query_engine(
            similarity_top_k=20,
            embed_model=embed_model
        )
        response = await engine.aquery(query)
        print("High top k response:", response)
        return ResponseEvent(query=query, source="High top k", response=str(response))

    async def _rerank(self, index, query, embed_model):
        reranker = CohereRerank(api_key=COHERE_API_KEY, top_n=5)
        
        retriever = index.as_retriever(
            similarity_top_k=20,
            embed_model=embed_model
        )
        
        engine = RetrieverQueryEngine.from_args(
            retriever=retriever,
            node_postprocessors=[reranker],
        )

        response = await engine.aquery(query)
        print("Reranker response:", response)
        return ResponseEvent(query=query, source="Reranker", response=str(response))

    @step(pass_context=True)
    async def parallel_rag(self, ctx: Context, ev: ParallelRAGEvent) -> ResponseEvent:
        index = ctx.data["index"]
        embed_model = GoogleGenAIEmbedding(
                            model_name="text-embedding-004",
                            embed_batch_size=100,
                            api_key=GOOGLE_API_KEY
                        )
        
        # Run all three strategies in parallel
        responses = await asyncio.gather(
            self._naive_rag(index, ev.query, embed_model),
            self._high_top_k(index, ev.query, embed_model),
            self._rerank(index, ev.query, embed_model)
        )
        
        # Send all responses to be judged
        for response in responses:
            self.send_event(response)
        
        # Return None as we don't want to trigger the judge step directly
        return None

    @step(pass_context=True)
    async def judge(self, ctx: Context, ev: ResponseEvent) -> StopEvent:
        ready = ctx.collect_events(ev, [ResponseEvent]*3)
        if ready is None:
            return None

        response = ctx.data["judge"].chat(f"""
            A user has provided a query and 3 different strategies have been used
            to try to answer the query. Your job is to decide which strategy best
            answered the query. The query was: {ev.query}

            Response 1 ({ready[0].source}): {ready[0].response}
            Response 2 ({ready[1].source}): {ready[1].response}
            Response 3 ({ready[2].source}): {ready[2].response}

            Please provide the number of the best response (1, 2, or 3).
            Just provide the number, with no other text or preamble.
        """)

        best_response = int(str(response))
        print(f"Best response was number {best_response}, which was from {ready[best_response-1].source}")
        
        # Store the final result in the instance variable
        self.final_result = str(ready[best_response-1].response)
        
        return StopEvent(result=self.final_result)
    
    # New method to get the final result
    def get_result(self):
        """
        Returns the final result after the workflow has completed.
        """
        return self.final_result

async def run_rag_workflow(user_query, directory_path):
    persist_dir = f"../Embeddings/{directory_path.split("/Data/")[-1]}"
    print(f"persist directort: {persist_dir}")
    workflow = ComplicatedWorkflow(timeout=60,
                verbose=True,
                directory_path = directory_path,
                persist_dir = persist_dir
            )
    
    final_result = await workflow.run(query = user_query)

    return final_result

if __name__ == '__main__':
    import warnings
    warnings.filterwarnings('ignore')
    query = "The directory has two resumes. Analyze Each resume and predict who has a higer chance of getting into a software development intern role at google? Give a definitive answer after thourough analysis with explanation"
    direc = "../Data/Test"
    result = asyncio.run(run_rag_workflow(query, direc))
    print(result)