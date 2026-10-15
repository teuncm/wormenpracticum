"""Parse compact, one-based integer selections used by analysis views."""

import re
from collections.abc import Iterable

_SELECTION_ITEM = re.compile(r"^(\d+)(?:\s*-\s*(\d+))?$")


def parse_display_selection(
    text: str, available: Iterable[int], *, strict: bool = True
) -> list[int]:
    """Return sorted selected IDs, validating against available IDs when strict.

    Ranges are intersected with the available IDs rather than expanded, so even
    a large range cannot allocate an unbounded list. In strict mode a range may
    end at the largest available ID and individual values must exist.
    """
    ids = sorted(set(available))
    if not text.strip():
        return ids

    available_set = set(ids)
    maximum = ids[-1] if ids else 0
    selected = set()
    for raw_item in text.split(","):
        item = raw_item.strip()
        match = _SELECTION_ITEM.fullmatch(item)
        if match is None:
            raise ValueError(f"Invalid selection item: {item or '(empty)'}")
        first = int(match.group(1))
        last = int(match.group(2) or first)
        if first < 1 or last < 1:
            raise ValueError("Use positive integers only.")
        if last < first:
            raise ValueError(f"Range must ascend: {item}")
        if strict and last > maximum:
            raise ValueError(
                f"Selection ends at {last}; available IDs end at {maximum}."
            )
        if strict and match.group(2) is None and first not in available_set:
            raise ValueError(f"ID {first} is not available.")
        selected.update(value for value in ids if first <= value <= last)
    return sorted(selected)
