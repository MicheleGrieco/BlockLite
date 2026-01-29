"""
Utility functions for the blockchain.
"""

import hashlib
import json


def hash_data(data: str | dict) -> str:
    """
    Generate a SHA-256 hash of the input data.
    Args:
        data: A string or dictionary to hash. Dictionaries are serialized
                to JSON with sorted keys for consistent hashing.

    Returns:
        The hexadecimal SHA-256 hash string.
    """
    if isinstance(data, dict):
        # Sorting keys to guarantee consistent hashing for dicts
        data = json.dumps(data, sort_keys=True)
    
    # Always encode the message to bytes
    return hashlib.sha256(data.encode('utf-8')).hexdigest()