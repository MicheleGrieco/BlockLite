"""
Utility functions for the blockchain.
"""

import hashlib
import json
from typing import Any


def canonical_json(data: Any) -> str:
    """
    Serialize data to a canonical JSON string.

    Keys are sorted and separators are compact, so logically equal
    structures always produce the same string (and therefore the same hash).
    """
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def hash_data(data: str | dict | list) -> str:
    """
    Generate a SHA-256 hash of the input data.

    Args:
        data: A string, dictionary or list to hash. Dictionaries and lists
              are serialized to canonical JSON for consistent hashing.

    Returns:
        The hexadecimal SHA-256 hash string.

    Raises:
        TypeError: If data is not a str, dict or list.
    """
    if isinstance(data, (dict, list)):
        data = canonical_json(data)
    elif not isinstance(data, str):
        raise TypeError(f"Cannot hash object of type {type(data).__name__}")

    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def meets_difficulty(block_hash: str, difficulty: int) -> bool:
    """
    Check whether a hash satisfies the proof-of-work target.

    The target is expressed as the number of leading hexadecimal zeros:
    difficulty 0 accepts any hash, difficulty 4 requires "0000...".
    """
    return block_hash.startswith("0" * difficulty)
