import hashlib
import json
import sys

"""
hashMe(msg="")
    Hashes a message using SHA-256 algorithm.
    The message can be a string or a dictionary.
    If it's a dictionary, it will be converted to a JSON string with sorted keys to ensure consistent hashing.
"""
def hashMe(msg=""):
    if type(msg) != str:
        # Sorting keys to guarantee consistent hashing for dicts
        msg = json.dumps(msg, sort_keys=True)
    
    # Python 2 and 3 compatibility
    # In Python 2, str is a byte string, so we can hash it directly
    # In Python 3, str is a unicode string, so we need to encode it to bytes first
    # Note: In Python 3, str is unicode, and bytes is a separate type
    if sys.version_info.major == 2:
        return hashlib.sha256(msg).hexdigest()
    else:
        return hashlib.sha256(str(msg).encode('utf-8')).hexdigest()