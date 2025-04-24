import hashlib
import json
import sys

def hashMe(msg=""):
    # Helper function that wraps the hashing algorithm
    if type(msg) != str:
        msg = json.dumps(msg, sort_keys=True)
        # Sorting keys to guarantee consistent hashing for dicts
    
    if sys.version_info.major == 2:
        return hashlib.sha256(msg).hexdigest()
    else:
        return hashlib.sha256(str(msg).encode('utf-8')).hexdigest()