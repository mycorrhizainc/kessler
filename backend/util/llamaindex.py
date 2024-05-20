from haystack_integrations.document_stores.chroma import ChromaDocumentStore
from haystack_integrations.components.retrievers.chroma import ChromaEmbeddingRetriever
from haystack_integrations.components.retrievers.chroma import ChromaQueryTextRetriever
from haystack.components.converters import MarkdownToDocument
from haystack.components.embedders import OpenAIDocumentEmbedder
from haystack.components.retrievers.in_memory import InMemoryEmbeddingRetriever
from haystack.components.writers import DocumentWriter
from haystack.utils import Secret, deserialize_secrets_inplace
from haystack import Document, Pipeline, PredefinedPipeline

from sqlalchemy import select
from models.files import FileModel

from typing import Optional, List
from pathlib import Path
from uuid import UUID
from logging import getLogger
import os
from models.files import provide_files_repo, FileModel, FileRepository

from models.utils import sqlalchemy_config

logger = getLogger(__name__)


octo_ef = OpenAIDocumentEmbedder(
    api_key=Secret.from_env_var("OCTO_API_KEY"),
    model="thenlper/gte-large",
    api_base_url="https://text.octoai.run/v1/embeddings",
)

chroma_path = os.environ["CHROMA_PERSIST_PATH"]
chroma_store = ChromaDocumentStore(persist_path=chroma_path)
chroma_embedding_retriever = ChromaEmbeddingRetriever(document_store=chroma_store)
chroma_text_retriever = ChromaQueryTextRetriever(document_store=chroma_store)

chroma_pipeline = Pipeline()
chroma_pipeline.add_component("OpenAIDocumentEmbedder", octo_ef)
chroma_pipeline.add_component("writer", DocumentWriter(chroma_store))


async def indexDocByID(fid: UUID):
    # find file
    logger.info(f"INDEXER: indexing document with fid: {fid}")
    session_factory = sqlalchemy_config.create_session_maker()
    async with session_factory() as db_session:
        try:
            file_repo = FileRepository(session=db_session)
        except Exception as e:
            logger.error("unable to get file model repo", e)
        logger.info("created file repo")
        f = await file_repo.get(fid)
        logger.info(f"INDEXER: found file")
        # get
        docs = [Document(id=str(f.id), content=f.english_text, meta=f.doc_metadata)]

        try:
            f.stage = "indexing"
            await file_repo.update(f, auto_commit=True)
            indexing = Pipeline()
            indexing.add_component("writer", DocumentWriter(chroma_store))
            logger.info("indexing document")
            indexing.run({"writer": {"documents": docs}})
            logger.info("completed indexing ")
        except Exception as e:
            logger.critical(f"Failed to index document with id {fid}", e)
            raise e


async def get_indexed_by_id(fid: UUID):
    searching = Pipeline()
    querying = Pipeline()
    querying.add_component("retriever", ChromaQueryTextRetriever(chroma_store))
    results = querying.run({"retriever": {"query": f"id: str(fid)", "top_k": 3}})
    return results


async def indexDocByHash(hash: str):
    file_repo = FileModel.repo()
    stmt = select(FileModel).where(FileModel.hash == hash)
    f = file_repo.get(statement=stmt)


def query_chroma(query: str, top_k: int = 5):
    querying = Pipeline()
    querying.add_component("retriever", ChromaQueryTextRetriever(chroma_store))
    results = querying.run({"retriever": {"query": query, "top_k": top_k}})
    return results


import logging
import sys
import os

logger = logging.getLogger()


logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stderr)
""""
# Postgres Vector Store
In this notebook we are going to show how to use [Postgresql](https://www.postgresql.org) and  [pgvector](https://github.com/pgvector/pgvector)  to perform vector searches in LlamaIndex

If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
"""

"""Running the following cell will install Postgres with PGVector in Colab."""


# import logging
# import sys

# Uncomment to see debug logs
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

from llama_index.core import SimpleDirectoryReader, StorageContext
from llama_index.core import VectorStoreIndex
from llama_index.core import Settings
from llama_index.vector_stores.postgres import PGVectorStore
import textwrap
import openai
from llama_index.llms.groq import Groq

from llama_index.readers.database import DatabaseReader


GROQ_API_KEY = os.environ["GROQ_API_KEY"]
Settings.llm = Groq(
    model="llama3-70b-8192", request_timeout=360.0, api_key=GROQ_API_KEY
)

openai.api_key = os.environ["OPENAI_API_KEY"]
# TODO : Change embedding model to use not openai.
# Settings.embed_model = OllamaEmbedding(model_name="nomic-embed-text")
"""### Setup OpenAI
The first step is to configure the openai key. It will be used to created embeddings for the documents loaded into the index
"""

import os

# os.environ["OPENAI_API_KEY"] = "<your key>"

"""Download Data"""

# !mkdir -p 'data/paul_graham/'
# !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'

"""### Loading documents
Load the documents stored in the `data/paul_graham/` using the SimpleDirectoryReader
"""

documents = SimpleDirectoryReader(datadir).load_data()
logger.info("Document ID:", documents[0].doc_id)

