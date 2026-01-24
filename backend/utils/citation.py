def format_apa(source: dict) -> str:
    """
    APA 7th basic format
    """
    author = "Unknown"
    year = "n.d."
    title = source.get("source_file", "Unknown document")
    page = source.get("page")

    page_part = f" (p. {page})" if page is not None else ""

    return f"{author} ({year}). {title}{page_part}."


def format_ieee(source: dict, index: int) -> str:
    """
    IEEE basic format
    """
    title = source.get("source_file", "Unknown document")
    page = source.get("page")

    page_part = f", p. {page}" if page is not None else ""

    return f"[{index}] {title}{page_part}."
