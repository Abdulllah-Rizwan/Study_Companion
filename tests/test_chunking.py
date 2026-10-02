"""Tests for the chunking module.

Run with either of:
    python -m unittest discover
    python -m unittest discover -s tests -t .
"""

import unittest

from chunking import Chunk, Page, chunk_page, chunk_pages


def make_page(text: str, document: str = "slides.pdf", page_number: int = 1) -> Page:
    return Page(document=document, page_number=page_number, text=text)


def numbered_words(count: int) -> list[str]:
    return [f"w{i}" for i in range(count)]


class ChunkPageTests(unittest.TestCase):
    def test_empty_page_produces_no_chunks(self):
        self.assertEqual(chunk_page(make_page("")), [])

    def test_whitespace_only_page_produces_no_chunks(self):
        self.assertEqual(chunk_page(make_page("   \n\t  ")), [])

    def test_short_text_is_a_single_chunk(self):
        page = make_page("the quick brown fox")
        chunks = chunk_page(page)

        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0].text, "the quick brown fox")
        self.assertEqual(chunks[0].chunk_index, 0)

    def test_text_exactly_chunk_size_is_a_single_chunk(self):
        page = make_page(" ".join(numbered_words(4)))
        chunks = chunk_page(page, chunk_size=4, overlap=1)

        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0].text, "w0 w1 w2 w3")

    def test_long_text_splits_into_expected_chunks(self):
        page = make_page(" ".join(numbered_words(10)))
        chunks = chunk_page(page, chunk_size=4, overlap=1)

        self.assertEqual(len(chunks), 3)
        self.assertEqual(chunks[0].text, "w0 w1 w2 w3")
        self.assertEqual(chunks[1].text, "w3 w4 w5 w6")
        self.assertEqual(chunks[2].text, "w6 w7 w8 w9")

    def test_consecutive_chunks_actually_overlap(self):
        page = make_page(" ".join(numbered_words(10)))
        chunks = chunk_page(page, chunk_size=4, overlap=1)

        for previous, current in zip(chunks, chunks[1:]):
            self.assertEqual(previous.text.split()[-1], current.text.split()[0])

    def test_trailing_chunk_is_not_a_pure_duplicate(self):
        page = make_page(" ".join(numbered_words(8)))
        chunks = chunk_page(page, chunk_size=4, overlap=1)

        self.assertEqual(len(chunks), 2)
        self.assertNotEqual(chunks[0].text, chunks[1].text)

    def test_chunk_indices_are_sequential(self):
        page = make_page(" ".join(numbered_words(10)))
        chunks = chunk_page(page, chunk_size=4, overlap=1)

        self.assertEqual([c.chunk_index for c in chunks], [0, 1, 2])

    def test_no_words_are_lost(self):
        words = numbered_words(37)
        page = make_page(" ".join(words))
        chunks = chunk_page(page, chunk_size=5, overlap=2)

        seen = {word for chunk in chunks for word in chunk.text.split()}
        self.assertEqual(seen, set(words))

    def test_metadata_is_carried_onto_every_chunk(self):
        page = make_page(
            " ".join(numbered_words(10)), document="notes.pdf", page_number=7
        )
        chunks = chunk_page(page, chunk_size=4, overlap=1)

        self.assertTrue(chunks)
        for chunk in chunks:
            self.assertEqual(chunk.document, "notes.pdf")
            self.assertEqual(chunk.page_number, 7)

    def test_citation_format(self):
        chunk = Chunk(
            document="past_paper.pdf", page_number=12, chunk_index=0, text="x"
        )

        self.assertEqual(chunk.citation(), "past_paper.pdf p.12")

    def test_zero_chunk_size_is_rejected(self):
        with self.assertRaises(ValueError):
            chunk_page(make_page("some text"), chunk_size=0, overlap=0)

    def test_negative_chunk_size_is_rejected(self):
        with self.assertRaises(ValueError):
            chunk_page(make_page("some text"), chunk_size=-5, overlap=0)

    def test_negative_overlap_is_rejected(self):
        with self.assertRaises(ValueError):
            chunk_page(make_page("some text"), chunk_size=5, overlap=-1)

    def test_overlap_equal_to_chunk_size_is_rejected(self):
        with self.assertRaises(ValueError):
            chunk_page(make_page("some text"), chunk_size=5, overlap=5)

    def test_overlap_larger_than_chunk_size_is_rejected(self):
        with self.assertRaises(ValueError):
            chunk_page(make_page("some text"), chunk_size=5, overlap=9)


class ChunkPagesTests(unittest.TestCase):
    def test_pages_are_chunked_in_order(self):
        pages = [
            make_page("alpha beta gamma", document="notes.pdf", page_number=1),
            make_page("delta epsilon zeta", document="notes.pdf", page_number=2),
        ]
        chunks = chunk_pages(pages)

        self.assertEqual([c.page_number for c in chunks], [1, 2])
        self.assertEqual(chunks[0].text, "alpha beta gamma")
        self.assertEqual(chunks[1].text, "delta epsilon zeta")

    def test_chunk_index_restarts_on_each_page(self):
        pages = [
            make_page(" ".join(numbered_words(10)), page_number=1),
            make_page(" ".join(numbered_words(10)), page_number=2),
        ]
        chunks = chunk_pages(pages, chunk_size=4, overlap=1)

        indices_by_page = {
            page_number: [
                c.chunk_index for c in chunks if c.page_number == page_number
            ]
            for page_number in (1, 2)
        }
        self.assertEqual(indices_by_page[1], [0, 1, 2])
        self.assertEqual(indices_by_page[2], [0, 1, 2])

    def test_empty_page_in_the_middle_is_skipped(self):
        pages = [
            make_page("alpha beta", page_number=1),
            make_page("", page_number=2),
            make_page("gamma delta", page_number=3),
        ]
        chunks = chunk_pages(pages)

        self.assertEqual([c.page_number for c in chunks], [1, 3])

    def test_no_pages_produces_no_chunks(self):
        self.assertEqual(chunk_pages([]), [])

    def test_invalid_arguments_are_rejected_without_pages(self):
        with self.assertRaises(ValueError):
            chunk_pages([], chunk_size=0, overlap=0)


if __name__ == "__main__":
    unittest.main()
