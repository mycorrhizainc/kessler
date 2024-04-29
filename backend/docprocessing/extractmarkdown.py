from util.niclib import rand_string, rand_filepath
import logging

# Note: Refactoring imports.py

import requests

from typing import Optional, List, Union


# from langchain.vectorstores import FAISS

import subprocess
import os


from pathlib import Path

from util.gpu_compute_calls import GPUComputeEndpoint


class MarkdownExtractor:
    def __init__(self, logger, endpoint_url: str, tmpdir: Path):
        self.tmpdir = tmpdir
        self.endpoint_url = endpoint_url
        self.logger = logger
        # TODO : Add database connection.

    def process_raw_document_into_english_text(self, file_loc: Path, metadata: str):
        lang = metadata["str"]
        raw_text = self.process_raw_document_into_untranslated_text(file_loc, metadata)
        return self.convert_text_into_eng(raw_text, lang)

    def convert_text_into_eng(self, file_text: str, lang: str):
        if lang in ["en", "eng", "english", None]:
            return raw_text
        english_text = GPUComputeEndpoint(self.endpoint_url).translate_text(
            raw_text, lang, "en"
        )
        return english_text

    def process_raw_document_into_untranslated_text(
        self, file_loc: Path, doctype : str, lang : str
    ) -> str:
        def process_audio(filepath: Path, metadata: dict) -> str:
            source_lang = metadata["language"]
            target_lang = "en"
            doctype = metadata["doctype"]
            return GPUComputeEndpoint(self.endpoint_url).audio_to_text(
                filepath, source_lang, target_lang, doctype
            )

        def process_pdf(filepath: Path) -> str:
            return GPUComputeEndpoint(self.endpoint_url).transcribe_pdf(filepath)

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
