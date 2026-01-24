def groundedness_score(sources, expected_sources):
    if not sources:
        return 0.0

    matched = 0
    for src in sources:
        source_file = src.get("source_file", "")
        if any(exp in source_file for exp in expected_sources):
            matched += 1

    return matched / len(expected_sources)


def citation_coverage(sources):
    if not sources:
        return 0.0

    cited = [s for s in sources if s.get("page") is not None]
    return len(cited) / len(sources)


def hallucination_flag(sources):
    return len(sources) == 0