"""### Create the Database
Using an existing postgres running at localhost, create the database we'll be using.
"""

import psycopg2

connection_string = os.environ["DATABASE_CONNECTION_STRING"]

# FIXME : Go ahead and try to figure out how to get this to work asynchronously assuming that is an important thing to do.
if "postgresql+asyncpg://" in connection_string:
    postgres_connection_string = connection_string.replace(
        "postgresql+asyncpg://", "postgresql://"
    )

db_name = "postgres"
vec_table_name = "vector_db"
file_table_name = "file"


conn = psycopg2.connect(connection_string)
conn.autocommit = True


"""### Hybrid Search

To enable hybrid search, you need to:
1. pass in `hybrid_search=True` when constructing the `PGVectorStore` (and optionally configure `text_search_config` with the desired language)
2. pass in `vector_store_query_mode="hybrid"` when constructing the query engine (this config is passed to the retriever under the hood). You can also optionally set the `sparse_top_k` to configure how many results we should obtain from sparse text search (default is using the same value as `similarity_top_k`).
"""

from sqlalchemy import make_url

url = make_url(connection_string)


reader = DatabaseReader(
    dbname=db_name,
    host=url.host,
    password=url.password,
    port=url.port,
    user=url.username,
)


hybrid_vector_store = PGVectorStore.from_params(
    database=db_name,
    host=url.host,
    password=url.password,
    port=url.port,
    user=url.username,
    table_name=vec_table_name,
    embed_dim=1536,  # openai embedding dimension
    hybrid_search=True,
    text_search_config="english",
)


def add_document_to_db_from_uuid(uuid_str: str) -> None:
    query = f"SELECT english_text FROM file WHERE document_id = '{uuid_str}';"
    documents = reader.load_data(query=query)


storage_context = StorageContext.from_defaults(vector_store=hybrid_vector_store)
hybrid_index = VectorStoreIndex.from_documents(
    documents, storage_context=storage_context
)

hybrid_query_engine = hybrid_index.as_query_engine(
    vector_store_query_mode="hybrid", sparse_top_k=2
)
hybrid_response = hybrid_query_engine.query(
    "Who does Paul Graham think of with the word schtick"
)

logger.info(hybrid_response)

"""#### Improving hybrid search with QueryFusionRetriever

Since the scores for text search and vector search are calculated differently, the nodes that were found only by text search will have a much lower score.

You can often improve hybrid search performance by using `QueryFusionRetriever`, which makes better use of the mutual information to rank the nodes.
"""

from llama_index.core.response_synthesizers import CompactAndRefine
from llama_index.core.retrievers import QueryFusionRetriever
from llama_index.core.query_engine import RetrieverQueryEngine

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

response = query_engine.query(
    "Who does Paul Graham think of with the word schtick, and why?"
)
logger.info(response)

"""### Metadata filters

PGVectorStore supports storing metadata in nodes, and filtering based on that metadata during the retrieval step.

#### Download git commits dataset
"""

# !mkdir -p 'data/git_commits/'
# !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/csv/commit_history.csv' -O 'data/git_commits/commit_history.csv'

