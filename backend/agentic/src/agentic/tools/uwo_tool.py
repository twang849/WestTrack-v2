from langchain.chat_models import init_chat_model
from langchain_openai import OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
import getpass
import os
import bs4
from langchain import hub
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import START, StateGraph
from typing_extensions import List, TypedDict
from langchain_chroma import Chroma
from typing import Callable, Literal
from typing_extensions import Annotated

from agentic.tools.base import BaseAgenticTool
from agentic.tools.utils.registry import (ConfigRequirement, Dependency,
                                          tool_registry)
from dotenv import load_dotenv
import os

load_dotenv()

@tool_registry.register(
    name="UWOTool",
    description="A tool to access information about the academic policies of Western University.",
    dependencies=[
        Dependency(
            name="langchain",
            version="0.3.25",
            type="pip",
        ),
        Dependency(
            name="langchain-openai",
            version="0.3.1",
            type="pip",
        ),
        Dependency(
            name="beautifulsoup4",
            version="4.12.2",
            type="pip",
        ),
        Dependency(
            name="langchain-core",
            version="0.3.59",
            type="pip",
        ),
        Dependency(
            name="langchain-text-splitters",
            version="0.3.8",
            type="pip",
        ),
        Dependency(
            name="langchain-community",
            version="0.3.19",
            type="pip",
        ),
        Dependency(
            name="langgraph",
            version="0.4.3",
            type="pip",
        ),
        Dependency(
            name="langchain-chroma",
            version="0.2.3",
            type="pip",
        ),
        Dependency(
            name="typing-extensions ",
            version="4.13.2",
            type="pip",
        ),
        
    ],  # Any pip packages your tool depends on
    config_requirements=[],  # Any required configuration settings
)

class Search(TypedDict):
    """Search query."""

    query: Annotated[str, ..., "Search query to run."]
    section: Annotated[
        Literal["beginning", "middle", "end"],
        ...,
        "Section to query.",
    ]

# Define state for application
class State(TypedDict):
    question: str
    query: Search
    context: List[Document]
    answer: str

class UWOTool(BaseAgenticTool):
    def get_tools(self) -> list[Callable]:
            """Return a list of functions that will be exposed to the agent."""
            return [
                self.queryDatabase
            ]
    
    def __init__(self):
        self.llm = init_chat_model("gpt-4o-mini", model_provider="openai")

        embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

        persist_directory = os.path.abspath("./chroma_langchain_db")

        self.vector_store = Chroma(
            collection_name="example_collection",
            embedding_function=embeddings,
            persist_directory=persist_directory,  # Where to save data locally, remove if not necessary
        )

        # Define prompt for question-answering
        self.prompt = hub.pull("rlm/rag-prompt")

        graph_builder = StateGraph(State).add_sequence([self.analyze_query, self.retrieve, self.generate])
        graph_builder.add_edge(START, "analyze_query")
        self.graph = graph_builder.compile()

    def analyze_query(self, state: State):
        structured_llm = self.llm.with_structured_output(Search)
        query = structured_llm.invoke(state["question"])
        return {"query": query}


    def retrieve(self, state: State):
        # import os
        # print(os.path.abspath("../../WestTrack/chroma_langchain_db"))

        query = state["query"]
        retrieved_docs = self.vector_store.similarity_search(
            query["query"],
        )
        return {"context": retrieved_docs}

    def generate(self, state: State):
        docs_content = "\n\n".join(doc.page_content for doc in state["context"])
        messages = self.prompt.invoke({"question": state["question"], "context": docs_content})
        response = self.llm.invoke(messages)
        return {"answer": response.content}

    def add_documents (self, list_of_links):
        loader = WebBaseLoader(
            web_paths=list_of_links,
            bs_kwargs=dict(
                parse_only=bs4.SoupStrainer(
                    id=("FullCategoryDiv")
                )
            ),
        )
        docs = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        all_splits = text_splitter.split_documents(docs)

        # Index chunks
        _ = self.vector_store.add_documents(documents=all_splits)

    def queryDatabase(self, query):
        """Function to query the vector database and retrieve semantically similar information.
        
        Args:
            query: The query to search the database for.
        """
        response = self.graph.invoke({"question": query})

        return response["answer"]

if __name__ == "__main__":
    obj = UWOTool()
    # obj.add_documents([
    #     "https://www.westerncalendar.uwo.ca/PolicyPages.cfm?PolicyCategoryID=1&command=showCategory&SelectedCalendar=Live&ArchiveID=",
    #     "https://www.westerncalendar.uwo.ca/PolicyPages.cfm?PolicyCategoryID=2&command=showCategory&SelectedCalendar=Live&ArchiveID=",
    #     "https://www.westerncalendar.uwo.ca/PolicyPages.cfm?PolicyCategoryID=3&command=showCategory&SelectedCalendar=Live&ArchiveID=",
    #     "https://www.westerncalendar.uwo.ca/PolicyPages.cfm?PolicyCategoryID=4&command=showCategory&SelectedCalendar=Live&ArchiveID=",
    #     "https://www.westerncalendar.uwo.ca/PolicyPages.cfm?PolicyCategoryID=5&command=showCategory&SelectedCalendar=Live&ArchiveID=",
    #     "https://www.westerncalendar.uwo.ca/PolicyPages.cfm?PolicyCategoryID=6&command=showCategory&SelectedCalendar=Live&ArchiveID="
    # ])

    print(obj.query("what are breadth requirements for undergrads at uwo"))