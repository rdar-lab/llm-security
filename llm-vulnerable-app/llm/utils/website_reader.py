import logging

from langchain_community.document_loaders import WebBaseLoader

_logger = logging.getLogger(__name__)


def read_from_url(url):
    loader = WebBaseLoader(url, verify_ssl=False)
    docs = loader.load()
    _logger.info(f"Loaded documents {docs}")
    return docs
