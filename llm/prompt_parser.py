"""Prompt parsing entry points."""


def parse_prompt(prompt: str) -> dict:
    """Extract structured information from a natural-language architecture prompt."""
    return {"raw_prompt": prompt.strip()}
