"""Command parser helpers."""

from __future__ import annotations

from collections.abc import Mapping


def dictmerge[T](*libs: Mapping[T, list[str]]) -> dict[T, list[str]]:
    """Merge parser dictionaries in legacy order."""
    merged: dict[T, list[str]] = {}

    for lib in libs:
        merged.update(lib)

    return merged


def parse_command[T](raw_input: object, dictionary: Mapping[T, list[str]]) -> list[T]:
    """Parse command text using Mud's broad legacy token matching."""
    text = str(raw_input).lower()
    nodigits = "".join(i for i in text if not i.isdigit())
    sentence = nodigits.split()
    output: list[T] = []

    for key in list(dictionary.keys()):
        if set(sentence).isdisjoint(set(dictionary[key])) is False:
            output.append(key)

    return output


parser = parse_command
