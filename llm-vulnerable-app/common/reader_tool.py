from typing import Type

from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from common import website_reader

MAX_RESULT_LENGTH_CHAR = 1000 * 4  # roughly 1,000 tokens


def page_result(text: str, cursor: int, max_length: int) -> (str, bool):
    """Page through `text` and return a substring of `max_length` characters starting from `cursor`."""
    return text[cursor: cursor + max_length], len(text) > cursor + max_length


def get_url(url: str) -> str:
    """Fetch URL and return the contents as a string."""

    documents = website_reader.read_from_url(url)
    return "\n".join([doc.page_content for doc in documents])


class ReaderToolInput(BaseModel):
    url: str = Field(..., description="URL of the website to read")
    cursor: int = Field(
        default=0,
        description="Start reading from this character."
                    "Use when the first response was truncated"
                    "and you want to continue reading the page.",
    )


class ReaderTool(BaseTool):
    """Reader tool for getting website contents. Gives more control than SimpleReaderTool."""

    name: str = "read_page"
    args_schema: Type[BaseModel] = ReaderToolInput
    description: str = "use this to read a website"

    def _run(self, url: str, cursor: int = 0) -> str:
        page_contents = get_url(url)

        page_result_str, has_more = page_result(page_contents, cursor, MAX_RESULT_LENGTH_CHAR)
        if has_more:
            page_contents += f"\nPAGE WAS TRUNCATED. TO CONTINUE READING, USE CURSOR={cursor + len(page_contents)}."

        return page_contents

    async def _arun(self, url: str) -> str:
        raise NotImplementedError


class SimpleReaderToolInput(BaseModel):
    url: str = Field(..., description="URL of the website to read")


class SimpleReaderTool(ReaderTool):
    """Reader tool for getting website contents, with URL as the only argument."""

    name: str = "simple_read_page"
    args_schema: Type[BaseModel] = SimpleReaderToolInput
    description: str = "use this to read a website"