# import csv
#
# with open("data/git_commits/commit_history.csv", "r") as f:
#     commits = list(csv.DictReader(f))
#
# logger.info(commits[0])
# logger.info(len(commits))
#
# """#### Add nodes with custom metadata"""
#
# # Create TextNode for each of the first 100 commits
# from llama_index.core.schema import TextNode
# from datetime import datetime
# import re
#
# nodes = []
# dates = set()
# authors = set()
# for commit in commits[:100]:
#     author_email = commit["author"].split("<")[1][:-1]
#     commit_date = datetime.strptime(
#         commit["date"], "%a %b %d %H:%M:%S %Y %z"
#     ).strftime("%Y-%m-%d")
#     commit_text = commit["change summary"]
#     if commit["change details"]:
#         commit_text += "\n\n" + commit["change details"]
#     fixes = re.findall(r"#(\d+)", commit_text, re.IGNORECASE)
#     nodes.append(
#         TextNode(
#             text=commit_text,
#             metadata={
#                 "commit_date": commit_date,
#                 "author": author_email,
#                 "fixes": fixes,
#             },
#         )
#     )
#     dates.add(commit_date)
#     authors.add(author_email)
#
# logger.info(nodes[0])
# logger.info(min(dates), "to", max(dates))
# logger.info(authors)
#
# vector_store = PGVectorStore.from_params(
#     database=db_name,
#     host=url.host,
#     password=url.password,
#     port=url.port,
#     user=url.username,
#     table_name="metadata_filter_demo3",
#     embed_dim=1536,  # openai embedding dimension
# )
#
# index = VectorStoreIndex.from_vector_store(vector_store=vector_store)
# index.insert_nodes(nodes)
#
# logger.info(index.as_query_engine().query("How did Lakshmi fix the segfault?"))
#
# """#### Apply metadata filters
#
# Now we can filter by commit author or by date when retrieving nodes.
# """
#
# from llama_index.core.vector_stores.types import (
#     MetadataFilter,
#     MetadataFilters,
# )
#
# filters = MetadataFilters(
#     filters=[
#         MetadataFilter(key="author", value="mats@timescale.com"),
#         MetadataFilter(key="author", value="sven@timescale.com"),
#     ],
#     condition="or",
# )
#
# retriever = index.as_retriever(
#     similarity_top_k=10,
#     filters=filters,
# )
#
# retrieved_nodes = retriever.retrieve("What is this software project about?")
#
# for node in retrieved_nodes:
#     logger.info(node.node.metadata)
#
# filters = MetadataFilters(
#     filters=[
#         MetadataFilter(key="commit_date", value="2023-08-15", operator=">="),
#         MetadataFilter(key="commit_date", value="2023-08-25", operator="<="),
#     ],
#     condition="and",
# )
#
# retriever = index.as_retriever(
#     similarity_top_k=10,
#     filters=filters,
# )
#
# retrieved_nodes = retriever.retrieve("What is this software project about?")
#
# for node in retrieved_nodes:
#     logger.info(node.node.metadata)
#
# """#### Apply nested filters
#
# In the above examples, we combined multiple filters using AND or OR. We can also combine multiple sets of filters.
#
# e.g. in SQL:
# ```sql
# WHERE (commit_date >= '2023-08-01' AND commit_date <= '2023-08-15') AND (author = 'mats@timescale.com' OR author = 'sven@timescale.com')
# ```
# """
#
# filters = MetadataFilters(
#     filters=[
#         MetadataFilters(
#             filters=[
#                 MetadataFilter(
#                     key="commit_date", value="2023-08-01", operator=">="
#                 ),
#                 MetadataFilter(
#                     key="commit_date", value="2023-08-15", operator="<="
#                 ),
#             ],
#             condition="and",
#         ),
#         MetadataFilters(
#             filters=[
#                 MetadataFilter(key="author", value="mats@timescale.com"),
#                 MetadataFilter(key="author", value="sven@timescale.com"),
#             ],
#             condition="or",
#         ),
#     ],
#     condition="and",
# )
#
# retriever = index.as_retriever(
#     similarity_top_k=10,
#     filters=filters,
# )
#
# retrieved_nodes = retriever.retrieve("What is this software project about?")
#
# for node in retrieved_nodes:
#     logger.info(node.node.metadata)
#
# """The above can be simplified by using the IN operator. `PGVectorStore` supports `in`, `nin`, and `contains` for comparing an element with a list."""
#
# filters = MetadataFilters(
#     filters=[
#         MetadataFilter(key="commit_date", value="2023-08-01", operator=">="),
#         MetadataFilter(key="commit_date", value="2023-08-15", operator="<="),
#         MetadataFilter(
#             key="author",
#             value=["mats@timescale.com", "sven@timescale.com"],
#             operator="in",
#         ),
#     ],
#     condition="and",
# )
#
# retriever = index.as_retriever(
#     similarity_top_k=10,
#     filters=filters,
# )
#
# retrieved_nodes = retriever.retrieve("What is this software project about?")
#
# for node in retrieved_nodes:
#     logger.info(node.node.metadata)
#
# # Same thing, with NOT IN
# filters = MetadataFilters(
#     filters=[
#         MetadataFilter(key="commit_date", value="2023-08-01", operator=">="),
#         MetadataFilter(key="commit_date", value="2023-08-15", operator="<="),
#         MetadataFilter(
#             key="author",
#             value=["mats@timescale.com", "sven@timescale.com"],
#             operator="nin",
#         ),
#     ],
#     condition="and",
# )
#
# retriever = index.as_retriever(
#     similarity_top_k=10,
#     filters=filters,
# )
#
# retrieved_nodes = retriever.retrieve("What is this software project about?")
#
# for node in retrieved_nodes:
#     logger.info(node.node.metadata)
#
# # CONTAINS
# filters = MetadataFilters(
#     filters=[
#         MetadataFilter(key="fixes", value="5680", operator="contains"),
#     ]
# )
#
# retriever = index.as_retriever(
#     similarity_top_k=10,
#     filters=filters,
# )
#
# retrieved_nodes = retriever.retrieve("How did these commits fix the issue?")
# for node in retrieved_nodes:
#     logger.info(node.node.metadata)
#
# """### PgVector Query Options
#
# #### IVFFlat Probes
#
# Specify the number of [IVFFlat probes](https://github.com/pgvector/pgvector?tab=readme-ov-file#query-options) (1 by default)
#
# When retrieving from the index, you can specify an appropriate number of IVFFlat probes (higher is better for recall, lower is better for speed)
# """
#
# retriever = index.as_retriever(
#     vector_store_query_mode="hybrid",
#     similarity_top_k=5,
#     vector_store_kwargs={"ivfflat_probes": 10},
# )
#
# """#### HNSW EF Search
#
# Specify the size of the dynamic [candidate list](https://github.com/pgvector/pgvector?tab=readme-ov-file#query-options-1) for search (40 by default)
# """
#
# retriever = index.as_retriever(
#     vector_store_query_mode="hybrid",
#     similarity_top_k=5,
#     vector_store_kwargs={"hnsw_ef_search": 300},
# )