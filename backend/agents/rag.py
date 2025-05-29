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
from typing import Literal
from typing_extensions import Annotated

os.environ["LANGSMITH_TRACING"] = "true"    
os.environ["LANGSMITH_API_KEY"] = "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"
os.environ["OPENAI_API_KEY"] = "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"

llm = init_chat_model("gpt-4o-mini", model_provider="openai")

embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

vector_store = Chroma(
    collection_name="example_collection",
    embedding_function=embeddings,
    persist_directory="./chroma_langchain_db",  # Where to save data locally, remove if not necessary
)

# loader = WebBaseLoader(
#     web_paths=("https://www.westerncalendar.uwo.ca/PolicyPages.cfm?PolicyCategoryID=4&command=showCategory&SelectedCalendar=Live&ArchiveID=",),
#     bs_kwargs=dict(
#         parse_only=bs4.SoupStrainer(
#             id=("FullCategoryDiv")
#         )
#     ),
# )
# docs = loader.load()

# text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
# all_splits = text_splitter.split_documents(docs)

# # Index chunks
# _ = vector_store.add_documents(documents=all_splits)

# Define prompt for question-answering
prompt = hub.pull("rlm/rag-prompt")

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


def analyze_query(state: State):
    structured_llm = llm.with_structured_output(Search)
    query = structured_llm.invoke(state["question"])
    return {"query": query}


def retrieve(state: State):
    query = state["query"]
    retrieved_docs = vector_store.similarity_search(
        query["query"],
    )
    return {"context": retrieved_docs}


def generate(state: State):
    docs_content = "\n\n".join(doc.page_content for doc in state["context"])
    messages = prompt.invoke({"question": state["question"], "context": docs_content})
    response = llm.invoke(messages)
    return {"answer": response.content}


graph_builder = StateGraph(State).add_sequence([analyze_query, retrieve, generate])
graph_builder.add_edge(START, "analyze_query")
graph = graph_builder.compile()

# response = graph.invoke({"question": "how many credits to graduate with a 4 year bachelor's degree?"})
# print(response["answer"])

# print(vector_store._collection.count())
# with open("agents/file.txt", "w") as file:
#     file.write(str(vector_store._collection.get()))

for step in graph.stream(
    {"question": "how many credits to graduate with a 4 year bachelor's degree?"},
    stream_mode="updates",
):
    print(f"{step}\n\n----------------\n")