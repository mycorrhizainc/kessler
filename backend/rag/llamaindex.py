from llama_index.core.llms import ChatMessage
import logging
import sys
import os

import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from typing import List, Dict, Tuple, Optional

# Import the FileModel from file.py
from models.files import FileModel, provide_files_repo

from llama_index.core import StorageContext
from llama_index.core import VectorStoreIndex
from llama_index.core import Settings
from llama_index.vector_stores.lancedb import LanceDBVectorStore

from llama_index.core.node_parser import SentenceSplitter

# from llama_index.vector_stores.postgres import PGVectorStore
# import psycopg2
import textwrap
import openai
from llama_index.llms.groq import Groq


from sqlalchemy import make_url
from llama_index.core.response_synthesizers import CompactAndRefine
from llama_index.core.retrievers import QueryFusionRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.vector_stores import VectorStoreQuery
from llama_index.embeddings.openai import OpenAIEmbedding


from llama_index.core import Document


logger = logging.getLogger()


logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stderr)


# Uncomment to see debug logs
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))


GROQ_API_KEY = os.environ["GROQ_API_KEY"]
Settings.llm = Groq(
    model="llama3-70b-8192", request_timeout=360.0, api_key=GROQ_API_KEY
)

openai.api_key = os.environ["OPENAI_API_KEY"]
# TODO : Change embedding model to use not openai.
# Settings.embed_model = OllamaEmbedding(model_name="nomic-embed-text")

connection_string_unknown = os.environ["DATABASE_CONNECTION_STRING"]

# FIXME : Go ahead and try to figure out how to get this to work asynchronously assuming that is an important thing to do.
if "postgresql+asyncpg://" in connection_string_unknown:
    sync_postgres_connection_string = connection_string_unknown.replace(
        "postgresql+asyncpg://", "postgresql://"
    )
else:
    sync_postgres_connection_string = connection_string_unknown

async_postgres_connection_string = sync_postgres_connection_string.replace(
    "postgresql://", "postgresql+asyncpg://"
)


db_name = "postgres"
vec_table_name = "demo_vectordb"
file_table_name = "file"


url = make_url(sync_postgres_connection_string)

hybrid_vector_store = LanceDBVectorStore(
    uri="/tmp/lancedb", mode="overwrite", query_type="hybrid"
)
storage_context = StorageContext.from_defaults(vector_store=hybrid_vector_store)
# initial_documents = asyncio.run(get_document_list_from_file())
# initial_documents = await get_document_list_from_file()

# hybrid_index = VectorStoreIndex.from_documents(example_documents + initial_documents, storage_context=storage_context)
hybrid_index = VectorStoreIndex.from_vector_store(vector_store=hybrid_vector_store)

vector_retriever = hybrid_index.as_retriever(
    vector_store_query_mode="default",
    similarity_top_k=5,
)
text_retriever = hybrid_index.as_retriever(
    vector_store_query_mode="sparse",
    similarity_top_k=5,  # interchangeable with sparse_top_k in this context
)
retriever = QueryFusionRetriever(
    [vector_retriever, text_retriever],
    similarity_top_k=5,
    num_queries=1,  # set this to 1 to disable query generation
    mode="relative_score",
    use_async=False,
)

response_synthesizer = CompactAndRefine()
query_engine = RetrieverQueryEngine(
    retriever=retriever,
    response_synthesizer=response_synthesizer,
)


def get_nodes_from_query(query: str) -> List[str]:
    query_embeded = OpenAIEmbedding(api_key=openai.api_key).get_query_embedding(query)

    vs_query = VectorStoreQuery(
        query_embeding=query_embeded, query_str=query, similarity_top_k=10
    )
    result = hybrid_vector_store.query(vs_query)
    return result.nodes


def get_all_nodes() -> List:
    return hybrid_vector_store.from_table("vectors").get_nodes()


