"""
    RULES for a simple banking system:
    - The sum of deposits and withdrawals must be 0 (tokens are neither created nor destroyed)
    - A user’s account must have sufficient funds to cover any withdrawals
"""
import json
import hashcode as hashMe

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