from typing import Optional, List, Union
from src.gpu_compute_calls import *

import json
import copy
import yaml
import re


from habanero import Crossref

from langchain_core.documents import Document

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

from src.niclib import *

from src.llm_prompts import LLM, token_split

from src.datatypes import *


from langchain.vectorstores import FAISS

DEFAULT_VECT = FAISS


from langchain.embeddings import HuggingFaceBgeEmbeddings

langchain_hf_uae_large_v1 = HuggingFaceBgeEmbeddings(
    model_name="WhereIsAI/UAE-Large-V1",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)

DEFAULT_EMBEDDINGS = langchain_hf_uae_large_v1


class DocumentProcessor:
    # Megaclass Containing Everything
    def __init__(
        self,
        llm: LLM,
        rawDocDir: Path,
        procDocDir: Path,
        gpu_compute_endpoint: GPUComputeEndpoint,
        tmpdir: Path = Path("/tmp/"),
        picklepath: Optional[Path] = None,
        embeddings=DEFAULT_EMBEDDINGS,
        vector_database=DEFAULT_VECT,
    ):
        self.rawDocDir = rawDocDir
        self.rawDocDir.mkdir(parents=True, exist_ok=True)
        self.procDocDir = procDocDir
        self.procDocDir.mkdir(parents=True, exist_ok=True)
        self.tmpdir = tmpdir
        self.tmpdir.mkdir(parents=True, exist_ok=True)
        self.crossref = Crossref()
        self.embeddings = embeddings
        self.endpoint = gpu_compute_endpoint
        self.llm = llm
        if picklepath == None:
            self.__documentlist: dict = {}
        else:
            with open(picklepath, "rb") as f:
                self.__documentlist = pickle.load(f)

        self.reconstruct_from_processed_markdown()
        self.vdb = vector_database.from_documents(
            documents=[
                Document(
                    "Langchain is bugged if you try to initialize with no documents."
                )
            ],
            embedding=self.embeddings,
        )
        map(self.add_docid_to_vdb, self.dump_documents())

    # NOTE: CODE FOR INTITALIZING, RESTORING AND SAVING THE DOCUMENT DATABASE
    def reconstruct_from_processed_markdown(self):
        return "Nicole should write this function"

    # TODO: MAKE THE FUNCTION

    def pickle_dict(self, picklepath: Path):
        if not picklepath.exists() or picklepath.is_file() or picklepath.is_dir():
            Exception(f"File is present at {picklepath}, cannot save dictionary")
        else:
            with open(picklepath, "wb") as f:
                pickle.dump(self.__documentlist, f)

    # NOTE: PURE CODE BEGINS HERE:

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
            warn("Failed to find arxiv id, falling back to HTML,")
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

    # NOTE: MISC FUNCTIONS
    def is_english(self, doc: DocumentID) -> bool:
        return doc.metadata["lang"] in ["en", "eng"]

    # NOTE: SETTERS AND GETTERS BEGIN HERE:

    def __rawdocpath(self, doc: Union[DocumentID, str]) -> Path:
        blake2b64 = opt_dochash(doc)
        return self.rawDocDir / Path(blake2b64)

    def __procdocpath(self, doc: Union[DocumentID, str]) -> Path:
        blake2b64 = opt_dochash(doc)
        return self.procDocDir / Path(blake2b64 + ".md")

    def __procdocpath_original(self, doc: Union[DocumentID, str]) -> Path:
        blake2b64 = opt_dochash(doc)
        return self.procDocDir / Path(blake2b64 + "-original.md")

    def __add_raw_file_nocheck(
        self, doc: Union[DocumentID, str], file_location_raw: Path
    ):
        shutil.copy(file_location_raw, self.__rawdocpath(doc))

    def __add_proc_file_nocheck(
        self, doc: Union[DocumentID, str], processed_file_text: str
    ):
        file_path = self.__procdocpath(doc)
        # TODO : IF duplicates and lost metadata is a problem add a function here that merges the metadata
        if os.path.isfile(file_path):
            os.remove(file_path)
        with open(file_path, "w") as file:
            file.write(processed_file_text)

    def __add_proc_file_original_lang_nocheck(
        self, doc: Union[DocumentID, str], processed_file_text: str
    ):
        file_path = self.__procdocpath_original(doc)
        if os.path.isfile(file_path):
            os.remove(file_path)
        with open(file_path, "w") as file:
            file.write(processed_file_text)

    def __add_doc_nocheck(self, doc: Union[DocumentID, str], filepath: Path = Path("")):
        self.__documentlist[opt_dochash(doc)] = doc
        if filepath != Path(""):
            self.__add_raw_file_nocheck(doc, filepath)

    def add_docID(self, doc: Union[DocumentID, str], filepath: Path):
        if opt_dochash(doc) == get_blake2(filepath):
            self.__add_doc_nocheck(doc, filepath)
        else:
            warnings.warn("File does not match hash.")

    def get_doc_from_hash(self, b64blake2: str) -> DocumentID:
        return self.__documentlist[b64blake2]

    def strip_yaml_header(self, text_with_metadata: str) -> Optional[str]:
        split_text = text_with_metadata.split("\n---\n")
        text_without_metadata = "\n---\n".join(
            split_text[1::]
        )  # Take out the metadata chunk and reconstruct the string
        # Check if string is empty of whitespace and if so return nothing
        if text_without_metadata == "" or text_without_metadata.isspace():
            return None
        return text_without_metadata

    def get_proc_doc(self, doc: Union[DocumentID, str]) -> Optional[str]:
        path = self.__procdocpath(doc)
        if not (path.is_file()):
            raise Exception("Processed File does not exist!")
        with open(path, "r") as file:
            text_with_metadata = file.read()
        text_without_metadata = self.strip_yaml_header(text_with_metadata)
        return text_without_metadata

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

    def dump_hashes(self) -> list:
        return list(self.__documentlist.keys())

    def dump_documents(self) -> list:
        return list(self.__documentlist.values())

    # NOTE: CODE FOR ADDING DOCUMENTS

    def add_document_from_path(
        self, filepath: Path, metadata: Optional[dict] = None
    ) -> DocumentID:
        if metadata == None:
            metadata = self.infer_metadata_from_path(filepath)
        dochash = get_blake2(filepath)
        collision = self.__documentlist.get(dochash)
        if collision != None:
            warnings.warn(
                f"File with blake2 hash {dochash} already present, leaving metadata unchanged."
            )
            return collision
        else:
            hash_dict = gen_hash_dict(filepath)
            raw_document = DocumentID(hashes=hash_dict, metadata=metadata)
            self.__add_doc_nocheck(raw_document, filepath)
            return raw_document

    # NOTE: CODE THAT INITIALIZES AN EXISTING DOCUMENT

    def process_raw_document(self, rawdoc: DocumentID):
        # Generate a chunk of yaml that will allow recovery of metadata:
        def generate_yaml_string(doc_id: DocumentID) -> str:
            yaml_dict = copy.deepcopy(doc_id.metadata)
            yaml_dict["hashes"] = copy.deepcopy(doc_id.hashes)
            yaml_str = yaml.dump(yaml_dict)
            return "---\n" + yaml_str + "\n---\n"

        rawdoc_path = self.__rawdocpath(rawdoc)
        document_text = self.process_raw_document_into_text(rawdoc_path, rawdoc)
        assert document_text != None
        assert document_text != ""
        # TODO: Write script for figuring out language automatically instead of assuming it is english.
        if rawdoc.metadata.get("lang") == None:
            rawdoc.metadata["lang"] = "en"
        if not self.is_english(rawdoc):
            original_lang_document_text = generate_yaml_string(rawdoc) + document_text
            self.__add_proc_file_original_lang_nocheck(
                rawdoc, original_lang_document_text
            )
            english_text = self.GPUComputeEndpoint.translate_text(
                document_text, rawdoc.metadata["lang"], "en"
            )
            document_text = english_text
        final_doc_text = generate_yaml_string(rawdoc) + document_text
        self.__add_proc_file_nocheck(rawdoc, final_doc_text)

    # Checks if the supplied DocumentID has a summary and if it doesnt it generates one and returns the docid.
    def generate_summary_mut(
        self, docid: DocumentID, regenerate_summary: bool = False
    ) -> DocumentID:
        # Check to see if a summary was already generated
        not_regen_summary = not regenerate_summary
        if (
            (docid.extras["summary"] == None)
            & (docid.extras["short_summary"])
            & not_regen_summary
        ):
            return docid
        processed_text = self.get_proc_doc(docid)
        summary_text = self.llm.summarize_document_text(processed_text)
        docid.extras["summary"] = summary_text
        short_summary_text = self.llm.gen_short_sum_from_long_sum(summary_text)
        docid.extras["short_summary"] = short_summary_text
        return docid

    # Gets the links from the text of a document id:
    def extract_links_mut(self, docid: DocumentID):
        # Function that extracts the markdown links on a piece of markdown text
        def extract_markdown_links(markdown_document_text: str) -> list[str]:
            # This regex pattern is designed to match typical markdown link structures
            markdown_url_pattern = r"!?\[.*?\]\((.*?)\)"
            # Find all non-overlapping matches in the markdown text
            urls = re.findall(markdown_url_pattern, markdown_document_text)
            return urls

        markdown_text = self.get_proc_doc(docid)
        docid.extras["links"] = extract_markdown_links(markdown_text)
        return docid

    def generate_extras_hash(
        self, blake2b64: str, regenerate_summary: bool = False
    ) -> DocumentID:
        self.generate_summary_mut(self.__documentlist[blake2b64], regenerate_summary)
        self.extract_links_mut(self.__documentlist[blake2b64])
        return self.__documentlist[blake2b64]

    def generate_extras_docid(
        self, docid: DocumentID, regenerate_summary: bool = False
    ) -> DocumentID:
        return self.generate_extras_hash(dochash(docid), regenerate_summary)

    # NOTE: VECTOR DATABASE STUFF

    def chunkify_doc(self, doc: DocumentID, chunk_size: int = 500) -> list:
        processed_doc_text = self.get_proc_doc(doc)
        assert processed_doc_text != None
        chunks = token_split(processed_doc_text, chunk_size)
        create_smalldoc = lambda x: Document(x)
        # TODO: Verify and rewrite the vector database side of this whole thing so it isnt using langchain for imports.
        return list(map(create_smalldoc, chunks))

    def add_docid_to_vdb(self, docid: DocumentID):
        ## Convert doc into chunks
        chunks = self.chunkify_doc(docid)
        self.vdb.add_documents(chunks)

    def add_docids_to_vdb(self, doc_list: list):
        map(self.add_docids_to_vdb, doc_list)

    def retrieve(self, query: str) -> list:
        return self.vdb.similarity_search(query)

    # NOTE: Final Public Methods
    def generate_log(self, docid: DocumentID) -> str:
        doc_metadata = f"Document added to database with hash:{dochash(docid)}\n{yaml.dump(docid.metadata)}"
        text = self.get_proc_doc(docid)
        if text == None:
            logging.error(f"Document {dochash(docid)} was unable to be processed.")
            doc_exerpt = ""
        else:
            doc_exerpt = "\nExcerpt: " + text[0:100]
        summary = docid.extras.get("summary")
        if summary == None:
            logging.error(f"Summary not generated for document: {dochash(docid)}")
            doc_summary = ""
        else:
            doc_summary = "\nExcerpt: " + docid.extras["summary"]
        log = doc_metadata + doc_exerpt + doc_summary
        logging.info(log)
        return log

    def postprocess_document(self, docid: DocumentID) -> DocumentID:
        assert docid != None
        assert docid.metadata.get("doctype") != None
        self.process_raw_document(docid)
        self.generate_extras_docid(docid)
        # self.add_docid_to_vdb(docid)
        self.generate_log(docid)
        return docid

    def add_url(self, url: str) -> DocumentID:
        filepath, metadata = self.url_to_file_and_metadata(url)
        docid = self.add_document_from_path(filepath, metadata)
        docid = self.postprocess_document(docid)
        return docid

    def add_files_in_directory(self, dirpath: Path):
        def recursive_find_files(dirpath: Path):
            if dirpath.is_dir():
                listoflists = map(recursive_find_files, dirpath.glob("*"))
                return concatlist(list(listoflists))
            else:
                return [dirpath]

        # Add all the files to the doc db
        list_of_docids = map(self.add_document_from_path, recursive_find_files(dirpath))
        # Postprocess all the documents.
        map(self.postprocess_document, list_of_docids)

    # NOTE: Buisness logic for dedicated contractor stuff
    def add_youtube_playlist(self, url: str):
        def get_playlist_video_urls_ytdlp(playlist_url: str) -> List[str]:
            # Command to fetch playlist info
            cmd = ["yt-dlp", "--flat-playlist", "--dump-json", playlist_url]
            # Run the command and capture the output
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # Check for errors in execution
            if result.returncode != 0:
                raise Exception(
                    f"Error executing yt-dlp: {result.stderr.decode('utf-8')}"
                )
            # Process the result
            video_urls = []
            for line in result.stdout.splitlines():
                video_data = json.loads(line)
                video_id = video_data.get("id")
                if video_id:
                    video_urls.append(f"https://www.youtube.com/watch?v={video_id}")

            return video_urls

        video_urls = get_playlist_video_urls_ytdlp(url)
        video_docids = map(self.add_url, video_urls)
        return list(video_docids)
