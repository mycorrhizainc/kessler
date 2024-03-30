from celery import Celery

from typing import Optional, List, Union

app = Celery("tasks", broker="pyamqp://guest@localhost//")

from docprocessing.docingest import DocumentIngester


class DocumentProcessing:
    def __init__(
        self,
        gpu_endpoint_url: str,
    ):
        self.endpoint_url = gpu_endpoint_url

    @app.task
    def ingest_document(input: Union[str, Path]):
        return input
