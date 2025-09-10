import hashlib
import json
import sys


def hash_me(msg=""):
    """
    Helper function to hash a message using SHA-256 algorithm.
    The message can be a string or a dictionary.
    If it's a dictionary, it will be converted to a JSON string with sorted keys to ensure consistent hashing.

    Args:
        msg (str, optional): Defaults to "".

    Returns:
        str: The SHA-256 hash of the message.
    """
    if not isinstance(msg, str):
        # Sorting keys to guarantee consistent hashing for dicts
        msg = json.dumps(msg, sort_keys=True)
    
    # Always encode the message to bytes
    msg_bytes = msg.encode('utf-8')
    return hashlib.sha256(msg_bytes).hexdigest()