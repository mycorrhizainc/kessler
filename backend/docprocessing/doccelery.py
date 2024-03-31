from celery import Celery

from typing import Optional, List, Union

app = Celery("tasks", broker="pyamqp://guest@localhost//")

from docprocessing.docingest import DocumentIngester
from docprocessing.extractmarkdown import MarkdownExtractor
from docprocessing.genextras import GenerateExtras


class DocumentProcessing:
    def __init__(self, gpu_endpoint_url: str, tmpdir: Path):
        self.endpoint_url = gpu_endpoint_url
        self.tmpdir = tmpdir

    @app.task
    def ingest_document(self, input: Union[str, Path]):
        docingest = DocumentIngester(self.tmpdir)
        # mdextract = MarkdownExtractor(self.endpoint_url, self.tmpdir)
        # genextras = GenerateExtras(self.endpoint_url, self.tmpdir)

        return input
