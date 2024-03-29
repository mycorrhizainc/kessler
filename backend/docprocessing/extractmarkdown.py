from util.niclib import rand_string, rand_filepath


from typing import Optional, List, Union

import json
import re


from habanero import Crossref


import logging

# Note: Refactoring imports.py

import requests

from typing import Optional, List, Union


# from langchain.vectorstores import FAISS

import subprocess
import warnings
import shutil
import urllib
import mimetypes
import os
import pickle


from pathlib import Path
import shlex


class MarkdownExtractor:
    def __init__(self, tmpdir=Path("/tmp/kessler/extractmarkdown")):
        self.tmpdir = tmpdir
        # TODO : Add database connection.

    def is_english(self, lang_code: Optional[str]) -> bool:
        return lang_code in ["en", "eng", "english", None]

    def translate_to_english_if_necessary(self, raw_text: str, lang: Optional[str]):
        if not self.is_english(rawdoc):
            original_lang_document_text = generate_yaml_string(rawdoc) + document_text
            self.__add_proc_file_original_lang_nocheck(
                rawdoc, original_lang_document_text
            )
            english_text = self.GPUComputeEndpoint.translate_text(
                document_text, rawdoc.metadata["lang"], "en"
            )
            document_text = english_text

    def process_raw_document_into_text(self, file_loc: Path, doc_id: DocumentID) -> str:
        doctype = doc_id.metadata["doctype"]

        def process_audio(filepath: Path, documentid: DocumentID) -> str:
            source_lang = documentid.metadata["language"]
            target_lang = "en"
            doctype = documentid.metadata["doctype"]
            return self.endpoint.audio_to_text(
                filepath, source_lang, target_lang, doctype
            )

        def process_pdf(filepath: Path) -> str:
            return self.endpoint.transcribe_pdf(filepath)

        # Take a file with a path of path and a pandoc type of doctype and convert it to pandoc markdown and return the output as a string.
        # TODO: Make it so that you dont need to run sudo apt install pandoc for it to work, and it bundles with the pandoc python library
        def process_pandoc(filepath: Path, doctype: str) -> str:
            command = f"pandoc -f {doctype} {filepath}"
            process = subprocess.Popen(
                command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            output, error = process.communicate()
            output_str = output.decode()
            error_str = error.decode()
            if error_str:  # TODO : Debug this weird if statement
                raise Exception(f"Error running pandoc command: {error_str}")
            return output_str

        if not os.path.isfile(file_loc):
            raise Exception("A document with that hash is not present")
        elif doctype == "md":
            with open(file_loc, "r") as file:
                result = file.read()
            return result
        elif doctype == "pdf":
            return process_pdf(file_loc)
        elif doctype in [
            "html",
            "doc",
            "docx",
            "tex",
            "epub",
            "odt",
            "rtf",
        ]:
            return process_pandoc(file_loc, doctype)
        elif doctype == "tex":
            return process_pandoc(file_loc, "latex")
        elif doctype in ["mp3", "opus", "mkv"]:
            return process_audio(file_loc, doc_id)
        else:
            raise ValueError(
                f'Improper File Type, processing Failed with doctype: "{doctype}"'
            )

    def get_proc_doc_original(self, doc: DocumentID) -> Optional[str]:
        if doc["lang"] in ["en"]:
            return self.get_proc_doc(doc)
        path = self.__procdocpath_original(doc)
        if not (path.is_file()):
            raise Exception(
                "Original Language Processed File does not exist for nonenglish file!"
            )
        with open(path, "r") as file:
            text_with_metadata = file.read()
        text_without_metadata = self.strip_yaml_header(text_with_metadata)
        return text_without_metadata

    def get_proc_doc_translated(
        self, doc: DocumentID, target_lang: str
    ) -> Optional[str]:
        if target_lang == "en":
            return self.get_proc_doc(doc)
        elif target_lang == doc.metadata["lang"]:
            return self.get_proc_doc_original(doc)
        elif self.is_english(doc):
            eng_text = self.get_proc_doc(doc)
            return self.endpoint.translate_text(eng_text, "en", target_lang)
        else:
            doc_text = self.get_proc_doc_original(doc)
            return self.endpoint.translate_text(
                doc_text, doc.metadata["lang"], target_lang
            )
