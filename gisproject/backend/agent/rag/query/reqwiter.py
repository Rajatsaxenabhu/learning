import re

from langchain_core.messages import HumanMessage
from spellchecker import SpellChecker

from app.conf.logging.agentlog import logger


class SpellingCorrector:

    def __init__(self, extra_terms=None):
        self.spell = SpellChecker()

        if extra_terms:
            self.spell.word_frequency.load_words(extra_terms)

    def correct(self, query: str) -> str:
        tokens = re.findall(r"\S+|\s+", query)
        corrected_tokens = []

        for token in tokens:

            if token.isspace():
                corrected_tokens.append(token)
                continue

            match = re.match(r"^([^\w]*)([\w]+)([^\w]*)$", token)

            if not match:
                corrected_tokens.append(token)
                continue

            prefix, word, suffix = match.groups()

            if word.isdigit():
                corrected_tokens.append(token)
                continue

            if word.isupper():
                corrected_tokens.append(token)
                continue

            if any(c.isdigit() for c in word):
                corrected_tokens.append(token)
                continue

            if any(char in word for char in [":", "_", "-"]):
                corrected_tokens.append(token)
                continue

            lower_word = word.lower()

            if lower_word in self.spell:
                corrected_tokens.append(token)
                continue

            correction = self.spell.correction(lower_word)

            if not correction:
                corrected_tokens.append(token)
                continue

            if correction == lower_word:
                corrected_tokens.append(token)
                continue

            if word[0].isupper():
                correction = correction.capitalize()

            corrected_tokens.append(
                f"{prefix}{correction}{suffix}"
            )

        return "".join(corrected_tokens)


class QueryRewriter:

    def __init__(self, llm):
        self.llm = llm
        self.spelling_corrector = SpellingCorrector()

    async def rewrite(self, query: str) -> str:
        logger.info("Query before spelling correction: %s", query)
        query = self.spelling_corrector.correct(query)
        logger.info("Query after spelling correction: %s", query)

        prompt = f"""Rewrite the user's query into a concise, information-rich web search query.

        Rules:
        - Preserve intent and technical terms (software, libraries, acronyms, datasets, CRS codes, identifiers, proper nouns).
        - Fix grammar and remove conversational filler.
        - Add context only if clearly implied; never invent facts.
        - Do not answer the question.
        - Return ONLY the search query.

        User query: {query}

        Search query:"""

        response = await self.llm.ainvoke(
            [
                HumanMessage(content=prompt)
            ]
        )

        return response.content.strip()
