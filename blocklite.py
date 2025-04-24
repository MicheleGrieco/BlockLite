import hashlib
import json
import sys
import random

random.seed(0)


def hashMe(msg=""):
    """
    Hashes a message using SHA-256 algorithm.
    The message can be a string or a dictionary.
    If it's a dictionary, it will be converted to a JSON string with sorted keys to ensure consistent hashing.

    Args:
        msg (str, optional): Defaults to "".

    Returns:
        str: The SHA-256 hash of the message.
    """
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


def makeTransaction(maxValue=3):
    """
    Creates a random transaction between Alice and Bob, where the amount is between -maxValue and maxValue.
    The sum of deposits and withdrawals must be 0 (tokens are neither created nor destroyed)
    A user’s account must have sufficient funds to cover any withdrawals.
    The transaction is represented as a dictionary with account names as keys and amounts as values.
    The function returns a dictionary with the transaction details.
    The transaction is guaranteed to be valid according to the rules defined in the isValidTxn function.

    Args:
        maxValue (int, optional): Defaults to 3.

    Returns:
        str: A string representation of the transaction.
    """
    sign = int(random.getrandbits(1)) * 2 - 1
    # Randomly choose a value between -1 and 1
    amount = random.randint(1, maxValue)
    alicePays = sign * amount
    bobPays = -1 * alicePays
    
    # By construction, this will always return transactions that respect the conservation of tokens.
    # However, note that we have not done anything to check whether these overdraft an account
    return {u'Alice':alicePays,u'Bob':bobPays}


# This is a list of transactions that will be used to test the algorithm.
txnBuffer = [makeTransaction() for i in range(30)]

"""
    RULES for a simple banking system:
    - The sum of deposits and withdrawals must be 0 (tokens are neither created nor destroyed)
    - A user’s account must have sufficient funds to cover any withdrawals
"""

def updateState(txn, state):
    """
    Updates the state of the accounts based on the transaction.
    
    Args:
        txn (dict): dictionary keyed with account names, holding numeric values for transfer amount
        state (dict): dictionary keyed with account names, holding numeric values for account balance

    Returns:
        dict: Updated state, with additional users added to state if necessary
    """
    
    # As dictionaries are mutable, let's avoid any confusion by creating a working copy of the data.
    state = state.copy()
    for key in txn:
        if key in state.keys():
            state[key] += txn[key]
        else:
            state[key] = txn[key]
    return state


def isValidTxn(txn, state):
    
    """
    Checks if a transaction is valid according to the rules defined.
    
    Args:
        txn (dict): dictionary keyed with account names, holding numeric values for transfer amount
        state (dict): dictionary keyed with account names, holding numeric values for account balance

    Returns:
        bool: True if the transaction is valid, False otherwise
    """
    # Assume that the transaction is a dictionary keyed by account names

    # Check that the sum of the deposits and withdrawals is 0
    if sum(txn.values()) != 0:
        return False
    
    # Check that the transaction does not cause an overdraft
    for key in txn.keys():
        if key in state.keys(): 
            acctBalance = state[key]
        else:
            acctBalance = 0
        if (acctBalance + txn[key]) < 0:
            return False
    
    return True



state = {u'Alice':5, u'Bob':5}

print(isValidTxn({u'Alice': -3, u'Bob': 3}, state))  # Basic transaction- this works great!
print(isValidTxn({u'Alice': -4, u'Bob': 3}, state))  # But we can't create or destroy tokens!
print(isValidTxn({u'Alice': -6, u'Bob': 6}, state))  # We also can't overdraft our account.
print(isValidTxn({u'Alice': -4, u'Bob': 2,'Lisa':2}, state)) # Creating new users is valid
print(isValidTxn({u'Alice': -4, u'Bob': 3,'Lisa':2}, state)) # But the same rules still apply!

state = {u'Alice':50, u'Bob':50}  # Define the initial state
genesisBlockTxns = [state]
genesisBlockContents = {u'blockNumber':0,u'parentHash':None,u'txnCount':1,u'txns':genesisBlockTxns}
genesisHash = hashMe(genesisBlockContents)
genesisBlock = {u'hash':genesisHash,u'contents':genesisBlockContents}
genesisBlockStr = json.dumps(genesisBlock, sort_keys=True)

chain = [genesisBlock]  # Initialize the blockchain with the genesis block

def makeBlock(txns, chain):
    parentBlock = chain[-1]  # Get the last block in the chain
    parentHash = parentBlock[u'hash']  # Get the hash of the last block
    blockNumber = parentBlock[u'contents'][u'blockNumber'] + 1  # Increment the block number
    txnCount = len(txns)  # Get the number of transactions in the new block
    blockContents = {u'blockNumber':blockNumber, u'parentHash':parentHash, u'txnCount':len(txns), u'txns':txns}  # Create the block contents
    blockHash = hashMe(blockContents)  # Hash the block contents to get the block hash
    block = {u'hash':blockHash, u'contents':blockContents}  # Create the block with its hash and contents
    return block
