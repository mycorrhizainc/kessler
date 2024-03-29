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

from util.gpu_compute_calls import GPUComputeEndpoint


class MarkdownExtractor:
    def __init__(
        self, endpoint: GPUComputeEndpoint, tmpdir=Path("/tmp/kessler/extractmarkdown")
    ):
        self.tmpdir = tmpdir
        self.endpoint = endpoint
        # TODO : Add database connection.

    def process_raw_document_into_english_text(self, file_loc: Path, metadata: dict):
        raw_text = self.process_raw_document_into_untranslated_text(file_loc, metadata)
        lang = metadata["lang"]
        if lang in ["en", "eng", "english", None]:
            return raw_text
        english_text = self.endpoint.translate_text(raw_text, lang, "en")
        return english_text

    def process_raw_document_into_untranslated_text(
        self, file_loc: Path, metadata: dict
    ) -> str:
        doctype = metadata["doctype"]

        def process_audio(filepath: Path, metadata: dict) -> str:
            source_lang = metadata["language"]
            target_lang = "en"
            doctype = metadata["doctype"]
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
        if doctype == "md":
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
            return process_audio(file_loc, metadata)
        else:
            raise ValueError(
                f'Improper File Type, processing Failed with doctype: "{doctype}"'
            )

    def get_proc_doc_original(self, doc: DocumentID) -> Optional[str]:
        # TODO: 

    def get_proc_doc_translated(
        self, doc: DocumentID, target_lang: str
    ) -> Optional[str]:
