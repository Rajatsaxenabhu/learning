from dataclasses import dataclass

from bs4 import BeautifulSoup


@dataclass(slots=True)
class ContentValidationResult:

    valid: bool

    reason: str

    text_length: int

    title_present: bool

    challenge_detected: bool

    boilerplate_detected: bool


class ContentValidator:

    MIN_TEXT_LENGTH = 200

    CHALLENGE_PATTERNS = (
        "enable javascript",
        "enable javascript to continue",
        "checking your browser",
        "checking your browser before accessing",
        "verify you are human",
        "verify you are a human",
        "captcha",
        "access denied",
        "temporarily blocked",
        "unusual traffic",
        "security check",
        "just a moment",
        "cloudflare",
    )

    def validate(
        self,
        content: bytes,
        content_type: str | None,
    ) -> ContentValidationResult:

        if not content:

            return ContentValidationResult(
                valid=False,
                reason="empty_content",
                text_length=0,
                title_present=False,
                challenge_detected=False,
                boilerplate_detected=False,
            )

        if not content_type:

            return ContentValidationResult(
                valid=False,
                reason="missing_content_type",
                text_length=0,
                title_present=False,
                challenge_detected=False,
                boilerplate_detected=False,
            )

        content_type = content_type.lower()

        if (
            "text/html" not in content_type
            and
            "application/xhtml+xml"
            not in content_type
        ):

            return ContentValidationResult(
                valid=False,
                reason="unsupported_content_type",
                text_length=0,
                title_present=False,
                challenge_detected=False,
                boilerplate_detected=False,
            )

        try:

            soup = BeautifulSoup(
                content,
                "html.parser",
            )

        except Exception:

            return ContentValidationResult(
                valid=False,
                reason="html_parse_failed",
                text_length=0,
                title_present=False,
                challenge_detected=False,
                boilerplate_detected=False,
            )

        title_present = bool(
            soup.title
            and soup.title.get_text(
                strip=True
            )
        )

        for tag in soup(
            [
                "script",
                "style",
                "noscript",
                "svg",
            ]
        ):
            tag.decompose()

        text = soup.get_text(
            separator=" ",
            strip=True,
        )

        text = " ".join(
            text.split()
        )

        text_length = len(text)

        normalized_text = text.lower()

        challenge_detected = any(
            pattern in normalized_text
            for pattern in self.CHALLENGE_PATTERNS
        )

        if challenge_detected:

            return ContentValidationResult(
                valid=False,
                reason="challenge_page",
                text_length=text_length,
                title_present=title_present,
                challenge_detected=True,
                boilerplate_detected=False,
            )

        if text_length < self.MIN_TEXT_LENGTH:

            return ContentValidationResult(
                valid=False,
                reason="content_too_short",
                text_length=text_length,
                title_present=title_present,
                challenge_detected=False,
                boilerplate_detected=False,
            )

        boilerplate_detected = (
            self._is_boilerplate(
                soup=soup,
                text_length=text_length,
            )
        )

        if boilerplate_detected:

            return ContentValidationResult(
                valid=False,
                reason="boilerplate_content",
                text_length=text_length,
                title_present=title_present,
                challenge_detected=False,
                boilerplate_detected=True,
            )

        return ContentValidationResult(
            valid=True,
            reason="valid_content",
            text_length=text_length,
            title_present=title_present,
            challenge_detected=False,
            boilerplate_detected=False,
        )

    def _is_boilerplate(
        self,
        soup: BeautifulSoup,
        text_length: int,
    ) -> bool:

        body = soup.body

        if body is None:
            return True

        body_text = body.get_text(
            separator=" ",
            strip=True,
        )

        body_text = " ".join(
            body_text.split()
        )

        if not body_text:
            return True

        meaningful_tags = soup.find_all(
            [
                "article",
                "main",
                "section",
                "p",
                "h1",
                "h2",
                "h3",
            ]
        )

        meaningful_text = " ".join(
            tag.get_text(
                separator=" ",
                strip=True,
            )
            for tag in meaningful_tags
        )

        meaningful_text = " ".join(
            meaningful_text.split()
        )

        if not meaningful_text:
            return True

        meaningful_ratio = (
            len(meaningful_text)
            / max(text_length, 1)
        )

        return meaningful_ratio < 0.05