async def get_document_list_from_file_table() -> list:
    async def query_file_table_for_all_rows() -> List[Tuple[str, dict]]:
        # Create an async engine and session
        engine = create_async_engine(async_postgres_connection_string, echo=True)
        async_session_maker = sessionmaker(
            engine, expire_on_commit=False, class_=AsyncSession
        )

        async with async_session_maker() as session:
            # Create a query to select all rows
            stmt = session.select(FileModel)
            result = await session.execute(stmt)
            file_rows = result.scalars().all()

            documents = []
            for file_row in file_rows:
                if file_row.english_text is not None and isinstance(
                    file_row.doc_metadata, dict
                ):
                    documents.append((file_row.english_text, file_row.doc_metadata))

            return documents

    documents = await query_file_table_for_all_rows()
    document_list = []
    for english_text, doc_metadata in documents:
        if english_text is not None:
            additional_document = Document(text=english_text, metadata=doc_metadata)
            additional_document.doc_id = str(doc_metadata.get("hash"))
            document_list.append(document_list)
    return document_list


def add_document_to_db(doc: Document) -> None:
    # split the document into sentences
    parser = SentenceSplitter()
    nodes = parser.get_nodes_from_documents([doc])
    hybrid_index.insert_nodes(nodes)


def add_document_to_db_from_text(text: str, metadata: Optional[dict] = None) -> None:
    if metadata is None:
        metadata = {}
    document = Document(text=text, metadata=metadata)
    add_document_to_db(document)
    return


async def add_document_to_db_from_hash(hash_str: str) -> None:
    async def query_file_table_for_hash(hash: str) -> Tuple[any, any]:
        # Create an async engine and session
        engine = create_async_engine(async_postgres_connection_string, echo=True)
        async_session_maker = sessionmaker(
            engine, expire_on_commit=False, class_=AsyncSession
        )

        async with async_session_maker() as session:
            # Create a query to select the first row matching the given id
            stmt = session.select(FileModel).where(FileModel.hash == hash)
            result = await session.execute(stmt)
            file_row = result.scalars().first()

            if file_row:
                english_text = file_row.english_text
                document_metadata = file_row.doc_metadata
            else:
                english_text = None
                document_metadata = None

            return (english_text, document_metadata)

    return_tuple = await query_file_table_for_hash(hash_str)
    english_text = return_tuple[0]
    doc_metadata = return_tuple[1]
    if english_text is not None:
        assert isinstance(english_text, str)
        assert isinstance(doc_metadata, dict)
        # TODO : Add support for metadata filtering
        additional_document = Document(text=english_text, metadata=doc_metadata)
        additional_document.doc_id = str(hash)
        # FIXME : Make sure the UUID matches the other function, and dryify this entire fucking mess.
        add_document_to_db(additional_document)
    else:
        assert False, "English text not present for document."
    return None


async def regenerate_vector_database_from_file_table() -> None:
    document_list = await get_document_list_from_file_table()
    # TODO : Try to get this to set the global VAR
    global hybrid_index
    hybrid_index = VectorStoreIndex.from_documents(
        document_list, storage_context=storage_context
    )


def create_rag_response_from_query(query: str):
    return str(query_engine.query(query))


# Chat engine for rag


def sanitzie_chathistory_llamaindex(chat_history: List[dict]) -> List[ChatMessage]:
    def sanitize_message(raw_message: dict) -> ChatMessage:
        return ChatMessage(role=raw_message["role"], content=raw_message["content"])

    return list(map(sanitize_message, chat_history))


def generate_chat_completion(chat_history: List[dict]) -> dict:
    llama_index_chat_history = sanitzie_chathistory_llamaindex(chat_history)
    chat_engine = hybrid_index.as_chat_engine(
        chat_mode="react", verbose=True, chat_history=llama_index_chat_history
    )
    response = chat_engine.chat("")
    response_str = str(response)
    chat_engine.reset()
    return {"role": "assistant", "content": response_str}
