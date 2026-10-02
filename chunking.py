"""Chunking for the course-materials RAG pipeline.

Implements step 3 of the pipeline described in the README: extracted page text
is split into overlapping chunks, and each chunk keeps its document name and
page number as metadata so an answer can cite where it came from.

Standard library only -- deliberately no new dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

DEFAULT_CHUNK_SIZE = 200
DEFAULT_OVERLAP = 40


@dataclass(frozen=True)
class Page:
    """Extracted text for one page of one document."""

    document: str
    page_number: int
    text: str


@dataclass(frozen=True)
class Chunk:
    """A retrievable slice of a page, ready to be embedded and stored."""

    document: str
    page_number: int
    chunk_index: int
    text: str

    def citation(self) -> str:
        """Human-readable source reference, e.g. ``slides.pdf p.12``."""
        return f"{self.document} p.{self.page_number}"


def _validate(chunk_size: int, overlap: int) -> None:
    if chunk_size <= 0:
        raise ValueError(f"chunk_size must be positive, got {chunk_size}")
    if overlap < 0:
        raise ValueError(f"overlap must not be negative, got {overlap}")
    if overlap >= chunk_size:
        raise ValueError(
            f"overlap ({overlap}) must be smaller than chunk_size ({chunk_size})"
        )


def chunk_page(
    page: Page,
    *,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_OVERLAP,
) -> list[Chunk]:
    """Split a single page into overlapping windows of ``chunk_size`` words.

    Consecutive chunks share ``overlap`` words so context is not lost at a
    boundary. A page with no words produces an empty list. The trailing short
    window is emitted only if it holds words not already covered, so the final
    chunk is never a pure duplicate of the previous one.
    """
    _validate(chunk_size, overlap)

    words = page.text.split()
    if not words:
        return []

    step = chunk_size - overlap
    chunks: list[Chunk] = []
    start = 0
    index = 0

    while start < len(words):
        window = words[start : start + chunk_size]
        chunks.append(
            Chunk(
                document=page.document,
                page_number=page.page_number,
                chunk_index=index,
                text=" ".join(window),
            )
        )
        index += 1

        if start + chunk_size >= len(words):
            break
        start += step

    return chunks


def chunk_pages(
    pages: Iterable[Page],
    *,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_OVERLAP,
) -> list[Chunk]:
    """Chunk every page in order, preserving each page's metadata.

    ``chunk_index`` restarts at 0 for each page.
    """
    _validate(chunk_size, overlap)

    chunks: list[Chunk] = []
    for page in pages:
        chunks.extend(chunk_page(page, chunk_size=chunk_size, overlap=overlap))
    return chunks
