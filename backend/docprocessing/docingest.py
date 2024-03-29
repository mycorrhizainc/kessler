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


def download_file(url: str, savedir: Path) -> Path:
    local_filename = savedir  # TODO: Use a temporary directory for downloads or archive it in some other way.
    # NOTE the stream=True parameter below
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                # if chunk:
                f.write(chunk)
    return local_filename


class DocumentIngester:
    def __init__(self, tmpdir=Path("/tmp/kessler/docingest")):
        self.tmpdir = tmpdir
        self.crossref = Crossref()
        # TODO : Add database connection.

    def add_document_to_database(self, document_path: Path, metadata: dict):
        # TODO : Add document to database
        print("Yell at nicole to add stuff to the database.")

    def url_to_file_and_metadata(self, url: str) -> tuple[Path, dict]:
        parsed_url = urllib.parse.urlparse(url)
        domain = (
            parsed_url.netloc.split(".")[-2] + "." + parsed_url.netloc.split(".")[-1]
        )
        if domain in ["youtube.com", "youtu.be"]:
            filepath, metadata = self.get_file_from_ytdlp(url)
        elif domain in ["arxiv.org"]:
            filepath, metadata = self.get_file_from_arxiv(url)
        else:
            filepath, metadata = self.add_file_from_url_nocall(url)
        return (filepath, metadata)

    def get_file_from_arxiv(self, url: str) -> tuple[Path, dict]:
        def extract_arxiv_id(url: str) -> Optional[str]:
            # Regular expression to match arXiv ID patterns in the URL
            arxiv_regex = re.compile(
                r"arxiv\.org/(?:abs|html|pdf|e-print)/(\d+\.\d+v?\d*)(?:\.pdf)?",
                re.IGNORECASE,
            )

            # Search for matches using the regex
            match = arxiv_regex.search(url)

            # If a match is found, return the ID in the required format
            if match:
                arxiv_id = match.group(1)
                return arxiv_id
            return None

        arxiv_id = extract_arxiv_id(url)
        if arxiv_id == None:
            logging.warn("Failed to find arxiv id, falling back to HTML,")
            return self.add_file_from_url_nocall(url)
        htmlurl = f"https://arxiv.org/html/{arxiv_id}v1"

        htmlresponse = requests.get(htmlurl)

        # TODO : Generalize this function into a general metadata searcher, this fails if the doi is not found for example.
        try:
            metadata = self.crossref.works(ids=f"10.48550/arXiv.{arxiv_id}")
        except:
            logging.warning(
                "Not able to lookup metadata based on doi, defaulting to extracting html metadata from arxiv."
            )
            metadata = self.get_metada_from_url(f"https://arxiv.org/abs/{arxiv_id}")

        if "HTML is not available for the source" in htmlresponse.text:
            metadata["doctype"] = "pdf"
            pdfdir = download_file(
                f"https://arxiv.org/pdf/{arxiv_id}.pdf", self.tmpdir / rand_filepath()
            )
            return (pdfdir, metadata)
        htmlpath = self.tmpdir / Path(rand_string())
        with open(htmlpath, "w") as file:
            file.write(htmlresponse.text)
        metadata["doctype"] = "html"
        return (htmlpath, metadata)

    def get_file_from_ytdlp(self, url: str) -> Optional[tuple[Path, dict]]:
        filename = rand_string()
        ytdlp_path = self.tmpdir / Path(filename)
        video_path = self.tmpdir / Path(filename + ".mkv")
        json_path = self.tmpdir / Path(filename + ".info.json")
        json_filepath = self.tmpdir / Path(rand_string())
        command = f"yt-dlp --remux-video mkv --write-info-json -o {shlex.quote(str(ytdlp_path))} {shlex.quote(url)}"
        logging.info(f"Calling youtube dlp with call: {command}")
        try:
            result = subprocess.run(
                command,
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            with open(json_path, "r", encoding="utf-8") as info_file:
                info_data = json.load(info_file)
                metadata = {
                    "title": info_data.get("title"),
                    "author": info_data.get("uploader"),
                    "language": info_data.get("language"),
                    "url": url,
                    "doctype": "mkv",
                }
                logging.info((video_path, metadata))
                return (video_path, metadata)
        except subprocess.CalledProcessError as e:
            logging.critical(f"An error occurred when using yt-dlp: {e.stderr}")
            return None

    def get_metada_from_url(self, url: str) -> dict:
        response = requests.get(url)

        def get_doctype_from_header_and_url(response, url: str) -> Optional[str]:
            # Guess the file extension from the URL itself
            # This is useful for direct links to files with a clear file extension in the URL
            if url.lower().endswith(
                (".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx")
            ):
                return url.split(".")[-1].lower()
            content_type = response.headers.get("Content-Type")
            # If the Content-Type header is not found, return None
            if content_type is None or content_type == None:
                return None
            # Use the mimetypes library to get the corresponding extension
            file_extension = mimetypes.guess_extension(content_type.split(";")[0])
            if file_extension:
                return file_extension.strip(
                    "."
                )  # Remove the . at the beginning of the extension
            else:
                # No matching file extension found, return the MIME type directly
                return content_type.split("/")[-1]

        # Call function to get the document_type
        document_type = get_doctype_from_header_and_url(response, url)
        # Get language from the headers
        language = response.headers.get("Content-Language")
        # Get last modified from the headers
        last_modified = response.headers.get("Last-Modified")

        def url_to_name(url: str) -> str:
            parsed_url = urllib.parse.urlparse(url)
            netloc_path = parsed_url.netloc + parsed_url.path
            return netloc_path.replace("/", "-")

        name = url_to_name(url)
        return {
            "doctype": document_type,
            "language": language,
            "date": last_modified,
            "title": name,
        }

    def add_file_from_url_nocall(self, url: str) -> tuple[Path, dict]:
        metadata = self.get_metada_from_url(url)
        fileloc = download_file(url, self.tmpdir / Path(rand_string()))
        return (fileloc, metadata)

    def infer_metadata_from_path(self, filepath: Path) -> dict:
        return {"title": filepath.stem, "doctype": filepath.suffix}
