from typing import Optional, List, Union

from pydantic import BaseModel

import hashlib


from pathlib import Path

from src.niclib import *


def HumanMessage(content: str):
    return {"content": content, "role": "Human"}


def SystemMessage(content: str):
    return {"content": content, "role": "System"}


def AIMessage(content: str):
    return {"ai": content, "role": "System"}


class DocumentArrow(BaseModel):
    origin_id: str
    target_id: str
    data: dict = {}


class DocumentID(BaseModel):
    hashes: dict
    metadata: dict = {}
    extras: dict = {
        "instantiated_references": False,
        "links": [],
        "summary": None,  # Maybe(str)
    }
    arrows: list[DocumentArrow] = []


def gen_hash_dict(filepath: Path) -> dict:
    return {
        "blake2": get_hash_str(filepath, hashlib.blake2b()),
        "sha256": get_hash_str(filepath, hashlib.sha256()),
        "md5": get_hash_str(filepath, hashlib.md5()),
    }


def dochash(docid: DocumentID):
    return docid.hashes["blake2"]


def opt_dochash(doc: Union[DocumentID, str]) -> str:
    if isinstance(doc, str):
        return doc
    else:
        return dochash(doc)


# Specific type of error for cases where LLM outputs are unparsable
class LLMParseError(Exception):
    pass
