from typing import Tuple
from pathlib import Path


from src.niclib import *

from src.llm_prompts import LLM

import subprocess

import requests
import logging

from typing import List, Optional

from warnings import warn

DEFAULT_TMPDIR = Path("/tmp/")


# YOUR CPU SHALL BE SACRIFICED FOR OUR SERVER BANDWITH, MUAHAHAHAHAHA
def downsample_audio(
    filepath: Path, file_type: str, bitrate: int, tmpdir: Path
) -> Path:
    outfile = tmpdir / Path(rand_string() + ".opus")
    """
    Converts an input audio or video file to a Opus audio file w/ a specified bit rate.
    """
    ffmpeg_command = [
        "ffmpeg",  # The command to invoke FFmpeg
        "-i",
        filepath,  # The input file
        "-c:a",
        "libopus",  # Codec to use for the audio conversion
        "-b:a",
        str(bitrate),  # Bitrate for the output audio
        "-vn",  # No video (discard video data)
        outfile,  # Name of the output file
    ]
    # Execute the FFmpeg command
    result = subprocess.run(
        ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    # Check if FFmpeg command execution was successful
    if result.returncode != 0:
        warn(
            f"Error converting video file, falling back to original. FFmpeg said:\n{result.stderr.decode()}"
        )
        return filepath
    return outfile


class GPUComputeEndpoint:
    def __init__(self, endpoint_url: str):
        GPUComputeEndpoint(self.endpoint_url)_url = endpoint_url

    def llm_nonlocal_raw_call(
        self, msg_history: list[dict], model_name: Optional[str]
    ) -> dict:
        if model_name == None:
            model_name = "nous-hermes-2-mistral-7b-dpo"
        # The API endpoint you will be hitting
        url = f"{GPUComputeEndpoint(self.endpoint_url)_url}/v0/chat_completion/external_api"
        jsonpayload = {
            "messages": msg_history,
            "model_name": model_name,
        }
        print(f"Calling external endpoint: {GPUComputeEndpoint(self.endpoint_url)_url}")
        # Make the POST request with files
        response = requests.post(url, json=jsonpayload)
        # Raise an exception if the request was unsuccessful
        response.raise_for_status()
        # Parse the JSON response
        response_json = response.json()
        # Extract the translated text from the JSON response
        return response_json["message"]

    def llm_from_model_name(self, model_name: Optional[str] = None):
        return LLM(lambda messages: self.llm_nonlocal_raw_call(messages, model_name))

    def audio_to_text_raw(
        self, filepath: Path, source_lang: str, target_lang: str, file_type: str
    ) -> str:
        # The API endpoint you will be hitting
        url = f"{GPUComputeEndpoint(self.endpoint_url)_url}/v0/multimodal_asr/whisper-latest"
        # Open the file in binary mode
        with filepath.open("rb") as file:
            # Define the multipart/form-data payload
            files = {"file": (filepath.name, file, "application/octet-stream")}
            jsonpayload = {
                "source_lang": source_lang,
                "target_lang": target_lang,
            }
            # Make the POST request with files
            response = requests.post(url, files=files, json=jsonpayload)
            # Raise an exception if the request was unsuccessful
            response.raise_for_status()

        # Parse the JSON response
        response_json = response.json()

        # Extract the translated text from the JSON response
        translated_text = response_json["response"]
        return translated_text

    def audio_to_text(
        self,
        filepath: Path,
        source_lang: str,
        target_lang: str,
        file_type: str,
        bitrate: int = 15000,
        tmpdir: Path = DEFAULT_TMPDIR,
    ) -> str:
        downsampled = downsample_audio(filepath, file_type, bitrate, tmpdir)
        if downsampled == filepath:
            return self.audio_to_text_raw(filepath, source_lang, target_lang, file_type)
        return self.audio_to_text_raw(downsampled, source_lang, target_lang, "opus")

    def transcribe_pdf(self, filepath: Path) -> str:
        # The API endpoint you will be hitting
        # url = "http://api.mycor.io/v0/multimodal_asr/local-m4t"
        url = f"{GPUComputeEndpoint(self.endpoint_url)_url}/v0/document-ocr/local-nougat"
        # Open the file in binary mode
        with filepath.open("rb") as file:
            # Define the multipart/form-data payload
            files = {
                "file": (filepath.name, file, "application/octet-stream"),
            }
            # Mke the POST request with files
            response = requests.post(url, files=files)
            print(f"Request Headers: {response.request.headers}")
            # Raise an exception if the request was unsuccessful
            response.raise_for_status()

        # Parse the JSON response
        response_json = response.json()

        # Extract the translated text from the JSON response
        translated_text = response_json["response"]
        return translated_text

    def embed_raw_dicts(self, text_list: List[dict], model_name: str) -> list:
        if not model_name in ["mistral7b-sfr"]:
            raise Exception("Invalid Model ID")
        if len(text_list) == 0:
            return []
        url = f"{GPUComputeEndpoint(self.endpoint_url)_url}/v0/embedding/{model_name}"
        payload = {"embeddable": text_list, "model_name": model_name}
        response = requests.post(url, json=payload)
        response.raise_for_status()
        embeddings = response.json().get("embeddings", [])
        print(embeddings)
        return embeddings

    def embed_queries_and_texts(
        self, query_list: List[str], text_list: List[str]
    ) -> Tuple[list, list]:
        query_dict_list = map(lambda x: {"text": x, "query": True}, query_list)
        text_dict_list = map(lambda x: {"text": x, "query": False}, text_list)

        raw_list = list(query_dict_list) + list(text_dict_list)
        embeddings = self.embed_raw_dicts(raw_list, "mistral7b-sfr")
        query_embeddings = embeddings[: len(query_list)]
        text_embeddings = embeddings[len(query_list) :]
        return (query_embeddings, text_embeddings)

    def embedding_query(self, embedding: str):
        return (self.embed_queries_and_texts([embedding], [])[0])[0]

    def translate_text(
        self, doctext: str, source_lang: Optional[str], target_lang: str
    ) -> str:
        url = f"{GPUComputeEndpoint(self.endpoint_url)_url}/v0/translation/google-translate"
        payload = {
            "text": doctext,
            "source_lang": source_lang,
            "target_lang": target_lang,
        }
        response = requests.post(url, json=payload)
        response.raise_for_status()
        text = response.json().get("text", [])
        return text
